from rest_framework import serializers
from .models import Organization, EmployeeProfile,Payroll,ActivityLog,Leave
from django.utils.timesince import timesince
from django.contrib.auth import get_user_model



User = get_user_model()


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "created_at"]


class EmployeeCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField()
    position = serializers.CharField()
    base_salary = serializers.DecimalField(max_digits=10, decimal_places=2)
    allowance = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    deduction = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)

    def create(self, validated_data):
        request = self.context["request"]
        org = request.user.organization  # HR ki organization

        email = validated_data.pop("email")
        password = validated_data.pop("password")
        full_name = validated_data.pop("full_name")

        # 1. Create User
        user = User.objects.create_user(
            email=email,
            password=password,
            role="EMPLOYEE",
            full_name=full_name,
        )
        user.organization = org
        user.save()

        # 2. Create EmployeeProfile
        profile = EmployeeProfile.objects.create(
            user=user,
            organization=org,
            **validated_data
        )

        return profile


class EmployeeProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = [
            "id",
            "user_email",
            "full_name",
            "position",
            "base_salary",
            "allowance",
            "deduction",
            "is_active",
            "created_at",
        ]





class PayrollSerializer(serializers.ModelSerializer):
    employee_email = serializers.EmailField(source="employee.user.email", read_only=True)
    username = serializers.CharField(source="employee.user.username", read_only=True)
    pdf_file = serializers.SerializerMethodField()

    class Meta:
        model = Payroll
        fields = [
            "id",
            "employee",
            "employee_email",
            "username",
            "month",
            "year",
            "base_salary",
            "allowance",
            "deduction",
            "net_salary",
            "status",
            "created_at",
            "pdf_file",
        ]
        read_only_fields = ["net_salary", "status", "created_at", "pdf_file"]

    def get_pdf_file(self, obj):
        if obj.pdf_file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
            return obj.pdf_file.url
        return None

class SuperAdminCreateOrganizationSerializer(serializers.Serializer):

    organization_name = serializers.CharField(max_length=255)
    hr_email = serializers.EmailField()
    hr_full_name = serializers.CharField(max_length=255)
    hr_password = serializers.CharField(write_only=True)

class SuperAdminOrganizationListSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    name = serializers.CharField()
    hr_name = serializers.CharField()
    employees = serializers.IntegerField()
    created_at = serializers.DateTimeField()

class SuperAdminOrganizationDetailSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    name = serializers.CharField()
    hr_name = serializers.CharField()
    hr_email = serializers.EmailField()
    employees = serializers.IntegerField()
    payrolls = serializers.IntegerField()
    created_at = serializers.DateTimeField()

class ActivityLogSerializer(serializers.ModelSerializer):

    time_ago = serializers.SerializerMethodField()
    user_name = serializers.CharField(source="user.full_name", default="System")

    class Meta:
        model = ActivityLog
        fields = ["action","message","user_name","time_ago"]

    def get_time_ago(self,obj):
        return timesince(obj.created_at) + " ago"

class LeaveSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.user.full_name", read_only=True)

    class Meta:
        model = Leave
        fields = [
            "id",
            "employee_name",
            "leave_type",
            "leave_payment",
            "start_date",
            "end_date",
            "status",
            "reason",
            "applied_at"
        ]