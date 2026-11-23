from django.contrib import admin
from .models import Attendance, EmployeeProfile, LeaveRequest, PayrollRecord


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = (
        "employee_code",
        "user",
        "job_title",
        "employment_type",
        "employment_status",
        "can_access_pos",
        "can_access_ordering",
    )
    list_filter = ("employment_type", "employment_status", "can_access_pos", "can_access_ordering")
    search_fields = ("employee_code", "user__full_name", "user__email", "job_title")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("employee", "date", "time_in", "time_out", "status")
    list_filter = ("status", "date")
    search_fields = ("employee__full_name", "employee__email")


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("employee", "leave_type", "start_date", "end_date", "status", "approved_by")
    list_filter = ("leave_type", "status")
    search_fields = ("employee__full_name", "employee__email")


@admin.register(PayrollRecord)
class PayrollRecordAdmin(admin.ModelAdmin):
    list_display = ("employee", "period_start", "period_end", "basic_pay", "net_pay", "status")
    list_filter = ("status",)
    search_fields = ("employee__full_name", "employee__email")
