import csv
import zipfile
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import time,date
from django.http import HttpResponse
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from accounts.models import User
from .models import Organization, EmployeeProfile,Payroll,ActivityLog,Attendance,Leave
from .serializers import (OrganizationSerializer, EmployeeCreateSerializer,
                          EmployeeProfileSerializer,PayrollSerializer, 
                          SuperAdminCreateOrganizationSerializer,SuperAdminOrganizationListSerializer,
                          SuperAdminOrganizationDetailSerializer,
                          ActivityLogSerializer,LeaveSerializer)
from .utils import generate_payroll_pdf, send_salary_email,timezone
from core.payroll_logic import calculate_salary
from core.tasks import mark_payroll_paid_task
from reportlab.lib.pagesizes import A4
from datetime import datetime
from calendar import monthrange

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

def hr_attendance_view(request):
    return render(request,  "hr/attendance.html")

def hr_leaves_view(request):
    return render(request, "hr/leaves.html")

def employee_leave_view(request):
    return render(request, "employee/leave.html")

def employee_dashboard_view(request):
    return render(request, "employee/dashboard.html")

def superadmin_dashboard_page(request):
    return render(request,"superadmin/dashboard.html")

def organization_detail_page(request, org_id):
    return render(request,"superadmin/organization_detail.html",{"org_id": org_id})






