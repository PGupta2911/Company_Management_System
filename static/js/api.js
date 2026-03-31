export async function apiRequest(url, options = {}) {
    const access = localStorage.getItem("access");

    const res = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            "Authorization": access ? `Bearer ${access}` : "",
            ...(options.headers || {})
        }
    });

    if (res.status === 401) {
        window.location.href = "/login/";
        return;
    }

    return await res.json();
}