# Generated manually for hr app

from decimal import Decimal
import django.db.models.deletion
import simple_history.models
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("dashboard", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="EmployeeProfile",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "employee_code",
                    models.CharField(blank=True, max_length=50, null=True, unique=True),
                ),
                ("job_title", models.CharField(blank=True, max_length=120, null=True)),
                (
                    "employment_type",
                    models.CharField(
                        choices=[
                            ("full_time", "Full-Time"),
                            ("part_time", "Part-Time"),
                            ("contract", "Contract"),
                            ("intern", "Intern"),
                        ],
                        default="full_time",
                        max_length=20,
                    ),
                ),
                (
                    "employment_status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("probation", "Probation"),
                            ("on_leave", "On Leave"),
                            ("resigned", "Resigned"),
                            ("terminated", "Terminated"),
                        ],
                        default="active",
                        max_length=20,
                    ),
                ),
                ("hire_date", models.DateField(blank=True, null=True)),
                (
                    "base_salary",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=12
                    ),
                ),
                (
                    "hourly_rate",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=10
                    ),
                ),
                (
                    "emergency_contact_name",
                    models.CharField(blank=True, max_length=150, null=True),
                ),
                (
                    "emergency_contact_phone",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                ("can_access_pos", models.BooleanField(default=False)),
                ("can_access_ordering", models.BooleanField(default=False)),
                (
                    "organization",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dashboard.organization",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="hr_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Employee Profile",
                "verbose_name_plural": "Employee Profiles",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="HistoricalEmployeeProfile",
            fields=[
                ("created_at", models.DateTimeField(blank=True, editable=False, null=True)),
                ("updated_at", models.DateTimeField(blank=True, editable=False, null=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                (
                    "id",
                    models.UUIDField(db_index=True, default=uuid.uuid4, editable=False),
                ),
                (
                    "employee_code",
                    models.CharField(blank=True, db_index=True, max_length=50, null=True),
                ),
                ("job_title", models.CharField(blank=True, max_length=120, null=True)),
                (
                    "employment_type",
                    models.CharField(
                        choices=[
                            ("full_time", "Full-Time"),
                            ("part_time", "Part-Time"),
                            ("contract", "Contract"),
                            ("intern", "Intern"),
                        ],
                        default="full_time",
                        max_length=20,
                    ),
                ),
                (
                    "employment_status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("probation", "Probation"),
                            ("on_leave", "On Leave"),
                            ("resigned", "Resigned"),
                            ("terminated", "Terminated"),
                        ],
                        default="active",
                        max_length=20,
                    ),
                ),
                ("hire_date", models.DateField(blank=True, null=True)),
                (
                    "base_salary",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=12
                    ),
                ),
                (
                    "hourly_rate",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=10
                    ),
                ),
                (
                    "emergency_contact_name",
                    models.CharField(blank=True, max_length=150, null=True),
                ),
                (
                    "emergency_contact_phone",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                ("can_access_pos", models.BooleanField(default=False)),
                ("can_access_ordering", models.BooleanField(default=False)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="dashboard.organization",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical Employee Profile",
                "verbose_name_plural": "historical Employee Profiles",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="LeaveRequest",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "leave_type",
                    models.CharField(
                        choices=[
                            ("vacation", "Vacation Leave"),
                            ("sick", "Sick Leave"),
                            ("emergency", "Emergency Leave"),
                            ("unpaid", "Unpaid Leave"),
                        ],
                        default="vacation",
                        max_length=20,
                    ),
                ),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("reason", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                (
                    "approved_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="approved_leaves",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="leave_requests",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dashboard.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "Leave Request",
                "verbose_name_plural": "Leave Requests",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="PayrollRecord",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("period_start", models.DateField()),
                ("period_end", models.DateField()),
                (
                    "basic_pay",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=12
                    ),
                ),
                (
                    "allowances",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=12
                    ),
                ),
                (
                    "deductions",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=12
                    ),
                ),
                (
                    "net_pay",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=12
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("approved", "Approved"),
                            ("paid", "Paid"),
                        ],
                        default="draft",
                        max_length=20,
                    ),
                ),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("notes", models.TextField(blank=True, null=True)),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payroll_records",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dashboard.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "Payroll Record",
                "verbose_name_plural": "Payroll Records",
                "ordering": ["-period_end", "-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Attendance",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("date", models.DateField()),
                ("time_in", models.TimeField(blank=True, null=True)),
                ("time_out", models.TimeField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("present", "Present"),
                            ("late", "Late"),
                            ("half_day", "Half-Day"),
                            ("absent", "Absent"),
                            ("on_leave", "On Leave"),
                        ],
                        default="present",
                        max_length=20,
                    ),
                ),
                ("notes", models.TextField(blank=True, null=True)),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attendances",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dashboard.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "Attendance",
                "verbose_name_plural": "Attendance Records",
                "ordering": ["-date", "-time_in"],
                "unique_together": {("employee", "date")},
            },
        ),
    ]
