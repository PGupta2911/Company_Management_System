"""
URL configuration for company_mgmt project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views import login_view, hr_dashboard_view, employee_dashboard_view,hr_employees_view,hr_payroll_view

urlpatterns = [
    path("admin/", admin.site.urls),

    path("login/", login_view, name="login"),
    path("hr/dashboard/", hr_dashboard_view, name="hr_dashboard"),
    path("hr/employees/", hr_employees_view, name="hr_employees"),
    path("employee/dashboard/", employee_dashboard_view, name="employee_dashboard"),
    path("hr/payrolls/", hr_payroll_view, name="hr_payrolls"),

    # JWT
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Accounts
    path("api/accounts/", include("accounts.urls")),
    path("api/core/", include("core.urls")),
]  + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)