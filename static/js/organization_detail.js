const token = localStorage.getItem("access");

if (!token) {

    window.location = "/login/";

}


/* LOGOUT */

document.getElementById("logoutBtn")
.addEventListener("click", () => {

    localStorage.removeItem("access");
    localStorage.removeItem("refresh");

    window.location = "/login/";

});


/* GET ORG ID */

const pathParts = window.location.pathname.split("/");

const orgId = pathParts[pathParts.length - 2];


/* LOAD ORGANIZATION */

async function loadOrganization() {

    const res = await fetch(`/api/core/superadmin/organizations/${orgId}/`, {

        headers: {
            "Authorization": "Bearer " + token
        }

    });

    if (!res.ok) {

        alert("Organization not found");
        return;

    }

    const data = await res.json();

    document.getElementById("org_name").innerText =
        data.name || "Organization";

    document.getElementById("hr_name").innerText =
        data.hr_name || "No HR";

    document.getElementById("hr_email").innerText =
        data.hr_email || "-";

    document.getElementById("employee_count").innerText =
        data.employees || 0;

    document.getElementById("payroll_count").innerText =
        data.payrolls || 0;

}


/* LOAD EMPLOYEES */

async function loadEmployees() {

    const res = await fetch(`/api/core/superadmin/organizations/${orgId}/employees/`, {

        headers: {
            "Authorization": "Bearer " + token
        }

    });

    const employees = await res.json();

    const table = document.getElementById("employee_table");

    table.innerHTML = "";

    if (!employees.length) {

        table.innerHTML = `
        <tr>
            <td colspan="2">No employees</td>
        </tr>
        `;

        return;

    }

    employees.forEach(emp => {

        table.innerHTML += `

        <tr>

            <td>${emp.full_name}</td>
            <td>${emp.email}</td>

        </tr>

        `;

    });

}


/* LOAD PAYROLLS */

async function loadPayrolls() {

    const res = await fetch(`/api/core/superadmin/organizations/${orgId}/payrolls/`, {

        headers: {
            "Authorization": "Bearer " + token
        }

    });

    const payrolls = await res.json();

    const table = document.getElementById("payroll_table");

    table.innerHTML = "";

    if (!payrolls.length) {

        table.innerHTML = `
        <tr>
            <td colspan="4">No payrolls</td>
        </tr>
        `;

        return;

    }

    payrolls.forEach(pay => {

        table.innerHTML += `

        <tr>

            <td>${pay.month}</td>
            <td>${pay.year}</td>
            <td>${pay.net_salary}</td>
            <td>${pay.status}</td>

        </tr>

        `;

    });

}


/* INIT */

loadOrganization();

loadEmployees();

loadPayrolls();