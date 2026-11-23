from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from assets.models import Asset, MaintenanceRecord
from authentication.models import User
from .models import PayrollRecord
from .serializers import (
    PayrollExpenseSerializer,
    StaffAuthRequestSerializer,
    StaffDirectorySerializer,
)


class StaffAuthAPI(APIView):
    """
    Authenticate staff for external ERP modules (Kate's POS, Alejandro's Ordering).
    Returns JWT tokens plus employee HR profile and module access flags.
    """

    permission_classes = [AllowAny]
    serializer_class = StaffAuthRequestSerializer

    def post(self, request):
        serializer = StaffAuthRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data["identifier"].strip()
        password = serializer.validated_data["password"]
        target_system = serializer.validated_data.get("system", "general")

        user = (
            User.objects.select_related("hr_profile", "department", "role")
            .filter(Q(email__iexact=identifier) | Q(username__iexact=identifier))
            .filter(is_deleted=False)
            .first()
        )
        if not user or not user.check_password(password):
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"detail": "Staff account is inactive."},
                status=status.HTTP_403_FORBIDDEN,
            )

        profile = getattr(user, "hr_profile", None)
        if profile and profile.employment_status in ("resigned", "terminated"):
            return Response(
                {"detail": f"Employment status is {profile.employment_status}."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if target_system == "pos" and not (profile and profile.can_access_pos):
            return Response(
                {"detail": "Staff is not authorized for POS access."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if target_system == "ordering" and not (profile and profile.can_access_ordering):
            return Response(
                {"detail": "Staff is not authorized for Ordering access."},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)
        staff_data = StaffDirectorySerializer(user).data
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "staff": staff_data,
            },
            status=status.HTTP_200_OK,
        )


class StaffDirectoryAPI(APIView):
    """
    List active staff/employees for POS, Ordering, and ERP synchronization.
    Supports ?system=pos|ordering and ?search=...
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = (
            User.objects.select_related("hr_profile", "department", "role")
            .filter(is_deleted=False, is_active=True)
            .order_by("full_name")
        )
        if request.user.organization:
            qs = qs.filter(organization=request.user.organization)

        system = request.query_params.get("system", "").strip().lower()
        if system == "pos":
            qs = qs.filter(hr_profile__can_access_pos=True)
        elif system == "ordering":
            qs = qs.filter(hr_profile__can_access_ordering=True)

        search = request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(full_name__icontains=search)
                | Q(email__icontains=search)
                | Q(employee_id__icontains=search)
                | Q(hr_profile__employee_code__icontains=search)
            )

        serializer = StaffDirectorySerializer(qs, many=True)
        return Response({"count": qs.count(), "results": serializer.data})


class EquipmentExpenseListAPI(APIView):
    """
    Expose Asseto equipment purchases and maintenance costs for Judy's Expenses module.
    Supports ?type=purchase|maintenance, ?start_date=YYYY-MM-DD, ?end_date=YYYY-MM-DD.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        expense_type = request.query_params.get("type", "").strip().lower()
        start_date = request.query_params.get("start_date", "").strip()
        end_date = request.query_params.get("end_date", "").strip()
        org = getattr(request.user, "organization", None)

        items = []

        if expense_type in ("", "purchase"):
            assets_qs = Asset.objects.select_related("vendor", "product").filter(
                is_deleted=False, price__isnull=False, price__gt=0
            )
            if org:
                assets_qs = assets_qs.filter(organization=org)
            if start_date:
                assets_qs = assets_qs.filter(purchase_date__gte=start_date)
            if end_date:
                assets_qs = assets_qs.filter(purchase_date__lte=end_date)

            for asset in assets_qs:
                items.append(
                    {
                        "source_id": str(asset.id),
                        "expense_type": "purchase",
                        "title": asset.name or (asset.product.name if asset.product else "Equipment Purchase"),
                        "asset_tag": asset.tag,
                        "vendor": asset.vendor.name if asset.vendor else None,
                        "amount": float(asset.price or 0),
                        "date": asset.purchase_date.isoformat() if asset.purchase_date else None,
                        "status": asset.get_status(),
                    }
                )

        if expense_type in ("", "maintenance"):
            maint_qs = MaintenanceRecord.objects.select_related("asset", "asset__vendor").all()
            if org:
                maint_qs = maint_qs.filter(organization=org)
            if start_date:
                maint_qs = maint_qs.filter(date__gte=start_date)
            if end_date:
                maint_qs = maint_qs.filter(date__lte=end_date)

            for rec in maint_qs:
                items.append(
                    {
                        "source_id": str(rec.id),
                        "expense_type": "maintenance",
                        "title": f"{rec.maintenance_type} ({rec.service_id})",
                        "asset_tag": rec.asset.tag if rec.asset else None,
                        "vendor": rec.technician,
                        "amount": float(rec.cost or 0),
                        "date": rec.date.isoformat() if rec.date else None,
                        "status": rec.status,
                    }
                )

        items.sort(key=lambda x: x["date"] or "", reverse=True)
        total_amount = round(sum(i["amount"] for i in items), 2)
        return Response(
            {
                "count": len(items),
                "total_amount": total_amount,
                "results": items,
            }
        )


class PayrollExpenseListAPI(APIView):
    """Expose approved/paid payroll records for Judy's Expenses module."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = PayrollRecord.objects.select_related("employee").filter(
            status__in=["approved", "paid"]
        )
        if request.user.organization:
            qs = qs.filter(organization=request.user.organization)

        start_date = request.query_params.get("start_date", "").strip()
        end_date = request.query_params.get("end_date", "").strip()
        if start_date:
            qs = qs.filter(period_start__gte=start_date)
        if end_date:
            qs = qs.filter(period_end__lte=end_date)

        serializer = PayrollExpenseSerializer(qs, many=True)
        total_amount = round(sum(float(r["net_pay"]) for r in serializer.data), 2)
        return Response(
            {
                "count": qs.count(),
                "total_amount": total_amount,
                "results": serializer.data,
            }
        )
