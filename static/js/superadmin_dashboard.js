document.addEventListener("DOMContentLoaded", () => {

const token = localStorage.getItem("access");

if (!token) {
    window.location = "/login/";
}


/* LOGOUT */

const logoutBtn = document.getElementById("logoutBtn");

if(logoutBtn){

    logoutBtn.addEventListener("click", () => {

        localStorage.removeItem("access");
        localStorage.removeItem("refresh");

        window.location = "/login/";

    });

}


/* STATS + CHART */

fetch("/api/core/superadmin/dashboard/stats/", {

    headers: {
        "Authorization": "Bearer " + token
    }

})
.then(res => res.json())
.then(data => {

    const orgCount = document.getElementById("org_count");
    const hrCount = document.getElementById("hr_count");
    const empCount = document.getElementById("emp_count");
    const payCount = document.getElementById("pay_count");

    if(orgCount) orgCount.innerText = data.organizations;
    if(hrCount) hrCount.innerText = data.hr;
    if(empCount) empCount.innerText = data.employees;
    if(payCount) payCount.innerText = data.payrolls;

    loadChart(data);

});


/* CHART */

let chartInstance = null;

function loadChart(data){

    const ctx = document.getElementById("statsChart");

    if(!ctx) return;

    if(chartInstance){
        chartInstance.destroy();
    }

    chartInstance = new Chart(ctx, {

        type: "bar",

        data: {

            labels: [
                "Organizations",
                "HR",
                "Employees",
                "Payrolls"
            ],

            datasets: [{

                label: "System Stats",

                data: [
                    data.organizations,
                    data.hr,
                    data.employees,
                    data.payrolls
                ],

                backgroundColor: [
                    "#2563eb",
                    "#16a34a",
                    "#f59e0b",
                    "#dc2626"
                ]

            }]

        },

        options: {

            responsive: true,

            plugins: {
                legend: {
                    display: false
                }
            }

        }

    });

}


/* ORGANIZATION DATA */

let orgData = [];
let currentPage = 1;
const rowsPerPage = 5;


fetch("/api/core/superadmin/organizations/", {

    headers: {
        "Authorization": "Bearer " + token
    }

})
.then(res => res.json())
.then(data => {

    orgData = data;

    paginate(orgData);

});


/* TABLE RENDER */

function renderTable(data){

    const table = document.getElementById("org_table");

    if(!table) return;

    table.innerHTML = "";

    data.forEach(org => {

        table.innerHTML += `

        <tr>

            <td>${org.id}</td>
            <td>${org.name}</td>
            <td>${org.hr_name}</td>
            <td>${org.employees}</td>

            <td>

                <button class="view" onclick="viewOrg(${org.id})">
                    View
                </button>

                <button class="edit"
                    onclick="editOrg(${org.id},'${org.name}','${org.hr_name}','${org.hr_email}')">
                    Edit
                </button>

                <button class="delete" onclick="deleteOrg(${org.id})">
                    Delete
                </button>

            </td>

        </tr>

        `;

    });

}


/* PAGINATION */

function paginate(data){

    const start = (currentPage - 1) * rowsPerPage;
    const end = start + rowsPerPage;

    const pageData = data.slice(start, end);

    renderTable(pageData);

    const pageCount = Math.ceil(data.length / rowsPerPage);

    const pagination = document.getElementById("pagination");

    if(!pagination) return;

    pagination.innerHTML = "";

    for(let i = 1; i <= pageCount; i++){

        pagination.innerHTML += `
            <button onclick="goPage(${i})">
                ${i}
            </button>
        `;

    }

}

window.goPage = function(page){

    currentPage = page;

    paginate(orgData);

}


/* SEARCH */

const searchInput = document.getElementById("searchOrg");

if(searchInput){

    searchInput.addEventListener("keyup", function(){

        const value = this.value.toLowerCase();

        const filtered = orgData.filter(o =>
            o.name.toLowerCase().includes(value)
        );

        currentPage = 1;

        paginate(filtered);

    });

}


/* MODAL */

const modal = document.getElementById("orgModal");
const createBtn = document.getElementById("createOrgBtn");
const closeModal = document.getElementById("closeModal");

if(createBtn && modal){

    createBtn.addEventListener("click", () => {

        modal.style.display = "block";

    });

}

if(closeModal && modal){

    closeModal.addEventListener("click", () => {

        modal.style.display = "none";

    });

}


/* CREATE ORGANIZATION */

const submitBtn = document.getElementById("submitOrg");

if(submitBtn){

submitBtn.addEventListener("click", async () => {

    const org_name = document.getElementById("org_name").value;
    const hr_name = document.getElementById("hr_name").value;
    const hr_email = document.getElementById("hr_email").value;
    const hr_password = document.getElementById("hr_password").value;

    const res = await fetch("/api/core/superadmin/organizations/create/", {

        method: "POST",

        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },

        body: JSON.stringify({

            organization_name: org_name,
            hr_full_name: hr_name,
            hr_email: hr_email,
            hr_password: hr_password

        })

    });

    if (res.ok) {
        location.reload();
    } else {
        alert("Error creating organization");
    }

});

}


/* DELETE */

window.deleteOrg = async function(id){

    if (!confirm("Delete this organization?")) return;

    const res = await fetch(`/api/core/superadmin/organizations/${id}/delete/`, {

        method: "DELETE",

        headers: {
            "Authorization": "Bearer " + token
        }

    });

    if(res.ok){
        location.reload();
    }

}


/* EDIT */

let currentOrgId = null;

window.editOrg = function(id, name, hrName, hrEmail){

    currentOrgId = id;

    document.getElementById("edit_org_name").value = name;
    document.getElementById("edit_hr_name").value = hrName;
    document.getElementById("edit_hr_email").value = hrEmail;

    document.getElementById("editModal").style.display = "block";

}


window.closeEdit = function(){
    document.getElementById("editModal").style.display = "none";
}

/* LOAD RECENT ACTIVITY */

function loadActivity(){

fetch("/api/core/superadmin/activity/",{

headers:{
"Authorization":"Bearer " + token
}

})
.then(res=>res.json())
.then(data=>{

const container=document.querySelector(".activity");

if(!container) return;

let html="<h3>Recent Activity</h3>";

data.forEach(a=>{

let icon="🟢";

if(a.action==="ADD_EMPLOYEE") icon="👤";
if(a.action==="GENERATE_PAYROLL") icon="💰";
if(a.action==="DELETE_ORG") icon="🔴";

html+=`

<div class="activity-item">

${icon} ${a.message}
<br>
<small>${a.user_name} • ${a.time_ago}</small>

</div>

`;

});

container.innerHTML=html;

});

}

loadActivity();

setInterval(loadActivity, 10000);


/* VIEW */

window.viewOrg = function(id){

    window.location = `/superadmin/organization/${id}/`;

}

});