// ===== CONFIG =====
const API_BASE = "/api/core";
const CURRENT_YEAR = new Date().getFullYear();

let selectedMonth = null;
let selectedMonthName = null;


// ===== AUTH HEADER =====
function authHeader() {
    const token = localStorage.getItem("access");
    return {
        "Authorization": `Bearer ${token}`
    };
}


// ===== LOAD MONTH CARDS =====
async function loadMonthCards() {
    try {
        const response = await fetch(`${API_BASE}/month-status/`, {
            headers: authHeader()
        });

        if (!response.ok) {
            console.error("Failed to load month status");
            return;
        }

        const months = await response.json();
        const container = document.getElementById("month-cards");
        container.innerHTML = "";

        months.forEach(month => {

            const card = document.createElement("div");
            card.classList.add("month-card");

            card.innerHTML = `
                <h4>${month.month_name}</h4>
                <p>${month.status.toUpperCase()}</p>
            `;

            // Status styling
            if (month.status === "paid") {
                card.classList.add("paid");
            } else if (month.status === "unpaid") {
                card.classList.add("unpaid");
            } else {
                card.classList.add("locked");
            }

            // Make ALL non-locked months clickable
            if (month.status !== "locked") {
                card.onclick = () => {
                    selectedMonth = month.month_number;
                    selectedMonthName = month.month_name;

                    document.querySelectorAll(".month-card")
                        .forEach(c => c.classList.remove("active"));

                    card.classList.add("active");

                    loadPayrollsForMonth(selectedMonth, selectedMonthName);
                };
            }

            container.appendChild(card);
        });

    } catch (error) {
        console.error("Month load error:", error);
    }
}


// ===== LOAD PAYROLLS FOR MONTH =====
async function loadPayrollsForMonth(month, monthName) {

    document.getElementById("selected-month-title").innerText =
        `Employee List - ${monthName}`;

    try {
        const response = await fetch(
            `${API_BASE}/payrolls/?month=${month}&year=${CURRENT_YEAR}`,
            { headers: authHeader() }
        );

        if (!response.ok) {
            console.error("Payroll fetch failed");
            return;
        }

        const data = await response.json();
        renderEmployeeTable(data);

    } catch (error) {
        console.error("Payroll load error:", error);
    }
}


// ===== RENDER TABLE =====
function renderEmployeeTable(data) {

    const tableBody = document.getElementById("employee-table-body");
    tableBody.innerHTML = "";

    if (!data.length) {
        tableBody.innerHTML =
            `<tr><td colspan="3">No employees found</td></tr>`;
        return;
    }

    data.forEach(emp => {

        const row = document.createElement("tr");
        row.dataset.status = emp.status;

        let actionHtml = "";

        if (!emp.payroll_id) {
            actionHtml = `
                <button class="btn-generate"
                    onclick="generatePayroll(${emp.employee_id})">
                    Generate Slip
                </button>
            `;
        }
        else if (emp.status === "PENDING") {
            actionHtml = `
                <button class="btn-mark"
                    onclick="markAsPaid(${emp.payroll_id})">
                    Mark Paid
                </button>
            `;
        }
        else if (emp.status === "PAID") {
            actionHtml = `
                <a href="${emp.pdf_file}"
                   target="_blank"
                   class="btn-view">
                   View Slip
                </a>
            `;
        }

        row.innerHTML = `
            <td>${emp.employee_name}</td>
            <td>
                <span class="status-badge ${emp.status}">
                    ${emp.status}
                </span>
            </td>
            <td>${actionHtml}</td>
        `;

        tableBody.appendChild(row);
    });
}


// ===== GENERATE PAYROLL =====
async function generatePayroll(employeeId) {

    try {
        const response = await fetch(
            `${API_BASE}/payrolls/generate/`,
            {
                method: "POST",
                headers: {
                    ...authHeader(),
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    employee_id: employeeId,
                    month: selectedMonth,
                    year: CURRENT_YEAR
                })
            }
        );

        const result = await response.json();
        alert(result.detail || "Payroll generated");

        loadPayrollsForMonth(selectedMonth, selectedMonthName);
        loadMonthCards();

    } catch (error) {
        console.error("Generate error:", error);
    }
}


// ===== MARK AS PAID =====
async function markAsPaid(payrollId) {

    try {
        const response = await fetch(
            `${API_BASE}/payrolls/${payrollId}/mark-paid/`,
            {
                method: "POST",
                headers: authHeader()
            }
        );

        const result = await response.json();
        alert(result.message || "Marked as paid");

        loadPayrollsForMonth(selectedMonth, selectedMonthName);
        loadMonthCards();

    } catch (error) {
        console.error("Mark paid error:", error);
    }
}


// ===== FILTER =====
function filterEmployees(type) {

    const rows = document.querySelectorAll("#employee-table-body tr");

    rows.forEach(row => {

        const status = row.dataset.status;

        if (type === "ALL") {
            row.style.display = "";
        }
        else if (status && status.toUpperCase() === type.toUpperCase()) {
            row.style.display = "";
        }
        else {
            row.style.display = "none";
        }

    });
}


// ===== GENERATE ALL UNPAID =====
async function generateAllUnpaid() {

    if (!selectedMonth) {
        alert("Select a month first");
        return;
    }

    const rows = document.querySelectorAll("#employee-table-body tr");

    for (const row of rows) {
        if (row.dataset.status === "UNPAID") {
            const btn = row.querySelector(".btn-generate");
            if (btn) btn.click();
        }
    }
}


// ===== INIT =====
document.addEventListener("DOMContentLoaded", loadMonthCards);


// expose globally
window.filterEmployees = filterEmployees;
window.generateAllUnpaid = generateAllUnpaid;
window.markAsPaid = markAsPaid;
window.generatePayroll = generatePayroll;