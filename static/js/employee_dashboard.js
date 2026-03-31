import { apiRequest } from "./api.js";
import { requireAuth, logout } from "./auth.js";

requireAuth();
document.getElementById("logoutBtn")?.addEventListener("click", logout);

const payrollTable = document.getElementById("payrollTable");

const attendanceTable = document.getElementById("attendanceTable");


// =========================
// UPDATE DASHBOARD STATS
// =========================
function updateStats(payrolls) {

  const totalPayslips = payrolls.length;

  let totalEarned = 0;

  payrolls.forEach((p) => {
    totalEarned += parseFloat(p.net_salary);
  });

  document.getElementById("totalPayslips").innerText = totalPayslips;

  document.getElementById("totalEarned").innerText =
    "₹" + totalEarned.toFixed(2);

  if (payrolls.length > 0) {

    document.getElementById("lastSalary").innerText =
      "₹" + payrolls[0].net_salary;

    const highest = Math.max(...payrolls.map((p) => parseFloat(p.net_salary)));

    const avg = totalEarned / payrolls.length;

    document.getElementById("highestSalary").innerText =
      "₹" + highest.toFixed(2);

    document.getElementById("averageSalary").innerText =
      "₹" + avg.toFixed(2);

  } else {

    document.getElementById("lastSalary").innerText = "₹0";
    document.getElementById("highestSalary").innerText = "₹0";
    document.getElementById("averageSalary").innerText = "₹0";

  }

}


// =========================
// SALARY GRAPH
// =========================
let chartInstance = null;

function renderSalaryChart(payrolls) {

  const months = [];
  const salaries = [];

  payrolls
    .sort((a, b) => a.month - b.month)
    .forEach((p) => {
      months.push(`M${p.month}`);
      salaries.push(p.net_salary);
    });

  const ctx = document.getElementById("salaryChart");

  if (!ctx) return;

  if (chartInstance) {
    chartInstance.destroy();
  }

  chartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: months,
      datasets: [{
        label: "Salary",
        data: salaries,
        borderColor: "#2563eb",
        tension: 0.3
      }]
    }
  });
}


// =========================
// LOAD PAYROLL DATA
// =========================
async function loadMyPayrolls() {

  payrollTable.innerHTML = `<tr><td colspan="5">Loading...</td></tr>`;

  try {

    const year = document.getElementById("yearFilter")?.value;

    const payrolls = await apiRequest(
      `http://127.0.0.1:8000/api/core/payrolls/me/?year=${year}`
    );

    updateStats(payrolls);
    renderSalaryChart(payrolls);

    payrollTable.innerHTML = "";

    if (!payrolls || payrolls.length === 0) {
      payrollTable.innerHTML =
        `<tr><td colspan="5">No payrolls found</td></tr>`;
      return;
    }

    payrolls.forEach((p) => {

      const tr = document.createElement("tr");

      tr.innerHTML = `
        <td>${p.month}</td>
        <td>${p.year}</td>
        <td>${p.net_salary}</td>
        <td>
          <span class="status-badge ${p.status}">
            ${p.status}
          </span>
        </td>
        <td>
          ${
            p.status === "PAID" && p.pdf_file
              ? `<a href="${p.pdf_file}" target="_blank" class="btn-view">
                   View Slip
                 </a>`
              : `<span>Not available</span>`
          }
        </td>
      `;

      payrollTable.appendChild(tr);

    });

  } catch (err) {

    console.error(err);

    payrollTable.innerHTML =
      `<tr><td colspan="5">Error loading payrolls</td></tr>`;

  }

}


// =========================
// YEAR FILTER
// =========================
document
  .getElementById("yearFilter")
  ?.addEventListener("change", loadMyPayrolls);


// =========================
// EXPORT CSV
// =========================
document
  .getElementById("exportCSV")
  ?.addEventListener("click", async () => {

    const year = document.getElementById("yearFilter")?.value;
    const token = localStorage.getItem("access");

    const response = await fetch(
      `http://127.0.0.1:8000/api/core/payrolls/export/?year=${year}`,
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    );

    const blob = await response.blob();

    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `salary_slips_${year}.csv`;

    document.body.appendChild(a);
    a.click();

    a.remove();

  });


// =========================
// DOWNLOAD ZIP
// =========================
document
  .getElementById("downloadZIP")
  ?.addEventListener("click", async () => {

    const year = document.getElementById("yearFilter")?.value;
    const token = localStorage.getItem("access");

    const response = await fetch(
      `http://127.0.0.1:8000/api/core/payrolls/download-zip/?year=${year}`,
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    );

    const blob = await response.blob();

    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `salary_slips_${year}.zip`;

    document.body.appendChild(a);
    a.click();

    a.remove();

  });

  function formatTime(timeStr){

  if(!timeStr) return "-";

  const parts = timeStr.split(":");

  return parts[0] + ":" + parts[1];

}

  async function loadAttendance() {

  if (!attendanceTable) return;

  attendanceTable.innerHTML = `<tr><td colspan="4">Loading...</td></tr>`;

  try {

    const records = await apiRequest(
      "http://127.0.0.1:8000/api/core/attendance/me/"
    );

    attendanceTable.innerHTML = "";

    if (!records || records.length === 0) {
      attendanceTable.innerHTML =
        `<tr><td colspan="4">No attendance found</td></tr>`;
      return;
    }

    records.forEach((r) => {

      const tr = document.createElement("tr");

      tr.innerHTML = `
      <td>${r.date}</td>
      <td>${formatTime(r.check_in)}</td>
      <td>${formatTime(r.check_out)}</td>
      <td>${r.working_hours || "-"}</td>
      <td><span class="status-badge ${r.status}">${r.status}</span></td>
      `;

      attendanceTable.appendChild(tr);

    });

  } catch (err) {

    console.error(err);

    attendanceTable.innerHTML =
      `<tr><td colspan="4">Error loading attendance</td></tr>`;

  }

}

document
  .getElementById("checkInBtn")
  ?.addEventListener("click", async () => {

    try {

      const res = await apiRequest(
        "http://127.0.0.1:8000/api/core/attendance/check-in/",
        {
          method: "POST"
        }
      );

      alert(res.message);
      loadAttendance();

    } catch (err) {
      console.error(err);
      alert("Check-in failed");
    }

  });

  document
  .getElementById("checkOutBtn")
  ?.addEventListener("click", async () => {

    try {

      const res = await apiRequest(
        "http://127.0.0.1:8000/api/core/attendance/check-out/",
        {
          method: "POST"
        }
      );

      alert(res.message);
      loadAttendance();

    } catch (err) {
      console.error(err);
      alert("Check-out failed");
    }

  });

  document.getElementById("leavePageBtn").addEventListener("click", () => {
    window.location.href = "/employee/leave/";
});


// =========================
// INITIAL LOAD
// =========================
loadMyPayrolls();
loadAttendance();