from rest_framework import serializers
from authentication.models import User
from .models import EmployeeProfile, PayrollRecord


class StaffAuthRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField(
        help_text="Employee email or username."
    )
    password = serializers.CharField(write_only=True)
    system = serializers.ChoiceField(
        choices=["pos", "ordering", "general"],
        required=False,
        default="general",
        help_text="Target ERP module requesting login (pos, ordering, or general).",
    )


class StaffDirectorySerializer(serializers.ModelSerializer):
    employee_code = serializers.SerializerMethodField()
    department = serializers.CharField(source="department.name", default=None)
    role = serializers.CharField(source="role.name", default=None)
    job_title = serializers.CharField(source="hr_profile.job_title", default=None)
    employment_type = serializers.CharField(
        source="hr_profile.employment_type", default=None
    )
    employment_status = serializers.CharField(
        source="hr_profile.employment_status", default="active"
    )
    can_access_pos = serializers.BooleanField(
        source="hr_profile.can_access_pos", default=False
    )
    can_access_ordering = serializers.BooleanField(
        source="hr_profile.can_access_ordering", default=False
    )

    class Meta:
        model = User
        fields = [
            "id",
            "employee_code",
            "username",
            "full_name",
            "email",
            "phone",
            "department",
            "role",
            "job_title",
            "employment_type",
            "employment_status",
            "can_access_pos",
            "can_access_ordering",
            "is_active",
        ]

    def get_employee_code(self, obj):
        profile = getattr(obj, "hr_profile", None)
        if profile and profile.employee_code:
            return profile.employee_code
        return obj.employee_id


class PayrollExpenseSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.get_full_name", read_only=True)
    employee_email = serializers.EmailField(source="employee.email", read_only=True)

    class Meta:
        model = PayrollRecord
        fields = [
            "id",
            "employee",
            "employee_name",
            "employee_email",
            "period_start",
            "period_end",
            "basic_pay",
            "allowances",
            "deductions",
            "net_pay",
            "status",
            "paid_at",
        ]