class IsHR(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "HR"


class MyOrganizationView(APIView):
    permission_classes = [IsHR]

    def get(self, request):

        org = request.user.organization

        if not org:
            return Response({"detail": "Organization not found"}, status=404)

        serializer = OrganizationSerializer(org)
        return Response(serializer.data)


    def post(self, request):

        # HR already belongs to an organization
        if request.user.organization:
            return Response(
                {"detail": "Organization already exists for this HR"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = OrganizationSerializer(data=request.data)

        if serializer.is_valid():

            org = serializer.save(created_by=request.user)

            request.user.organization = org
            request.user.save()

            return Response(OrganizationSerializer(org).data, status=201)

        return Response(serializer.errors, status=400)


    def put(self, request):

        org = request.user.organization

        if not org:
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
            ActivityLog.objects.create(
                user=request.user,
                action="ADD_EMPLOYEE",
                message=f"Employee '{profile.user.full_name}' added"
            )
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

        data = calculate_salary(employee, month, year)
        net = data["net_salary"]
        
        payroll = Payroll.objects.create(
            employee=employee,
            month=month,
            year=year,
            base_salary=employee.base_salary,
            allowance=employee.allowance,
            deduction=employee.deduction,
            net_salary=net,
            status="PENDING",
        )
        
        ActivityLog.objects.create(

            user=request.user,
            action="GENERATE_PAYROLL",
            message=f"Payroll generated for {employee.user.full_name}"

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
        payroll = get_object_or_404(Payroll, id=payroll_id)

        # Celery task trigger
        mark_payroll_paid_task.delay(payroll.id)

        return Response(
        {"message": "Payroll processing started"},
        status=status.HTTP_200_OK
        )


class MyPayrollListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        try:
            profile = request.user.employee_profile
        except EmployeeProfile.DoesNotExist:
            return Response({"detail": "Employee profile not found"}, status=404)

        year = request.GET.get("year")

        payrolls = Payroll.objects.filter(employee=profile)

        # YEAR FILTER
        if year:
            payrolls = payrolls.filter(year=year)

        payrolls = payrolls.order_by("-year", "-month")

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

class SuperAdminDashboardStatsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.user.role != "SUPERADMIN":
            return Response({"error": "Access denied"}, status=403)

        data = {
            "organizations": Organization.objects.count(),
            "hr": User.objects.filter(role="HR").count(),
            "employees": User.objects.filter(role="EMPLOYEE").count(),
            "payrolls": Payroll.objects.count(),
        }

        return Response(data)


class SuperAdminCreateOrganizationView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        if request.user.role != "SUPERADMIN":
            return Response({"error": "Access denied"}, status=403)

        serializer = SuperAdminCreateOrganizationSerializer(data=request.data)

        if serializer.is_valid():

            org_name = serializer.validated_data["organization_name"]
            hr_email = serializer.validated_data["hr_email"]
            hr_name = serializer.validated_data["hr_full_name"]
            hr_password = serializer.validated_data["hr_password"]

            organization = Organization.objects.create(
                name=org_name,
                created_by=request.user
            )

            hr_user = User.objects.create_user(
                email=hr_email,
                password=hr_password,
                role="HR",
                full_name=hr_name
            )
            ActivityLog.objects.create(
                user=request.user,
                action="CREATE_ORG",
                message=f"Organization '{org_name}' created"
            )

            hr_user.organization = organization
            hr_user.save()

            return Response({
                "message": "Organization and HR created successfully"
            })
        
        

        return Response(serializer.errors, status=400)
    

class SuperAdminOrganizationListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.user.role != "SUPERADMIN":
            return Response({"error": "Access denied"}, status=403)

        organizations = Organization.objects.all()

        data = []

        for org in organizations:

            hr_user = User.objects.filter(
                role="HR",
                organization=org
            ).first()

            employee_count = User.objects.filter(
                role="EMPLOYEE",
                organization=org
            ).count()

            data.append({
                "id": org.id,
                "name": org.name,
                "hr_name": hr_user.full_name if hr_user else "No HR",
                "employees": employee_count,
                "created_at": org.created_at
            })

        serializer = SuperAdminOrganizationListSerializer(data, many=True)

        return Response(serializer.data)
    

class SuperAdminOrganizationDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, org_id):

        if request.user.role != "SUPERADMIN":
            return Response({"error": "Access denied"}, status=403)

        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return Response({"error": "Organization not found"}, status=404)

        hr_user = User.objects.filter(
            role="HR",
            organization=organization
        ).first()

        employee_count = User.objects.filter(
            role="EMPLOYEE",
            organization=organization
        ).count()

        payroll_count = Payroll.objects.filter(
            employee__organization=organization
        ).count()

        data = {
            "id": organization.id,
            "name": organization.name,
            "hr_name": hr_user.full_name if hr_user else "No HR",
            "hr_email": hr_user.email if hr_user else "",
            "employees": employee_count,
            "payrolls": payroll_count,
            "created_at": organization.created_at
        }

        serializer = SuperAdminOrganizationDetailSerializer(data)

        return Response(serializer.data)

class SuperAdminOrganizationEmployeesView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, org_id):

        if request.user.role != "SUPERADMIN":
            return Response({"error": "Access denied"}, status=403)

        employees = User.objects.filter(
            role="EMPLOYEE",
            organization_id=org_id
        )

        data = []

        for emp in employees:

            data.append({
                "id": emp.id,
                "full_name": emp.full_name,
                "email": emp.email
            })

        return Response(data)


class SuperAdminOrganizationPayrollsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, org_id):

        if request.user.role != "SUPERADMIN":
            return Response({"error": "Access denied"}, status=403)

        payrolls = Payroll.objects.filter(
            employee__organization_id=org_id
        )

        data = []

        for pay in payrolls:

            data.append({
                "month": pay.month,
                "year": pay.year,
                "net_salary": pay.net_salary,
                "status": pay.status
            })

        return Response(data)

class SuperAdminDeleteOrganizationView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, org_id):

        if request.user.role != "SUPERADMIN":
            return Response({"error": "Access denied"}, status=403)

        try:

            organization = Organization.objects.get(id=org_id)

            org_name = organization.name   # save before delete

            organization.delete()

            # Activity log AFTER successful delete
            ActivityLog.objects.create(
                user=request.user,
                action="DELETE_ORG",
                message=f"Organization '{org_name}' deleted"
            )

            return Response({
                "message": "Organization deleted successfully"
            })

        except Organization.DoesNotExist:

            return Response({
                "error": "Organization not found"
            }, status=404)

