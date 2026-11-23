from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from assets.models import AssignAsset
from .forms import (
    AttendanceForm,
    EmployeeProfileForm,
    LeaveRequestForm,
    PayrollRecordForm,
)
from .models import Attendance, EmployeeProfile, LeaveRequest, PayrollRecord


def _org_filter(request, queryset):
    """Scope queryset to the current user's organization when present."""
    org = getattr(request.user, "organization", None)
    if org is not None:
        return queryset.filter(organization=org)
    return queryset


def _can_manage_hr(user):
    return (
        user.is_superuser
        or user.is_staff
        or user.has_perm("hr.view_employeeprofile")
        or user.has_perm("authentication.view_users")
    )


@login_required
def employee_list(request):
    """List HR employee profiles with search and ERP access overview."""
    qs = _org_filter(
        request,
        EmployeeProfile.objects.select_related("user", "user__department", "user__role")
        .filter(is_deleted=False),
    )
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()
    if query:
        qs = qs.filter(
            Q(employee_code__icontains=query)
            | Q(job_title__icontains=query)
            | Q(user__full_name__icontains=query)
            | Q(user__email__icontains=query)
        )
    if status_filter:
        qs = qs.filter(employment_status=status_filter)

    paginator = Paginator(qs, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "sidebar": "hr",
        "submenu": "hr_employees",
        "page_obj": page_obj,
        "query": query,
        "status_filter": status_filter,
        "total_employees": qs.count(),
        "active_count": qs.filter(employment_status="active").count(),
        "pos_enabled_count": qs.filter(can_access_pos=True).count(),
        "ordering_enabled_count": qs.filter(can_access_ordering=True).count(),
        "can_manage_hr": _can_manage_hr(request.user),
    }
    return render(request, "hr/employee_list.html", context)


@login_required
def employee_add(request):
    """Create an HR profile for an existing user."""
    org = getattr(request.user, "organization", None)
    form = EmployeeProfileForm(request.POST or None, organization=org)
    if request.method == "POST" and form.is_valid():
        profile = form.save(commit=False)
        profile.organization = org or profile.user.organization
        if profile.employee_code and not profile.user.employee_id:
            profile.user.employee_id = profile.employee_code
            profile.user.save(update_fields=["employee_id"])
        profile.save()
        messages.success(request, "Employee HR profile created successfully.")
        return redirect("hr:employee_list")
    return render(
        request,
        "hr/form.html",
        {
            "sidebar": "hr",
            "submenu": "hr_employees",
            "form": form,
            "title": "Add Employee HR Profile",
            "back_url": "hr:employee_list",
        },
    )


@login_required
def employee_edit(request, pk):
    """Update an existing HR employee profile."""
    profile = get_object_or_404(_org_filter(request, EmployeeProfile.objects.all()), pk=pk)
    org = getattr(request.user, "organization", None)
    form = EmployeeProfileForm(request.POST or None, instance=profile, organization=org)
    if request.method == "POST" and form.is_valid():
        updated = form.save()
        if updated.employee_code and updated.user.employee_id != updated.employee_code:
            updated.user.employee_id = updated.employee_code
            updated.user.save(update_fields=["employee_id"])
        messages.success(request, "Employee HR profile updated.")
        return redirect("hr:employee_detail", pk=profile.pk)
    return render(
        request,
        "hr/form.html",
        {
            "sidebar": "hr",
            "submenu": "hr_employees",
            "form": form,
            "title": f"Edit HR Profile — {profile.user.get_full_name()}",
            "back_url": "hr:employee_list",
        },
    )


@login_required
def employee_detail(request, pk):
    """View employee HR details, assigned company equipment, attendance, and leaves."""
    profile = get_object_or_404(
        _org_filter(
            request,
            EmployeeProfile.objects.select_related("user", "user__department", "user__role"),
        ),
        pk=pk,
    )
    assigned_assets = AssignAsset.objects.select_related("asset", "asset__product").filter(
        user=profile.user
    )[:10]
    recent_attendance = Attendance.objects.filter(employee=profile.user)[:10]
    recent_leaves = LeaveRequest.objects.filter(employee=profile.user)[:10]
    recent_payrolls = PayrollRecord.objects.filter(employee=profile.user)[:10]

    return render(
        request,
        "hr/employee_detail.html",
        {
            "sidebar": "hr",
            "submenu": "hr_employees",
            "profile": profile,
            "assigned_assets": assigned_assets,
            "recent_attendance": recent_attendance,
            "recent_leaves": recent_leaves,
            "recent_payrolls": recent_payrolls,
        },
    )


@login_required
def attendance_list(request):
    """List attendance records and provide quick clock-in / clock-out for the current user."""
    qs = _org_filter(request, Attendance.objects.select_related("employee"))
    date_filter = request.GET.get("date", "").strip()
    if date_filter:
        qs = qs.filter(date=date_filter)

    today = timezone.localdate()
    today_record = Attendance.objects.filter(employee=request.user, date=today).first()

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "hr/attendance_list.html",
        {
            "sidebar": "hr",
            "submenu": "hr_attendance",
            "page_obj": page_obj,
            "date_filter": date_filter,
            "today_record": today_record,
        },
    )


