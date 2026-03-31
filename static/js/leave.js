const token = localStorage.getItem("access");

window.onload = function () {
    loadSummary();
    loadLeaves();
};

// ================= SUMMARY =================
async function loadSummary() {
    try {
        const res = await fetch("/api/core/leaves/summary/", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        if (!res.ok) throw new Error("Unauthorized");

        const data = await res.json();

        document.getElementById("total-leaves").innerText = data.total_taken ?? 0;
        document.getElementById("remaining-leaves").innerText = data.remaining ?? 0;
        document.getElementById("salary-deduction").innerText = "₹" + (data.salary_deduction ?? 0);

    } catch (err) {
        console.error("Summary Error:", err);
    }
}

// ================= STATUS CLASS =================
function getStatusClass(status) {
    if (status === "APPROVED") return "approved";
    if (status === "REJECTED") return "rejected";
    return "pending";
}

// ================= LOAD LEAVES =================
async function loadLeaves() {
    try {
        const res = await fetch("/api/core/leaves/my/", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        if (!res.ok) throw new Error("Unauthorized");

        const data = await res.json();

        const table = document.getElementById("leave-table");
        table.innerHTML = "";

        if (!Array.isArray(data)) {
            console.error("Invalid response:", data);
            return;
        }

        data.forEach(leave => {
            table.innerHTML += `
            <tr>
                <td>${leave.leave_type}</td>
                <td>${leave.start_date} → ${leave.end_date}</td>
                <td>
                    <span class="badge ${getStatusClass(leave.status)}">
                        ${leave.status}
                    </span>
                </td>
                <td>${leave.leave_payment}</td>
            </tr>
            `;
        });

    } catch (err) {
        console.error("Leave Load Error:", err);
    }
}

function showToast(message) {
    const toast = document.createElement("div");
    toast.innerText = message;
    toast.className = "toast";

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// ================= APPLY LEAVE =================
async function applyLeave() {

    const body = {
        leave_type: document.getElementById("leave-type").value,
        start_date: document.getElementById("start-date").value,
        end_date: document.getElementById("end-date").value,
        reason: document.getElementById("reason").value
    };

    try {
        const res = await fetch("/api/core/leaves/apply/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify(body)
        });

        if (res.ok) {
            showToast("Leave Applied ✅");

            loadLeaves();
            loadSummary();

            document.getElementById("reason").value = "";
        } else {
            const err = await res.json();
            console.error(err);
            alert("Error ❌");
        }

    } catch (err) {
        console.error("Apply Error:", err);
    }
}