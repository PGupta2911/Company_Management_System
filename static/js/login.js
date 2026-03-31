import { saveAuth } from "/static/js/auth.js";

document.getElementById("loginBtn").addEventListener("click", async () => {

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const errorBox = document.getElementById("error");
  errorBox.innerText = "";

  try {

    const res = await fetch("/api/token/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (!res.ok) {
      errorBox.innerText = data.detail || "Login failed";
      return;
    }

    saveAuth(data);

    const meRes = await fetch("/api/accounts/me/", {
      headers: { "Authorization": `Bearer ${data.access}` }
    });

    const me = await meRes.json();

    const role = (me.role || "").toUpperCase();
    console.log("ROLE:", role); // debug

    if (role === "SUPERADMIN") {
      window.location.replace("/superadmin/dashboard/");
      return;
    }

    if (role === "HR") {
      window.location.replace("/hr/dashboard/");
      return;
    }

    if (role === "EMPLOYEE") {
      window.location.replace("/employee/dashboard/");
      return;
    }

    errorBox.innerText = "Unknown role";

  } catch (err) {
    console.error(err);
    errorBox.innerText = "Server error";
  }
});