class SuperAdminUpdateOrganizationView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request, org_id):

        if request.user.role != "SUPERADMIN":
            return Response({"error": "Access denied"}, status=403)

        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return Response({"error": "Organization not found"}, status=404)

        org_name = request.data.get("organization_name")
        hr_name = request.data.get("hr_name")
        hr_email = request.data.get("hr_email")

        if org_name:
            organization.name = org_name
            organization.save()

        # HR user find
        hr_user = User.objects.filter(
            role="HR",
            organization=organization
        ).first()

        if hr_user:

            if hr_name:
                hr_user.full_name = hr_name

            if hr_email:
                hr_user.email = hr_email

            hr_user.save()

        return Response({
            "message": "Organization updated successfully"
        })
    
class SuperAdminActivityView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        logs = ActivityLog.objects.order_by("-created_at")[:10]

        serializer = ActivityLogSerializer(logs, many=True)

        return Response(serializer.data)

class ExportMyPayrollCSV(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        year = request.GET.get("year")

        try:
            profile = request.user.employee_profile
        except:
            return HttpResponse("Employee profile not found", status=404)

        payrolls = Payroll.objects.filter(employee=profile)

        if year:
            payrolls = payrolls.filter(year=year)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="salary_slips_{year}.csv"'

        writer = csv.writer(response)

        # Header Row
        writer.writerow([
            "Month",
            "Year",
            "Base Salary",
            "Allowance",
            "Deduction",
            "Net Salary",
            "Status"
        ])

        # Data Rows
        for p in payrolls:
            writer.writerow([
                p.month,
                p.year,
                p.base_salary,
                p.allowance,
                p.deduction,
                p.net_salary,
                p.status
            ])

        return response

class DownloadMyPayrollZip(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        year = request.GET.get("year")

        try:
            profile = request.user.employee_profile
        except:
            return HttpResponse("Employee profile not found", status=404)

        payrolls = Payroll.objects.filter(
            employee=profile,
            status="PAID"
        )

        if year:
            payrolls = payrolls.filter(year=year)

        response = HttpResponse(content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="salary_slips_{year}.zip"'

        zip_file = zipfile.ZipFile(response, "w")

        for payroll in payrolls:

            if payroll.pdf_file and os.path.exists(payroll.pdf_file.path):

                zip_file.write(
                    payroll.pdf_file.path,
                    os.path.basename(payroll.pdf_file.path)
                )

        zip_file.close()


        return response
    
class EmployeeCheckInView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        profile = request.user.employee_profile
        today = timezone.localdate()

        now = timezone.localtime().time()

        attendance, created = Attendance.objects.get_or_create(
            employee=profile,
            date=today
        )

        if attendance.check_in:
            return Response({"message": "Already checked in today"})

        attendance.check_in = now

        # 🔥 STATUS LOGIC
        if now <= time(9, 0):
            attendance.status = "PRESENT"

        elif now <= time(10, 0):
            attendance.status = "LATE"

        else:
            attendance.status = "ABSENT"

        attendance.save()

        return Response({
            "message": "Check-in successful",
            "status": attendance.status
        })
    
class EmployeeCheckOutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        profile = request.user.employee_profile
        today = timezone.localdate()

        now = timezone.localtime().time()

        try:
            attendance = Attendance.objects.get(
                employee=profile,
                date=today
            )
        except Attendance.DoesNotExist:
            return Response({"message": "Please check-in first"}, status=400)

        if attendance.check_out:
            return Response({"message": "Already checked out"}, status=400)

        # ❌ BLOCK before 5 PM
        if now < time(17, 0):
            return Response({
                "message": "Cannot checkout before 5 PM"
            }, status=400)

        # ✅ ALLOW checkout
        attendance.check_out = now

        # 🔥 WORKING HOURS CALCULATION
        check_in_datetime = datetime.combine(today, attendance.check_in)
        check_out_datetime = datetime.combine(today, now)

        duration = check_out_datetime - check_in_datetime

        attendance.working_hours = str(duration)

        attendance.save()

        return Response({
            "message": "Checked out successfully",
            "working_hours": attendance.working_hours
        })
    
class MyAttendanceListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            profile = request.user.employee_profile
        except EmployeeProfile.DoesNotExist:
            return Response({"detail": "Employee profile not found"}, status=404)

        records = Attendance.objects.filter(
            employee=profile
        ).order_by("-date")

        data = []

        for r in records:
            data.append({
                "date": r.date,
                "check_in": r.check_in,
                "check_out": r.check_out,
                "status": r.status
            })

        return Response(data)

class HRAttendanceSummaryView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.user.role != "HR":
            return Response({"error": "Access denied"}, status=403)

        month = request.GET.get("month")
        year = request.GET.get("year")

        if not month or not year:
            return Response({"error": "month and year required"}, status=400)

        employees = EmployeeProfile.objects.filter(
            organization=request.user.organization
        )

        response_data = []

        for emp in employees:

            attendance_qs = Attendance.objects.filter(
                employee=emp,
                date__month=month,
                date__year=year
            )

            present = attendance_qs.filter(status="PRESENT").count()
            absent = attendance_qs.filter(status="ABSENT").count()
            late = attendance_qs.filter(status="LATE").count()

            # 🔥 MAIN LOGIC (Option B)
            effective_absent = absent + (late // 3)

            response_data.append({
                "employee_id": emp.id,
                "employee_name": emp.user.full_name,
                "present_days": present,
                "absent_days": absent,
                "late_days": late,
                "effective_absent": effective_absent
            })

        return Response(response_data)


class ApplyLeaveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:
            profile = request.user.employee_profile
        except Exception as e:
            return Response(
                {"error": "Employee profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = LeaveSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(employee=profile)
            return Response(
                {"message": "Leave applied successfully"},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

class HRManageLeaveView(APIView):
    permission_classes = [IsHR]

    def post(self, request, leave_id):

        action = request.data.get("action")

        leave = get_object_or_404(
            Leave,
            id=leave_id,
            employee__organization=request.user.organization
        )

        if leave.status != "PENDING":
            return Response(
                {"error": "Leave already processed"},
                status=400
            )

        employee = leave.employee  # 🔥 IMPORTANT

        if action == "APPROVE":

            # 🔥 Leave days calculate
            leave_days = (leave.end_date - leave.start_date).days + 1

            # 🔥 Balance check
            if employee.leave_balance >= leave_days:
                leave.leave_payment = "PAID"
                employee.leave_balance -= leave_days
            else:
                leave.leave_payment = "UNPAID"

            leave.status = "APPROVED"
            leave.approved_by = request.user
            leave.approved_at = timezone.now()

            employee.save()

        elif action == "REJECT":
            leave.status = "REJECTED"

        else:
            return Response({"error": "Invalid action"}, status=400)

        leave.save()

        return Response({
            "message": f"Leave {leave.status}"
        })

class MyLeaveSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.employee_profile

        leaves = Leave.objects.filter(employee=profile)

        total_taken = 0
        paid_days = 0
        unpaid_days = 0

        approved_leaves = leaves.filter(status="APPROVED")

        for leave in approved_leaves:
            days = (leave.end_date - leave.start_date).days + 1
            total_taken += days

            if leave.leave_payment == "PAID":
                paid_days += days
            else:
                unpaid_days += days

        remaining = profile.leave_balance

        deduction = unpaid_days * (profile.base_salary / 30)

        return Response({
            "total_taken": total_taken,
            "remaining": remaining,
            "salary_deduction": round(deduction, 2)
        })
    
class MyLeavesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.employee_profile

        leaves = Leave.objects.filter(employee=profile).order_by("-applied_at")

        serializer = LeaveSerializer(leaves, many=True)
        return Response(serializer.data)

class HRAllLeavesView(APIView):
    permission_classes = [IsHR]

    def get(self, request):
        leaves = Leave.objects.filter(
            employee__organization=request.user.organization
        ).order_by("-applied_at")

        serializer = LeaveSerializer(leaves, many=True)
        return Response(serializer.data)