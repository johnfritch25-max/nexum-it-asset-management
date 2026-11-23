from django import forms
from authentication.models import User
from .models import Attendance, EmployeeProfile, LeaveRequest, PayrollRecord


class EmployeeProfileForm(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        fields = [
            "user",
            "employee_code",
            "job_title",
            "employment_type",
            "employment_status",
            "hire_date",
            "base_salary",
            "hourly_rate",
            "emergency_contact_name",
            "emergency_contact_phone",
            "can_access_pos",
            "can_access_ordering",
        ]
        widgets = {
            "user": forms.Select(attrs={"class": "form-select"}),
            "employee_code": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. EMP-0001"}
            ),
            "job_title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Cashier / IT Support"}
            ),
            "employment_type": forms.Select(attrs={"class": "form-select"}),
            "employment_status": forms.Select(attrs={"class": "form-select"}),
            "hire_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "base_salary": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "hourly_rate": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "emergency_contact_name": forms.TextInput(attrs={"class": "form-control"}),
            "emergency_contact_phone": forms.TextInput(attrs={"class": "form-control"}),
            "can_access_pos": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "can_access_ordering": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)
        qs = User.objects.filter(is_deleted=False)
        if organization:
            qs = qs.filter(organization=organization)
        if not self.instance.pk:
            qs = qs.filter(hr_profile__isnull=True)
        self.fields["user"].queryset = qs.order_by("full_name", "email")


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ["employee", "date", "time_in", "time_out", "status", "notes"]
        widgets = {
            "employee": forms.Select(attrs={"class": "form-select"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "time_in": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "time_out": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)
        qs = User.objects.filter(is_deleted=False, is_active=True)
        if organization:
            qs = qs.filter(organization=organization)
        self.fields["employee"].queryset = qs.order_by("full_name", "email")


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ["employee", "leave_type", "start_date", "end_date", "reason"]
        widgets = {
            "employee": forms.Select(attrs={"class": "form-select"}),
            "leave_type": forms.Select(attrs={"class": "form-select"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "reason": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)
        qs = User.objects.filter(is_deleted=False, is_active=True)
        if organization:
            qs = qs.filter(organization=organization)
        self.fields["employee"].queryset = qs.order_by("full_name", "email")

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_date")
        end = cleaned.get("end_date")
        if start and end and end < start:
            raise forms.ValidationError("End date cannot be earlier than start date.")
        return cleaned


class PayrollRecordForm(forms.ModelForm):
    class Meta:
        model = PayrollRecord
        fields = [
            "employee",
            "period_start",
            "period_end",
            "basic_pay",
            "allowances",
            "deductions",
            "status",
            "notes",
        ]
        widgets = {
            "employee": forms.Select(attrs={"class": "form-select"}),
            "period_start": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "period_end": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "basic_pay": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "allowances": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "deductions": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)
        qs = User.objects.filter(is_deleted=False, is_active=True)
        if organization:
            qs = qs.filter(organization=organization)
        self.fields["employee"].queryset = qs.order_by("full_name", "email")

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("period_start")
        end = cleaned.get("period_end")
        if start and end and end < start:
            raise forms.ValidationError("Period end date cannot be earlier than start date.")
        return cleaned
