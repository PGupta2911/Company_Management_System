import { apiRequest } from "./api.js";
import { requireAuth, logout } from "./auth.js";

requireAuth();
document.getElementById("logoutBtn")?.addEventListener("click", logout);

// Elements
const payrollTable = document.getElementById("payrollTable");
const showGenerateBtn = document.getElementById("showGenerateBtn");
const closeGenerateBtn = document.getElementById("closeGenerateBtn");
const generateModal = document.getElementById("generateModal");
const generateForm = document.getElementById("generateForm");
const payEmployeeSelect = document.getElementById("payEmployee");

// ================= Load Payrolls =================
async function loadPayrolls() {
  payrollTable.innerHTML = `<tr><td colspan="7">Loading...</td></tr>`;

  try {
    const payrolls = await apiRequest("http://127.0.0.1:8000/api/core/payrolls/");

    payrollTable.innerHTML = "";

    if (!payrolls || payrolls.length === 0) {
      payrollTable.innerHTML = `<tr><td colspan="7">No payrolls found</td></tr>`;
      return;
    }

    payrolls.forEach((p) => {
      const tr = document.createElement("tr");

      tr.innerHTML = `
        <td>${p.id}</td>
        <td>${p.employee_email || "-"}</td>
        <td>${p.month}</td>
        <td>${p.year}</td>
        <td>${p.net_salary}</td>
        <td>${p.status}</td>
        <td>
          ${
            p.status !== "PAID"
              ? `<button class="markPaidBtn" data-id="${p.id}">Mark Paid</button>`
              : `<span class="badge badge-success">Paid</span>`
          }
        </td>
      `;

      payrollTable.appendChild(tr);
    });
  } catch (err) {
    console.error(err);
    payrollTable.innerHTML = `<tr><td colspan="7">Error loading payrolls</td></tr>`;
  }
}

// ================= Load Employees for Dropdown =================
async function loadEmployeesForDropdown() {
  try {
    const employees = await apiRequest("http://127.0.0.1:8000/api/core/employees/");

    payEmployeeSelect.innerHTML = `<option value="">Select Employee</option>`;

    employees.forEach((emp) => {
      const opt = document.createElement("option");
      opt.value = emp.id;
      opt.textContent = `${emp.user_email || emp.email || "Employee"} (${emp.id})`;
      payEmployeeSelect.appendChild(opt);
    });
  } catch (err) {
    console.error("Failed to load employees", err);
  }
}

// ================= Modal Logic =================
showGenerateBtn?.addEventListener("click", () => {
  generateModal.style.display = "flex";
  loadEmployeesForDropdown();
});

closeGenerateBtn?.addEventListener("click", () => {
  generateModal.style.display = "none";
  generateForm.reset();
});

// ================= Generate Payroll =================
generateForm?.addEventListener("submit", async (e) => {
  e.preventDefault();

  const payload = {
    employee_id: payEmployeeSelect.value,
    month: document.getElementById("payMonth").value,
    year: document.getElementById("payYear").value,
  };

  try {
    await apiRequest("http://127.0.0.1:8000/api/core/payrolls/generate/", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    alert("Payroll generated successfully");
    generateModal.style.display = "none";
    generateForm.reset();
    loadPayrolls();
  } catch (err) {
    console.error(err);
    alert("Failed to generate payroll");
  }
});

// ================= Table Actions (Mark Paid / Delete) =================
payrollTable?.addEventListener("click", async (e) => {
  const markBtn = e.target.closest(".markPaidBtn");
  const delBtn = e.target.closest(".deletePayrollBtn");

  // ---- Mark Paid ----
  if (markBtn) {
    const id = markBtn.getAttribute("data-id");

    if (!confirm("Mark this payroll as PAID?")) return;

    try {
      await apiRequest(`http://127.0.0.1:8000/api/core/payrolls/${id}/mark-paid/`, {
        method: "POST",
      });

      alert("Payroll marked as PAID");
      loadPayrolls();
    } catch (err) {
      console.error(err);
      alert("Failed to mark paid");
    }
  }

  // ---- Delete Payroll ----
  if (delBtn) {
    const id = delBtn.getAttribute("data-id");

    if (!confirm("Are you sure you want to delete this payroll?")) return;

    try {
      await apiRequest(`http://127.0.0.1:8000/api/core/payrolls/${id}/`, {
        method: "DELETE",
      });

      alert("Payroll deleted");
      loadPayrolls();
    } catch (err) {
      console.error(err);
      alert("Failed to delete payroll");
    }
  }
});

// ================= Initial Load =================
loadPayrolls();