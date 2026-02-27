export function saveAuth(data) {
    localStorage.setItem("access", data.access);
    localStorage.setItem("refresh", data.refresh);
}

export function requireAuth() {
    const access = localStorage.getItem("access");
    if (!access) {
        window.location.href = "/login/";
    }
}

export function logout() {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    window.location.href = "/login/";
}