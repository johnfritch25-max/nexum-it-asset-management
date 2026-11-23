from django.urls import path
from . import views
from .api_views import (
    EquipmentExpenseListAPI,
    PayrollExpenseListAPI,
    StaffAuthAPI,
    StaffDirectoryAPI,
)

app_name = "hr"

urlpatterns = [
    # Employees
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/add/", views.employee_add, name="employee_add"),
    path("employees/detail/<uuid:pk>/", views.employee_detail, name="employee_detail"),
    path("employees/edit/<uuid:pk>/", views.employee_edit, name="employee_edit"),
    # Attendance
    path("attendance/", views.attendance_list, name="attendance_list"),
    path("attendance/add/", views.attendance_add, name="attendance_add"),
    path("attendance/clock-in/", views.attendance_clock_in, name="attendance_clock_in"),
    path("attendance/clock-out/", views.attendance_clock_out, name="attendance_clock_out"),
    # Leave Requests
    path("leaves/", views.leave_list, name="leave_list"),
    path("leaves/add/", views.leave_add, name="leave_add"),
    path(
        "leaves/<uuid:pk>/status/<str:action>/",
        views.leave_update_status,
        name="leave_update_status",
    ),
    # Payroll
    path("payroll/", views.payroll_list, name="payroll_list"),
    path("payroll/add/", views.payroll_add, name="payroll_add"),
    path("payroll/<uuid:pk>/mark-paid/", views.payroll_mark_paid, name="payroll_mark_paid"),
]

hr_api_url_patterns = [
    # ERP Integration APIs for Kate (POS), Alejandro (Ordering), and Judy (Expenses)
    path("api/erp/staff-auth/", StaffAuthAPI.as_view(), name="erp_staff_auth"),
    path("api/erp/staff/", StaffDirectoryAPI.as_view(), name="erp_staff_directory"),
    path(
        "api/erp/equipment-expenses/",
        EquipmentExpenseListAPI.as_view(),
        name="erp_equipment_expenses",
    ),
    path(
        "api/erp/payroll-expenses/",
        PayrollExpenseListAPI.as_view(),
        name="erp_payroll_expenses",
    ),
]
