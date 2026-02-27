import { apiRequest } from "./api.js";
import { requireAuth, logout } from "./auth.js";

requireAuth();
document.getElementById("logoutBtn")?.addEventListener("click", logout);

const payrollTable = document.getElementById("payrollTable");

async function loadMyPayrolls() {
  payrollTable.innerHTML = `<tr><td colspan="5">Loading...</td></tr>`;

  try {
    const payrolls = await apiRequest("http://127.0.0.1:8000/api/core/payrolls/me/");

    payrollTable.innerHTML = "";

    if (!payrolls || payrolls.length === 0) {
      payrollTable.innerHTML = `<tr><td colspan="5">No payrolls found</td></tr>`;
      return;
    }

    payrolls.forEach((p) => {
      const tr = document.createElement("tr");

      tr.innerHTML = `
        <td>${p.month}</td>
        <td>${p.year}</td>
        <td>${p.net_salary}</td>
        <td>${p.status}</td>
        <td>
          ${
            p.status === "PAID" && p.pdf_file
              ? `<a href="${p.pdf_file}" target="_blank">View PDF</a>`
              : `<span>Not available</span>`
          }
        </td>
      `;

      payrollTable.appendChild(tr);
    });
  } catch (err) {
    console.error(err);
    payrollTable.innerHTML = `<tr><td colspan="5">Error loading payrolls</td></tr>`;
  }
}

// Initial load
loadMyPayrolls();