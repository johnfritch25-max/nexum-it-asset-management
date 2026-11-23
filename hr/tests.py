from datetime import date, time
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from assets.models import Asset, MaintenanceRecord
from authentication.models import User
from dashboard.models import Organization
from .models import Attendance, EmployeeProfile, LeaveRequest, PayrollRecord


class HrModelsAndErpApiTests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Nexum ERP Org")
        self.user = User.objects.create_user(
            email="cashier@nexum.local",
            full_name="Kate Cashier",
            username="kate_cashier",
            phone="+639171234567",
            password="StrongPassword123!",
            is_active=True,
            organization=self.org,
        )
        self.profile = EmployeeProfile.objects.create(
            user=self.user,
            employee_code="EMP-0001",
            job_title="POS Cashier",
            employment_status="active",
            base_salary=Decimal("25000.00"),
            can_access_pos=True,
            can_access_ordering=False,
            organization=self.org,
        )
        self.client_api = APIClient()

    def test_attendance_hours_and_leave_days(self):
        att = Attendance.objects.create(
            employee=self.user,
            date=date(2026, 11, 23),
            time_in=time(8, 0),
            time_out=time(17, 0),
            organization=self.org,
        )
        self.assertEqual(att.hours_worked, 9.0)

        leave = LeaveRequest.objects.create(
            employee=self.user,
            leave_type="vacation",
            start_date=date(2026, 11, 24),
            end_date=date(2026, 11, 26),
            reason="Family trip",
            organization=self.org,
        )
        self.assertEqual(leave.total_days, 3)

    def test_payroll_net_pay_auto_calculation(self):
        payroll = PayrollRecord.objects.create(
            employee=self.user,
            period_start=date(2026, 11, 1),
            period_end=date(2026, 11, 15),
            basic_pay=Decimal("12500.00"),
            allowances=Decimal("1500.00"),
            deductions=Decimal("500.00"),
            status="approved",
            organization=self.org,
        )
        self.assertEqual(payroll.net_pay, Decimal("13500.00"))

    def test_erp_staff_auth_pos_and_ordering_access(self):
        url = reverse("hr:erp_staff_auth")
        # Authorized for POS
        res_pos = self.client_api.post(
            url,
            {"identifier": "cashier@nexum.local", "password": "StrongPassword123!", "system": "pos"},
            format="json",
        )
        self.assertEqual(res_pos.status_code, status.HTTP_200_OK)
        self.assertIn("access", res_pos.data)
        self.assertEqual(res_pos.data["staff"]["employee_code"], "EMP-0001")

        # Denied for Ordering
        res_ord = self.client_api.post(
            url,
            {"identifier": "kate_cashier", "password": "StrongPassword123!", "system": "ordering"},
            format="json",
        )
        self.assertEqual(res_ord.status_code, status.HTTP_403_FORBIDDEN)

    def test_erp_equipment_expenses_endpoint(self):
        asset = Asset.objects.create(
            tag="AST-1001",
            name="POS Terminal",
            price=15000.0,
            purchase_date=date(2026, 11, 10),
            organization=self.org,
        )
        MaintenanceRecord.objects.create(
            asset=asset,
            service_id="SRV-001",
            date=date(2026, 11, 15),
            maintenance_type="Calibration",
            cost=Decimal("1200.00"),
            technician="Tech A",
            status="Completed",
            organization=self.org,
        )

        self.client_api.force_authenticate(user=self.user)
        res = self.client_api.get(reverse("hr:erp_equipment_expenses"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 2)
        self.assertEqual(res.data["total_amount"], 16200.0)
