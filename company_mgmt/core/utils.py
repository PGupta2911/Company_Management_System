import os
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from django.utils import timezone
from django.core.mail import EmailMessage
from reportlab.platypus import Table, TableStyle



def generate_payroll_pdf(payroll):
    folder = os.path.join(settings.MEDIA_ROOT, "payrolls")
    os.makedirs(folder, exist_ok=True)

    filename = f"salary_slip_{payroll.id}.pdf"
    file_path = os.path.join(folder, filename)

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    employee = payroll.employee
    user = employee.user

    # ================= HEADER =================

    c.setFillColor(colors.HexColor("#2563eb"))
    c.rect(0, height - 90, width, 90, fill=1)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(40, height - 55, "Company Management System")

    c.setFont("Helvetica", 12)
    c.drawString(40, height - 75, "Employee Salary Slip")

    # ================= EMPLOYEE INFO =================

    y = height - 130

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y, "Employee Information")

    y -= 20
    c.line(40, y, width - 40, y)

    y -= 25
    c.setFont("Helvetica", 11)

    c.drawString(40, y, f"Employee Email:")
    c.drawString(200, y, f"{user.email}")

    y -= 20
    c.drawString(40, y, f"Position:")
    c.drawString(200, y, f"{employee.position}")

    y -= 20
    c.drawString(40, y, f"Month / Year:")
    c.drawString(200, y, f"{payroll.month} / {payroll.year}")

    y -= 40

    # ================= SALARY TABLE =================

    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y, "Salary Breakdown")

    y -= 20
    c.line(40, y, width - 40, y)

    y -= 25

    table_data = [
        ["Component", "Amount"],
        ["Basic Salary", f"₹ {payroll.base_salary}"],
        ["Allowance", f"₹ {payroll.allowance}"],
        ["Deduction", f"₹ {payroll.deduction}"],
    ]

    table = Table(table_data, colWidths=[300, 200])

    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 1), (1, -1), "RIGHT"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
    ])

    table.setStyle(style)

    table.wrapOn(c, width, height)
    table.drawOn(c, 40, y - 100)

    y -= 140

    # ================= NET SALARY BOX =================

    c.setFillColor(colors.HexColor("#ecfdf5"))
    c.rect(40, y - 20, width - 80, 40, fill=1, stroke=0)

    c.setFillColor(colors.HexColor("#16a34a"))
    c.setFont("Helvetica-Bold", 14)

    c.drawString(50, y, f"Net Salary : ₹ {payroll.net_salary}")

    y -= 50

    # ================= PAYMENT INFO =================

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)

    c.drawString(
        40,
        y,
        f"Payment Date : {timezone.now().strftime('%d %B %Y %H:%M')}"
    )

    # ================= FOOTER =================

    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors.grey)

    c.drawString(
        40,
        40,
        "This is a system generated salary slip. No signature required."
    )

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