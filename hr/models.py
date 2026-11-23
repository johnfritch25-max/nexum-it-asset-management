import uuid
from datetime import datetime
from decimal import Decimal
from django.db import models
from simple_history.models import HistoricalRecords

from authentication.models import User
from dashboard.models import Organization, SoftDeleteModel, TimeStampModel


class EmployeeProfile(TimeStampModel, SoftDeleteModel):
    """HR profile extending an existing User with employment, payroll, and ERP access flags."""

    EMPLOYMENT_TYPE_CHOICES = [
        ("full_time", "Full-Time"),
        ("part_time", "Part-Time"),
        ("contract", "Contract"),
        ("intern", "Intern"),
    ]
    EMPLOYMENT_STATUS_CHOICES = [
        ("active", "Active"),
        ("probation", "Probation"),
        ("on_leave", "On Leave"),
        ("resigned", "Resigned"),
        ("terminated", "Terminated"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="hr_profile"
    )
    employee_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    job_title = models.CharField(max_length=120, blank=True, null=True)
    employment_type = models.CharField(
        max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default="full_time"
    )
    employment_status = models.CharField(
        max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, default="active"
    )
    hire_date = models.DateField(blank=True, null=True)
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    emergency_contact_name = models.CharField(max_length=150, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=50, blank=True, null=True)

    # ERP Integration flags (POS & Ordering)
    can_access_pos = models.BooleanField(default=False)
    can_access_ordering = models.BooleanField(default=False)

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, blank=True, null=True
    )
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Employee Profile"
        verbose_name_plural = "Employee Profiles"
        ordering = ["-created_at"]

    def __str__(self):
        code = self.employee_code or self.user.employee_id or "NO-ID"
        return f"{code} - {self.user.get_full_name()}"


class Attendance(TimeStampModel):
    """Daily employee time-in and time-out record."""

    STATUS_CHOICES = [
        ("present", "Present"),
        ("late", "Late"),
        ("half_day", "Half-Day"),
        ("absent", "Absent"),
        ("on_leave", "On Leave"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="attendances"
    )
    date = models.DateField()
    time_in = models.TimeField(blank=True, null=True)
    time_out = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="present")
    notes = models.TextField(blank=True, null=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, blank=True, null=True
    )

    class Meta:
        verbose_name = "Attendance"
        verbose_name_plural = "Attendance Records"
        ordering = ["-date", "-time_in"]
        unique_together = ("employee", "date")

    @property
    def hours_worked(self):
        if self.time_in and self.time_out:
            dt_in = datetime.combine(self.date, self.time_in)
            dt_out = datetime.combine(self.date, self.time_out)
            diff = (dt_out - dt_in).total_seconds()
            if diff > 0:
                return round(diff / 3600, 2)
        return 0.0

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.date} ({self.get_status_display()})"


class LeaveRequest(TimeStampModel):
    """Employee leave application and approval workflow."""

    LEAVE_TYPE_CHOICES = [
        ("vacation", "Vacation Leave"),
        ("sick", "Sick Leave"),
        ("emergency", "Emergency Leave"),
        ("unpaid", "Unpaid Leave"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="leave_requests"
    )
    leave_type = models.CharField(
        max_length=20, choices=LEAVE_TYPE_CHOICES, default="vacation"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_leaves",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, blank=True, null=True
    )

    class Meta:
        verbose_name = "Leave Request"
        verbose_name_plural = "Leave Requests"
        ordering = ["-created_at"]

    @property
    def total_days(self):
        if self.start_date and self.end_date and self.end_date >= self.start_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.get_leave_type_display()} ({self.status})"


class PayrollRecord(TimeStampModel):
    """Payroll period calculation and payout record for an employee."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("approved", "Approved"),
        ("paid", "Paid"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="payroll_records"
    )
    period_start = models.DateField()
    period_end = models.DateField()
    basic_pay = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    allowances = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    deductions = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    net_pay = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    paid_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, blank=True, null=True
    )

    class Meta:
        verbose_name = "Payroll Record"
        verbose_name_plural = "Payroll Records"
        ordering = ["-period_end", "-created_at"]

    def save(self, *args, **kwargs):
        basic = Decimal(self.basic_pay or 0)
        allow = Decimal(self.allowances or 0)
        deduct = Decimal(self.deductions or 0)
        self.net_pay = basic + allow - deduct
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.get_full_name()} ({self.period_start} to {self.period_end})"
