import { apiRequest } from "./api.js";
import { requireAuth, logout } from "./auth.js";

requireAuth();

document.getElementById("logoutBtn").addEventListener("click", logout);

// ===== Load Employees =====
async function loadEmployees() {
  const tbody = document.getElementById("employeeTable");
  tbody.innerHTML = "<tr><td colspan='4'>Loading...</td></tr>";

  try {
    const employees = await apiRequest("http://127.0.0.1:8000/api/core/employees/");

    tbody.innerHTML = "";

    if (!employees || employees.length === 0) {
      tbody.innerHTML = "<tr><td colspan='4'>No employees found</td></tr>";
      return;
    }

    employees.forEach(emp => {
      const tr = document.createElement("tr");

      tr.innerHTML = `
        <td>${emp.id}</td>
        <td>${emp.full_name || ""}</td>
        <td>${emp.user_email || ""}</td>
        <td>
          <button data-id="${emp.id}" class="deleteBtn">Delete</button>
        </td>
      `;

      tbody.appendChild(tr);
    });

    // attach delete handlers
    document.getElementById("employeeTable").addEventListener("click", async (e) => {
        if (e.target.classList.contains("deleteBtn")) {
            const id = e.target.getAttribute("data-id");

            if (!confirm("Are you sure you want to delete this employee?")) return;

            try {
            await apiRequest(`http://127.0.0.1:8000/api/core/employees/${id}/`, {
                method: "DELETE",
            });

            alert("Employee deleted successfully");
            loadEmployees(); // refresh table
            } catch (err) {
            console.error(err);
            alert("Failed to delete employee");
            }
        }
    });

  } catch (err) {
    console.error(err);
    tbody.innerHTML = "<tr><td colspan='4'>Error loading employees</td></tr>";
  }
}

// ===== Modal Logic =====
const modal = document.getElementById("employeeModal");
const showBtn = document.getElementById("showAddEmployeeBtn");
const closeBtn = document.getElementById("closeModalBtn");
const addForm = document.getElementById("addEmployeeForm");

showBtn.addEventListener("click", () => {
  modal.style.display = "flex";
});

closeBtn.addEventListener("click", () => {
  modal.style.display = "none";
  addForm.reset();
});

// ===== Add Employee =====
addForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const payload = {
    email: document.getElementById("empEmail").value,        // ✅ REQUIRED
    password: document.getElementById("empPassword").value, // ✅ REQUIRED (new input)

    full_name: document.getElementById("empFullName").value,
    position: document.getElementById("empPosition").value,
    base_salary: document.getElementById("empBaseSalary").value,
    allowance: document.getElementById("empAllowance").value || 0,
    deduction: document.getElementById("empDeduction").value || 0,
  };

  try {
    await apiRequest("http://127.0.0.1:8000/api/core/employees/create/", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    alert("Employee added successfully");
    modal.style.display = "none";
    addForm.reset();
    loadEmployees();

  } catch (err) {
    console.error(err);
    alert("Failed to add employee");
  }
});

// initial load
loadEmployees();