from celery import shared_task
from datetime import date
from django.utils import timezone
from core.models import Attendance, EmployeeProfile, Payroll,Leave
from core.utils import send_salary_email, generate_payroll_pdf
from core.payroll_logic import calculate_salary


@shared_task
def mark_absent_employees():

    today = date.today()

    for emp in EmployeeProfile.objects.all():

        leave_exists = Leave.objects.filter(
            employee=emp,
            start_date__lte=today,
            end_date__gte=today,
            status="APPROVED"
        ).exists()

        if leave_exists:
            continue

        Attendance.objects.get_or_create(
            employee=emp,
            date=today,
            defaults={"status": "ABSENT"}
        )


@shared_task
def generate_monthly_payroll():

    today = date.today()
    month = today.month
    year = today.year

    for emp in EmployeeProfile.objects.all():

        # duplicate check
        if Payroll.objects.filter(employee=emp, month=month, year=year).exists():
            continue

        data = calculate_salary(emp, month, year)

        Payroll.objects.create(
            employee=emp,
            month=month,
            year=year,
            base_salary=emp.base_salary,
            allowance=emp.allowance,
            deduction=emp.deduction,
            net_salary=data["net_salary"],
            status="PENDING",
        )

    return "Monthly payroll generated"

@shared_task
def mark_payroll_paid_task(payroll_id):

    payroll = Payroll.objects.get(id=payroll_id)

    # status update
    payroll.status = "PAID"
    payroll.paid_at = timezone.now()
    payroll.save()

    # PDF generate
    pdf_path = generate_payroll_pdf(payroll)
    payroll.pdf_file = pdf_path
    payroll.save()

    # Email send
    send_salary_email(
        payroll.employee.user.email,
        pdf_path
    )

    return "Payroll marked as PAID"