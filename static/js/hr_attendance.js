import { apiRequest } from "./api.js";
import { requireAuth, logout } from "./auth.js";

requireAuth();

document.getElementById("logoutBtn")?.addEventListener("click", logout);

const table = document.getElementById("attendanceTable");

// ================= LOAD =================
async function loadAttendance() {

  const month = document.getElementById("monthSelect").value;
  const year = document.getElementById("yearSelect").value;

  table.innerHTML = `<tr><td colspan="5">Loading...</td></tr>`;

  try {

    const data = await apiRequest(
      `/api/core/attendance/hr-summary/?month=${month}&year=${year}`
    );

    table.innerHTML = "";

    if (!data || data.length === 0) {
      table.innerHTML = `<tr><td colspan="5">No data</td></tr>`;
      return;
    }

    data.forEach(emp => {

      const tr = document.createElement("tr");

      // highlight logic
      const highAbsent = emp.effective_absent > 5 ? "high-absent" : "";
      const lowPresent = emp.present_days < 5 ? "low-present" : "";

      tr.innerHTML = `
        <td>${emp.employee_name || "N/A"}</td>
        <td class="${lowPresent}">${emp.present_days}</td>
        <td>${emp.late_days}</td>
        <td>${emp.absent_days}</td>
        <td class="${highAbsent}"><strong>${emp.effective_absent}</strong></td>
      `;

      table.appendChild(tr);

    });

  } catch (err) {
    console.error(err);
    table.innerHTML = `<tr><td colspan="5">Error loading data</td></tr>`;
  }
}

// ================= EVENTS =================
document.getElementById("loadAttendanceBtn")
  ?.addEventListener("click", loadAttendance);

// auto load on page open
window.onload = loadAttendance;