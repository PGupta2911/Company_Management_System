from calendar import monthrange
from datetime import date
from core.models import Attendance, Leave


def calculate_salary(employee, month, year):

    total_days = monthrange(int(year), int(month))[1]

    attendance_qs = Attendance.objects.filter(
        employee=employee,
        date__month=month,
        date__year=year
    )

    present = attendance_qs.filter(status="PRESENT").count()
    absent = attendance_qs.filter(status="ABSENT").count()
    late = attendance_qs.filter(status="LATE").count()

    # 🔥 Fetch approved leaves (overlapping safe)
    approved_leaves = Leave.objects.filter(
        employee=employee,
        start_date__lte=date(year, month, total_days),
        end_date__gte=date(year, month, 1),
        status="APPROVED"
    )

    paid_leave_days = 0
    unpaid_leave_days = 0

    for leave in approved_leaves:
        days = (leave.end_date - leave.start_date).days + 1

        if leave.leave_payment == "PAID":
            paid_leave_days += days
        else:
            unpaid_leave_days += days

    # 🔥 Late penalty
    late_penalty = late // 3

    # 🔥 FINAL EFFECTIVE ABSENT
    effective_absent = absent + late_penalty + unpaid_leave_days

    # safeguard
    if effective_absent < 0:
        effective_absent = 0

    # 🔥 Salary calculation
    payable_days = total_days - effective_absent

    per_day_salary = employee.base_salary / total_days

    calculated_salary = per_day_salary * payable_days

    net_salary = calculated_salary + employee.allowance - employee.deduction

    return {
        "total_days": total_days,
        "present": present,
        "absent": absent,
        "late": late,
        "paid_leave_days": paid_leave_days,
        "unpaid_leave_days": unpaid_leave_days,
        "effective_absent": effective_absent,
        "net_salary": round(net_salary, 2)
    }