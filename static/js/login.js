import { saveAuth } from "/static/js/auth.js";

document.getElementById("loginBtn").addEventListener("click", async () => {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const res = await fetch("http://127.0.0.1:8000/api/token/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const data = await res.json();

  if (!res.ok) {
    document.getElementById("error").innerText = data.detail || "Login failed";
    return;
  }

  saveAuth(data);

  const meRes = await fetch("http://127.0.0.1:8000/api/accounts/me/", {
    headers: { "Authorization": `Bearer ${data.access}` },
  });

  const me = await meRes.json();

  if (me.role === "HR") {
    window.location.href = "/hr/dashboard/";
  } else {
    window.location.href = "/employee/dashboard/";
  }
});
