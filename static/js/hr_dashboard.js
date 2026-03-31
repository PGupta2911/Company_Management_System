import { apiRequest } from "/static/js/api.js";
import { requireAuth, logout } from "/static/js/auth.js";

requireAuth();

document.getElementById("logoutBtn").addEventListener("click", logout);

// Load basic user + org + employee count
async function loadData() {
    try {
        const me = await apiRequest("http://127.0.0.1:8000/api/accounts/me/");
        document.getElementById("userInfo").innerText = `${me.email} (${me.role})`;

        const org = await apiRequest("http://127.0.0.1:8000/api/core/my-organization/");
        console.log(org);
        document.getElementById("orgName").innerText = org.name;

        const employees = await apiRequest("http://127.0.0.1:8000/api/core/employees/");
        document.getElementById("TotalEmployees").innerText = employees.length;
    } catch (err) {
        console.error("Error loading base data:", err);
    }
}

// Load dashboard stats (pending payrolls)
async function loadDashboardStats() {
    try {
        const data = await apiRequest("http://127.0.0.1:8000/api/core/dashboard/stats/");
        document.getElementById("pendingPayrolls").innerText = data.pending_payrolls;
    } catch (err) {
        console.error("Error loading dashboard stats:", err);
        document.getElementById("pendingPayrolls").innerText = "Error";
    }
}

// Initial load
loadDashboardStats();
loadData();