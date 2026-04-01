# 🚀 Company Management System (Django + REST API)
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/eda9a5a6-629f-4f22-85f9-a968af810083" />


A full-stack **Role-Based Company Management & Payroll System** built using **Django and Django REST Framework**.

This system helps organizations manage employees, payroll, attendance, and administrative workflows with **automation, role-based access, and analytics dashboards**.

---

## 🔥 Key Highlights

- 🧑‍💼 Multi-role system (Superadmin, HR, Employee)
- 🏢 Multi-organization management
- 💰 Automated payroll system
- 📄 Salary slip PDF generation
- 📊 Analytics dashboard with charts
- 📦 Payroll export (CSV + ZIP)
- ⚡ REST API based backend
- 🔐 JWT Authentication & role-based access

---

## 👥 User Roles & Responsibilities

### 🟣 Superadmin
- Create and manage multiple organizations
- Create HR accounts for each organization
- Monitor overall system structure

### 🔵 HR
- Add / update / manage employees
- Generate payroll for employees
- Mark payroll as Paid / Pending
- Manage attendance and leave records
- Access HR dashboard insights

### 🟢 Employee
- View salary slips
- Download PDF payslips
- Filter payroll by year
- View salary analytics

---

## 🏢 Organization Management

- Multi-organization support
- Each organization has its own HR and employees
- Scalable structure for real-world company usage

- <img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/53f2c3ed-73dc-4194-b081-28027b58ccf9" />
> Displays all organizations with HR and employee count.

<img width="1048" height="298" alt="image" src="https://github.com/user-attachments/assets/c965c990-035f-46bd-a716-5fb86b40e9aa" />
> Shows detailed structure of a single organization including employees and payroll data.




---

## 👨‍💼 Employee Management

- Add / update / delete employees
- Assign employees to specific organizations
- Manage employee salary and details

---

## 💰 Payroll Management System

- Generate payroll for selected month/year
- Mark payroll as **Paid / Pending**
- Track payroll history

### ⚡ Automation:
When payroll is marked as **Paid**:
- Salary slip PDF is generated automatically
- File is stored in media folder
- Available instantly to employee

---

## 📄 Salary Slip System

- Auto PDF generation
- Downloadable from dashboard
- Stored securely in media storage

---

## 📊 Analytics Dashboard

- Total salary earned
- Total payslips generated
- Highest salary
- Average salary
- Salary growth chart (Chart.js)

---

## 📦 Export Features

- CSV export of payroll data
- ZIP download of salary slips (year-wise)

---

## 📅 Attendance & Leave Management

- Attendance tracking system
- Auto marking absent (via backend logic)
- Leave request & approval system

---

## 🛠️ Tech Stack

### Backend
- Python
- Django
- Django REST Framework
- JWT Authentication

### Frontend
- HTML
- CSS
- JavaScript
- Chart.js

### Database
- SQLite (Development)
- Scalable to PostgreSQL / MySQL

---

## 📂 Project Structure


company_management/
│── company_mgmt/
│── core/
│── frontend/
│── static/
│── manage.py


---

## ⚙️ Setup Instructions

### 1. Clone Repository
```bash
git clone https://github.com/PGupta2911/Company_Management_System.git
cd Company_Management_System
2. Create Virtual Environment
python -m venv venv
venv\Scripts\activate  # Windows
3. Install Dependencies
pip install -r requirements.txt
4. Run Migrations
python manage.py makemigrations
python manage.py migrate
5. Create Superuser
python manage.py createsuperuser
6. Run Server
python manage.py runserver

Open:
http://127.0.0.1:8000

🔮 Future Improvements
Email salary slips to employees
Background job processing (Celery)
API documentation (Swagger)
Advanced analytics dashboard
Notification system
🎯 Key Learnings
Built scalable backend systems using Django
Implemented real-world payroll automation
Designed role-based access control
Integrated backend APIs with frontend dashboards
Worked with file handling (PDF, ZIP, CSV)
👨‍💻 Author

Priyanshu Gupta
B.Tech CSE (AI & ML)
Python | Django | Backend Development | Machine Learning
