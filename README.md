# Company Management System

A **Role-Based Company Management System** built using **Django and Django REST Framework**.

This system allows organizations to manage employees, HR operations, and payroll processes efficiently.

The application supports **Admin and Employee roles**, employee management, payroll generation, and salary slip handling.

---

## Features

### Authentication & Roles
- Secure login system
- Role-based authentication (Admin / HR / Employee)
- Separate dashboards for HR/Admin and Employees

### Employee Management
- Add new employees
- Update employee details
- View employee list
- Role based employee access

### HR Dashboard
- HR/Admin dashboard with employee statistics
- Employee overview and management tools

### Payroll Management
- Generate payroll for employees
- Mark salary as **Paid / Unpaid**
- Automatic payroll status tracking

### Salary Slip Generation
- Salary slip PDF generated for employees
- Salary slips stored in the system
- Employees can view their salary slips

---

## Tech Stack

### Backend
- Python
- Django
- Django REST Framework

### Frontend
- HTML
- CSS
- JavaScript

### Database
- SQLite (can be replaced with PostgreSQL/MySQL later)

---

## Payroll Flow

1. HR/Admin opens the **Payroll Management Page**
2. HR selects the employee payroll
3. HR clicks **Mark as Paid**
4. System automatically:
   - Updates payroll status
   - Generates **Salary Slip PDF**
   - Saves the PDF in the media folder
5. Employee can view salary slip from the system

---

## Setup Instructions

### 1. Clone the repository

```
git clone https://github.com/PGupta2911/Company_Management_System.git
cd Company_Management_System
```

### 2. Create virtual environment

```
python -m venv venv
```

### Activate environment

Windows

```
venv\Scripts\activate
```

Linux / Mac

```
source venv/bin/activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Run migrations

```
python manage.py makemigrations
python manage.py migrate
```

### 5. Create superuser

```
python manage.py createsuperuser
```

### 6. Run the server

```
python manage.py runserver
```

Open in browser:

```
http://127.0.0.1:8000
```

---

## Future Improvements

- Email salary slips to employees
- PostgreSQL database integration
- API documentation
- Dashboard analytics
- Notification system

---

## Author

**Priyanshu Gupta**

B.Tech Computer Science Engineering (AI & ML)

Python | Django | Machine Learning | NLP

GitHub  
https://github.com/PGupta2911