import os
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from django.utils import timezone
from django.core.mail import EmailMessage



def generate_payroll_pdf(payroll):
    folder = os.path.join(settings.MEDIA_ROOT, "payrolls")
    os.makedirs(folder, exist_ok=True)

    filename = f"salary_slip_{payroll.id}.pdf"
    file_path = os.path.join(folder, filename)

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    employee = payroll.employee
    user = employee.user

    # ===== Header =====
    c.setFillColor(colors.HexColor("#1f4fd8"))
    c.rect(0, height - 80, width, 80, fill=1)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(40, height - 50, "Company Management System")
    c.setFont("Helvetica", 12)
    c.drawString(40, height - 70, "Salary Slip")

    # ===== Body =====
    y = height - 120
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)

    c.drawString(40, y, f"Employee Email: {user.email}")
    y -= 20
    c.drawString(40, y, f"Position: {employee.position}")
    y -= 20
    c.drawString(40, y, f"Month / Year: {payroll.month} / {payroll.year}")
    y -= 30

    # Line
    c.line(40, y, width - 40, y)
    y -= 30

    # Salary Details Box
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Salary Details")
    y -= 20

    c.setFont("Helvetica", 11)
    c.drawString(60, y, f"Basic Salary: {payroll.base_salary}")
    y -= 20
    c.drawString(60, y, f"Allowance: {payroll.allowance}")
    y -= 20
    c.drawString(60, y, f"Deduction: {payroll.deduction}")
    y -= 20

    c.line(40, y, width - 40, y)
    y -= 30

    # Net Salary Highlight
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#0a7d2c"))
    c.drawString(40, y, f"Net Salary: {payroll.net_salary}")
    y -= 30

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    c.drawString(40, y, f"Paid At: {timezone.now().strftime('%d-%m-%Y %H:%M')}")

    # Footer
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(40, 40, "This is a system generated salary slip. No signature required.")

    c.showPage()
    c.save()

    return f"payrolls/{filename}"



def send_salary_email(employee_email, pdf_path):
    subject = "Your Salary Slip"
    body = "Hi,\n\nPlease find attached your salary slip.\n\nRegards,\nHR Team"

    email = EmailMessage(
        subject=subject,
        body=body,
        to=[employee_email],
    )

    full_path = os.path.join(settings.MEDIA_ROOT, pdf_path)
    email.attach_file(full_path)
    email.send(fail_silently=False)