from django.urls import path
from .views import (MyOrganizationView, HRCreateEmployeeView, HREmployeeListView, MyEmployeeProfileView,
                     HRGeneratePayrollView,HRPayrollListView,HRMarkPayrollPaidView,MyPayrollListView,
                     HRDeleteEmployeeView,HRDashboardStatsView,month_status_view)

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


]