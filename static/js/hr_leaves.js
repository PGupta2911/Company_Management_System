import { requireAuth, logout } from "/static/js/auth.js";

requireAuth();

// ================= SAFE LOGOUT =================
const logoutBtn = document.getElementById("logoutBtn");
if (logoutBtn) {
    logoutBtn.addEventListener("click", logout);
}

let selectedLeaveId = null;

// ================= INIT =================
window.onload = function () {
    loadLeaves();
    setupModalEvents();
};

// ================= STATUS CLASS =================
function getStatusClass(status) {
    if (status === "APPROVED") return "approved";
    if (status === "REJECTED") return "rejected";
    return "pending";
}

// ================= LOAD LEAVES =================
async function loadLeaves() {
    try {
        const res = await fetch("/api/core/leaves/all/", {
            headers: {
                "Authorization": "Bearer " + localStorage.getItem("access")
            }
        });

        const data = await res.json();

        const table = document.getElementById("leaveTable");
        table.innerHTML = "";

        if (!Array.isArray(data) || data.length === 0) {
            table.innerHTML = `<tr><td colspan="6">No data found</td></tr>`;
            return;
        }

        data.forEach(leave => {
            const row = document.createElement("tr");
            row.dataset.status = leave.status;

            row.innerHTML = `
                <td>${leave.employee_name || "N/A"}</td>
                <td>${leave.leave_type}</td>
                <td>${leave.start_date} → ${leave.end_date}</td>
                <td>
                    <span class="badge ${getStatusClass(leave.status)}">
                        ${leave.status}
                    </span>
                </td>
                <td>${leave.leave_payment}</td>
                <td>
                    ${leave.status === "PENDING" ? `
                        <button class="action-btn approve-btn" onclick="manageLeave(${leave.id}, 'APPROVE')">Approve</button>
                        <button class="action-btn reject-btn" onclick="openRejectModal(${leave.id})">Reject</button>
                    ` : "-"}
                </td>
            `;

            table.appendChild(row);
        });

    } catch (err) {
        console.error("Error loading leaves:", err);
    }
}

// ================= OPEN MODAL =================
function openRejectModal(id) {
    selectedLeaveId = id;
    document.getElementById("rejectModal").style.display = "flex";
}

// ================= SETUP MODAL EVENTS =================
function setupModalEvents() {

    const closeBtn = document.getElementById("closeRejectModal");
    const confirmBtn = document.getElementById("confirmReject");

    if (closeBtn) {
        closeBtn.onclick = () => {
            document.getElementById("rejectModal").style.display = "none";
        };
    }

    if (confirmBtn) {
        confirmBtn.onclick = async () => {

            const reason = document.getElementById("rejectReason").value;

            if (!reason) {
                alert("Please enter reason");
                return;
            }

            try {
                const res = await fetch(`/api/core/leaves/${selectedLeaveId}/manage/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer " + localStorage.getItem("access")
                    },
                    body: JSON.stringify({
                        action: "REJECT",
                        reason: reason
                    })
                });

                if (res.ok) {
                    alert("Rejected with reason ✅");
                    document.getElementById("rejectModal").style.display = "none";
                    document.getElementById("rejectReason").value = "";
                    loadLeaves();
                } else {
                    alert("Error ❌");
                }

            } catch (err) {
                console.error(err);
                alert("Something went wrong");
            }
        };
    }
}

// ================= FILTER =================
function filterLeaves(type, event) {

    document.querySelectorAll(".filter-btn").forEach(btn => {
        btn.classList.remove("active");
    });

    if (event) event.target.classList.add("active");

    const rows = document.querySelectorAll("#leaveTable tr");

    rows.forEach(row => {
        const status = row.dataset.status;

        if (type === "ALL" || status === type) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
}

// ================= APPROVE =================
async function manageLeave(id, action) {

    try {
        const res = await fetch(`/api/core/leaves/${id}/manage/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + localStorage.getItem("access")
            },
            body: JSON.stringify({ action })
        });

        if (res.ok) {
            alert("Updated ✅");
            loadLeaves();
        } else {
            alert("Error ❌");
        }

    } catch (err) {
        console.error(err);
        alert("Something went wrong");
    }
}

// ================= GLOBAL EXPORT =================
window.manageLeave = manageLeave;
window.openRejectModal = openRejectModal;
window.filterLeaves = (type, e) => filterLeaves(type, e);