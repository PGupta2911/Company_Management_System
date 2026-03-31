from django.urls import path
from .views import (MyOrganizationView, HRCreateEmployeeView, HREmployeeListView, MyEmployeeProfileView,
                     HRGeneratePayrollView,HRPayrollListView,HRMarkPayrollPaidView,MyPayrollListView,
                     HRDeleteEmployeeView,HRDashboardStatsView,month_status_view,SuperAdminDashboardStatsView,
                     SuperAdminCreateOrganizationView,SuperAdminOrganizationListView,
                     SuperAdminOrganizationDetailView, SuperAdminOrganizationEmployeesView,
                     SuperAdminOrganizationPayrollsView,SuperAdminDeleteOrganizationView,
                     SuperAdminUpdateOrganizationView,SuperAdminActivityView,ExportMyPayrollCSV,EmployeeCheckInView, 
                     EmployeeCheckOutView, MyAttendanceListView,HRAttendanceSummaryView,ApplyLeaveView,
                     HRManageLeaveView,MyLeaveSummaryView,MyLeavesView,HRAllLeavesView)

urlpatterns = [
    path("my-organization/", MyOrganizationView.as_view(), name="my-organization"),

    # Employee APIs
    path("employees/", HREmployeeListView.as_view(), name="hr-employee-list"),
    path("employees/create/", HRCreateEmployeeView.as_view(), name="hr-employee-create"),
    path("employees/me/", MyEmployeeProfileView.as_view(), name="employee-me"),
    path("employees/<int:employee_id>/", HRDeleteEmployeeView.as_view(), name="hr-employee-delete"),

    # Payroll
    path("payrolls/generate/", HRGeneratePayrollView.as_view(), name="hr-generate-payroll"),
    path("payrolls/", HRPayrollListView.as_view(), name="hr-payroll-list"),
    path("payrolls/<int:payroll_id>/mark-paid/", HRMarkPayrollPaidView.as_view(), name="hr-mark-paid"),
    path("payrolls/me/", MyPayrollListView.as_view(), name="employee-payroll-list"),
    path("dashboard/stats/", HRDashboardStatsView.as_view(), name="hr-dashboard-stats"),
    path('month-status/', month_status_view, name='month_status'),

    #Super-Admin
    path("superadmin/dashboard/stats/",SuperAdminDashboardStatsView.as_view(),name="superadmin-dashboard-stats"),
    path("superadmin/organizations/create/",SuperAdminCreateOrganizationView.as_view(),name="superadmin-create-organization"),
    path("superadmin/organizations/",SuperAdminOrganizationListView.as_view(), name="superadmin-organizations"),
    path("superadmin/organizations/<int:org_id>/",SuperAdminOrganizationDetailView.as_view(),name="superadmin-organization-detail"),
    path("superadmin/organizations/<int:org_id>/employees/",SuperAdminOrganizationEmployeesView.as_view()),
    path("superadmin/organizations/<int:org_id>/payrolls/",SuperAdminOrganizationPayrollsView.as_view()),
    path("superadmin/organizations/<int:org_id>/delete/",SuperAdminDeleteOrganizationView.as_view()),
    path("superadmin/organizations/<int:org_id>/update/",SuperAdminUpdateOrganizationView.as_view()),
    path("payrolls/export/", ExportMyPayrollCSV.as_view()),

    path("superadmin/activity/",SuperAdminActivityView.as_view()),
    path("payrolls/export/", ExportMyPayrollCSV.as_view()),

    #Attadence 
    
    path("attendance/check-in/", EmployeeCheckInView.as_view()),
    path("attendance/check-out/", EmployeeCheckOutView.as_view()),
    path("attendance/me/", MyAttendanceListView.as_view()),
    path("attendance/hr-summary/", HRAttendanceSummaryView.as_view()),

    #Leave Management
    path("leaves/apply/", ApplyLeaveView.as_view(), name="apply-leave"),
    path("leaves/<int:leave_id>/manage/", HRManageLeaveView.as_view(), name="manage_leave"),
    path("leaves/summary/", MyLeaveSummaryView.as_view()),
    path("leaves/my/",MyLeavesView.as_view()),
    path("leaves/all/",HRAllLeavesView.as_view())
]