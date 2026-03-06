from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from .models import Organization, EmployeeProfile,Payroll
from .serializers import OrganizationSerializer, EmployeeCreateSerializer, EmployeeProfileSerializer,PayrollSerializer
from .utils import generate_payroll_pdf, send_salary_email
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from datetime import datetime
from django.utils import timezone
from django.shortcuts import render, get_object_or_404


def login_view(request):
    return render(request, "auth/login.html")

def hr_dashboard_view(request):
    return render(request, "hr/dashboard.html")

def hr_employees_view(request):
    return render(request, "hr/employee.html")

def hr_payroll_view(request):
    return render(request, "hr/payroll.html")


def employee_dashboard_view(request):
    return render(request, "employee/dashboard.html")



class IsHR(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "HR"


class MyOrganizationView(APIView):
    permission_classes = [IsHR]

    def get(self, request):
        try:
            org = Organization.objects.get(created_by=request.user)
        except Organization.DoesNotExist:
            return Response({"detail": "Organization not found"}, status=404)

        serializer = OrganizationSerializer(org)
        return Response(serializer.data)

    def post(self, request):
        # Check if already exists
        if Organization.objects.filter(created_by=request.user).exists():
            return Response(
                {"detail": "Organization already exists for this HR"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = OrganizationSerializer(data=request.data)
        if serializer.is_valid():
            org = serializer.save(created_by=request.user)
            return Response(OrganizationSerializer(org).data, status=201)

        return Response(serializer.errors, status=400)

    def put(self, request):
        try:
            org = Organization.objects.get(created_by=request.user)
        except Organization.DoesNotExist:
            return Response({"detail": "Organization not found"}, status=404)

        serializer = OrganizationSerializer(org, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)


class HRCreateEmployeeView(APIView):
    permission_classes = [IsHR]

    def post(self, request):
        serializer = EmployeeCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            profile = serializer.save()
            return Response(EmployeeProfileSerializer(profile).data, status=201)
        return Response(serializer.errors, status=400)


class HREmployeeListView(APIView):
    permission_classes = [IsHR]

    def get(self, request):
        org = request.user.organization
        employees = EmployeeProfile.objects.filter(organization=org)
        serializer = EmployeeProfileSerializer(employees, many=True)
        return Response(serializer.data)


class MyEmployeeProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.employee_profile
        except EmployeeProfile.DoesNotExist:
            return Response({"detail": "Employee profile not found"}, status=404)

        serializer = EmployeeProfileSerializer(profile)
        return Response(serializer.data)
    
    
class HRDeleteEmployeeView(APIView):
    permission_classes = [IsHR]

    def delete(self, request, employee_id):
        try:
            employee = EmployeeProfile.objects.get(
                id=employee_id,
                organization=request.user.organization
            )
        except EmployeeProfile.DoesNotExist:
            return Response({"detail": "Employee not found"}, status=404)

        user = employee.user
        employee.delete()
        user.delete()
        return Response({"detail": "Employee deleted successfully"}, status=200)

class HRDashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        org = request.user.organization

        total_employees = EmployeeProfile.objects.filter(organization=org).count()
        pending_payrolls = Payroll.objects.filter(
            employee__organization=org,
            status="PENDING"
        ).count()

        return Response({
            "total_employees": total_employees,
            "pending_payrolls": pending_payrolls
        })
    


class HRGeneratePayrollView(APIView):
    permission_classes = [IsHR]

    def post(self, request):
        employee_id = request.data.get("employee_id")
        month = request.data.get("month")
        year = request.data.get("year")

        if not employee_id or not month or not year:
            return Response({"detail": "employee_id, month, year are required"}, status=400)

        try:
            employee = EmployeeProfile.objects.get(id=employee_id, organization=request.user.organization)
        except EmployeeProfile.DoesNotExist:
            return Response({"detail": "Employee not found in your organization"}, status=404)

        # Prevent duplicate payroll
        if Payroll.objects.filter(employee=employee, month=month, year=year).exists():
            return Response({"detail": "Payroll already generated for this month"}, status=400)

        base = employee.base_salary
        allowance = employee.allowance
        deduction = employee.deduction
        net = base + allowance - deduction

        payroll = Payroll.objects.create(
            employee=employee,
            month=month,
            year=year,
            base_salary=base,
            allowance=allowance,
            deduction=deduction,
            net_salary=net,
            status="PENDING",
        )

        return Response(PayrollSerializer(payroll).data, status=201)


class HRPayrollListView(APIView):
    permission_classes = [IsHR]

    def get(self, request):
        org = request.user.organization
        month = request.GET.get("month")
        year = request.GET.get("year")

        if not month or not year:
            return Response({"detail": "month and year required"}, status=400)

        employees = EmployeeProfile.objects.filter(organization=org)

        response_data = []

        for emp in employees:
            payroll = Payroll.objects.filter(
                employee=emp,
                month=month,
                year=year
            ).first()

            if payroll:
                response_data.append({
                    "employee_id": emp.id,
                    "employee_name": emp.user.full_name or emp.user.email,
                    "status": payroll.status,
                    "net_salary": payroll.net_salary,
                    "payroll_id": payroll.id,
                    "pdf_file": payroll.pdf_file.url if payroll.pdf_file else None
                })
            else:
                response_data.append({
                    "employee_id": emp.id,
                    "employee_name": emp.user.full_name or emp.user.email,
                    "status": "UNPAID",
                    "net_salary": None,
                    "payroll_id": None,
                    "pdf_file": None
                })

        return Response(response_data)
    

class HRMarkPayrollPaidView(APIView):
    def post(self, request, payroll_id):
        payroll = get_object_or_404(Payroll, id=payroll_id)

        if payroll.status == "PAID":
            return Response(
                {"error": "Payroll already marked as paid"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Generate PDF
        pdf_relative_path = generate_payroll_pdf(payroll)

        # 2. Save PDF path + update status
        payroll.pdf_file = pdf_relative_path
        payroll.status = "PAID"
        payroll.paid_at = timezone.now()
        payroll.save()

        # 3. Send email
        employee_email = payroll.employee.user.email
        send_salary_email(employee_email, pdf_relative_path)

        return Response(
            {"message": "Salary marked as paid, PDF generated and email sent"},
            status=status.HTTP_200_OK
        )


class MyPayrollListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.employee_profile
        except EmployeeProfile.DoesNotExist:
            return Response({"detail": "Employee profile not found"}, status=404)

        payrolls = Payroll.objects.filter(employee=profile).order_by("-year", "-month")
        serializer = PayrollSerializer(payrolls, many=True, context={"request": request})
        return Response(serializer.data)
    

@api_view(['GET'])
def month_status_view(request):
    current_month = datetime.now().month
    current_year = datetime.now().year

    months = [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ]

    response_data = []

    for index, month_name in enumerate(months, start=1):

        if index > current_month:
            month_status = "locked"
        else:
            payrolls = Payroll.objects.filter(
                month=index,
                year=current_year
            )

            # If no payrolls created yet → treat as unpaid
            if not payrolls.exists():
                month_status = "unpaid"

            # If all payrolls are PAID
            elif payrolls.filter(status="PAID").count() == payrolls.count():
                month_status = "paid"

            # Otherwise pending exists
            else:
                month_status = "unpaid"

        response_data.append({
            "month_number": index,
            "month_name": month_name,
            "status": month_status
        })

    return Response(response_data)