@login_required
def attendance_clock_in(request):
    """Record time-in for the currently logged-in employee."""
    if request.method == "POST":
        today = timezone.localdate()
        now_time = timezone.localtime().time().replace(microsecond=0)
        record, created = Attendance.objects.get_or_create(
            employee=request.user,
            date=today,
            defaults={
                "time_in": now_time,
                "status": "present",
                "organization": getattr(request.user, "organization", None),
            },
        )
        if not created and not record.time_in:
            record.time_in = now_time
            record.save(update_fields=["time_in"])
        messages.success(request, f"Clocked in at {record.time_in}.")
    return redirect("hr:attendance_list")


@login_required
def attendance_clock_out(request):
    """Record time-out for the currently logged-in employee."""
    if request.method == "POST":
        today = timezone.localdate()
        now_time = timezone.localtime().time().replace(microsecond=0)
        record = Attendance.objects.filter(employee=request.user, date=today).first()
        if record:
            record.time_out = now_time
            record.save(update_fields=["time_out"])
            messages.success(request, f"Clocked out at {record.time_out}.")
        else:
            messages.warning(request, "You need to clock in first before clocking out.")
    return redirect("hr:attendance_list")


@login_required
def attendance_add(request):
    """Manually log an attendance entry."""
    org = getattr(request.user, "organization", None)
    form = AttendanceForm(request.POST or None, organization=org)
    if request.method == "POST" and form.is_valid():
        att = form.save(commit=False)
        att.organization = org or att.employee.organization
        att.save()
        messages.success(request, "Attendance record saved.")
        return redirect("hr:attendance_list")
    return render(
        request,
        "hr/form.html",
        {
            "sidebar": "hr",
            "submenu": "hr_attendance",
            "form": form,
            "title": "Log Attendance",
            "back_url": "hr:attendance_list",
        },
    )


@login_required
def leave_list(request):
    """List leave requests with approve/reject actions."""
    qs = _org_filter(request, LeaveRequest.objects.select_related("employee", "approved_by"))
    status_filter = request.GET.get("status", "").strip()
    if status_filter:
        qs = qs.filter(status=status_filter)

    paginator = Paginator(qs, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "hr/leave_list.html",
        {
            "sidebar": "hr",
            "submenu": "hr_leaves",
            "page_obj": page_obj,
            "status_filter": status_filter,
            "pending_count": qs.filter(status="pending").count(),
            "can_manage_hr": _can_manage_hr(request.user),
        },
    )


@login_required
def leave_add(request):
    """Submit a new leave request."""
    org = getattr(request.user, "organization", None)
    form = LeaveRequestForm(
        request.POST or None,
        initial={"employee": request.user},
        organization=org,
    )
    if request.method == "POST" and form.is_valid():
        leave = form.save(commit=False)
        leave.organization = org or leave.employee.organization
        leave.save()
        messages.success(request, "Leave request submitted.")
        return redirect("hr:leave_list")
    return render(
        request,
        "hr/form.html",
        {
            "sidebar": "hr",
            "submenu": "hr_leaves",
            "form": form,
            "title": "Submit Leave Request",
            "back_url": "hr:leave_list",
        },
    )


@login_required
def leave_update_status(request, pk, action):
    """Approve or reject a leave request."""
    if request.method == "POST" and _can_manage_hr(request.user):
        leave = get_object_or_404(_org_filter(request, LeaveRequest.objects.all()), pk=pk)
        if action in ("approved", "rejected"):
            leave.status = action
            leave.approved_by = request.user
            leave.approved_at = timezone.now()
            leave.save(update_fields=["status", "approved_by", "approved_at"])
            messages.success(request, f"Leave request {action}.")
    return redirect("hr:leave_list")


@login_required
def payroll_list(request):
    """List payroll records and total payout summary."""
    qs = _org_filter(request, PayrollRecord.objects.select_related("employee"))
    status_filter = request.GET.get("status", "").strip()
    if status_filter:
        qs = qs.filter(status=status_filter)

    total_net = qs.aggregate(total=Sum("net_pay"))["total"] or 0
    paginator = Paginator(qs, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "hr/payroll_list.html",
        {
            "sidebar": "hr",
            "submenu": "hr_payroll",
            "page_obj": page_obj,
            "status_filter": status_filter,
            "total_net": total_net,
            "can_manage_hr": _can_manage_hr(request.user),
        },
    )


@login_required
def payroll_add(request):
    """Create a payroll record."""
    org = getattr(request.user, "organization", None)
    form = PayrollRecordForm(request.POST or None, organization=org)
    if request.method == "POST" and form.is_valid():
        payroll = form.save(commit=False)
        payroll.organization = org or payroll.employee.organization
        if payroll.status == "paid" and not payroll.paid_at:
            payroll.paid_at = timezone.now()
        payroll.save()
        messages.success(request, "Payroll record created.")
        return redirect("hr:payroll_list")
    return render(
        request,
        "hr/form.html",
        {
            "sidebar": "hr",
            "submenu": "hr_payroll",
            "form": form,
            "title": "Create Payroll Record",
            "back_url": "hr:payroll_list",
        },
    )


@login_required
def payroll_mark_paid(request, pk):
    """Mark a payroll record as paid."""
    if request.method == "POST" and _can_manage_hr(request.user):
        payroll = get_object_or_404(_org_filter(request, PayrollRecord.objects.all()), pk=pk)
        payroll.status = "paid"
        payroll.paid_at = timezone.now()
        payroll.save(update_fields=["status", "paid_at"])
        messages.success(request, "Payroll marked as paid.")
    return redirect("hr:payroll_list")
