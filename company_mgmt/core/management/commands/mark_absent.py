from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import time
from core.models import Attendance, EmployeeProfile

class Command(BaseCommand):

    help = "Mark absent for employees who didn't check in"

    def handle(self, *args, **kwargs):

        today = timezone.localdate()

        now = timezone.localtime().time()

        # Run only after 10:30 AM
        if now < time(10, 30):
            self.stdout.write("Too early to mark absent")
            return

        employees = EmployeeProfile.objects.all()

        for emp in employees:

            attendance, created = Attendance.objects.get_or_create(
                employee=emp,
                date=today
            )

            if not attendance.check_in:
                attendance.status = "ABSENT"
                attendance.save()

        self.stdout.write("Absent marked successfully")