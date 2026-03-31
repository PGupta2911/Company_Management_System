from django.db import models
from django.conf import settings

class Organization(models.Model):

    name = models.CharField(max_length=255)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_organizations"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class EmployeeProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employee_profile")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="employees")

    position = models.CharField(max_length=100)
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    leave_balance = models.IntegerField(default=12)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.position}"



class Payroll(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "PENDING"),
        ("PAID", "PAID"),
    )

    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name="payrolls")
    month = models.PositiveIntegerField()   # 1-12
    year = models.PositiveIntegerField()

    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    net_salary = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to="payrolls/", null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("employee", "month", "year")

    def __str__(self):
        return f"{self.employee.user.email} - {self.month}/{self.year}"
    
class Attendance(models.Model):

    STATUS_CHOICES = [
        ("PRESENT", "Present"),
        ("LATE", "Late"),
        ("ABSENT", "Absent"),
    ]

    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name="attendances"
    )

    date = models.DateField()

    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    working_hours = models.CharField(max_length=20, null=True, blank=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PRESENT"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("employee", "date")

    def __str__(self):
        return f"{self.employee.user.full_name} - {self.date}"
    
class ActivityLog(models.Model):

    ACTION_CHOICES = [
        ("CREATE_ORG", "Organization Created"),
        ("ADD_EMPLOYEE", "Employee Added"),
        ("GENERATE_PAYROLL", "Payroll Generated"),
        ("DELETE_ORG", "Organization Deleted"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    action = models.CharField(max_length=50, choices=ACTION_CHOICES)

    message = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message

class Leave(models.Model):

    LEAVE_TYPE_CHOICES = [
        ("SICK", "Sick Leave"),
        ("CASUAL", "Casual Leave"),
    ]

    LEAVE_PAYMENT_CHOICES = [
        ("PAID", "Paid"),
        ("UNPAID", "Unpaid"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name="leaves"
    )

    leave_type = models.CharField(
        max_length=10,
        choices=LEAVE_TYPE_CHOICES
    )

    # 🔥 NEW FIELD (IMPORTANT)
    leave_payment = models.CharField(
        max_length=10,
        choices=LEAVE_PAYMENT_CHOICES,
        default="PAID"
    )

    start_date = models.DateField()
    end_date = models.DateField()

    reason = models.TextField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING"
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_leaves"
    )

    approved_at = models.DateTimeField(null=True, blank=True)

    applied_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.employee.user.email} - {self.leave_type} ({self.leave_payment})"