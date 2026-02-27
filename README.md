# Company Management System

A role-based organization management system built using Django and Django REST Framework.  
It supports Admin and Employee roles, employee management, and payroll handling.

---

## 🚀 Features

- Role-based authentication (Admin & Employee)
- Separate dashboards for HR/Admin and Employee
- Employee management
- Secure login system
- Payroll management
- REST API based backend
- Frontend using HTML, CSS, JavaScript

---

## 🛠 Tech Stack

**Backend:**
- Python
- Django
- Django REST Framework

**Frontend:**
- HTML
- CSS
- JavaScript

**Database:**
- SQLite (can be changed later)

---

## ⚙️ Setup Instructions

Follow these steps to run the project locally:

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/company-management-system.git
cd company-management-system
2. Create virtual environment
python -m venv venv
venv\Scripts\activate   # On Windows
# source venv/bin/activate  # On Linux/Mac
3. Install dependencies
pip install -r requirements.txt
4. Run migrations
python manage.py makemigrations
python manage.py migrate
5. Create superuser
python manage.py createsuperuser
6. Run the server
python manage.py runserver

Open in browser:

http://127.0.0.1:8000/