from django.contrib import admin
from .models import EmployeeProfile, Organization, Payroll,Attendance,Leave

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "get_email", "position", "is_active", "created_at")
    search_fields = ("user__email", "position")
    list_filter = ("is_active", "position")

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = "Email"


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ("id", "employee", "month", "year", "status", "created_at")
    list_filter = ("status", "month", "year")
    search_fields = ("employee__user__email",)

admin.site.register(Attendance)
admin.site.register(Leave)