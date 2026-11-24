# Generated to sync TimeStampModel and SoftDeleteModel fields with dashboard.models

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hr", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="employeeprofile",
            name="deleted_at",
        ),
        migrations.RemoveField(
            model_name="historicalemployeeprofile",
            name="deleted_at",
        ),
        migrations.AddField(
            model_name="employeeprofile",
            name="status",
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AddField(
            model_name="historicalemployeeprofile",
            name="status",
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AddField(
            model_name="employeeprofile",
            name="created_by",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="employeeprofile",
            name="updated_by",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="historicalemployeeprofile",
            name="created_by",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="historicalemployeeprofile",
            name="updated_by",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="attendance",
            name="created_by",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="attendance",
            name="updated_by",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="leaverequest",
            name="created_by",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="leaverequest",
            name="updated_by",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="payrollrecord",
            name="created_by",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="payrollrecord",
            name="updated_by",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
