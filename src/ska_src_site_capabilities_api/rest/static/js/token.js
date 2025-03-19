function parseJwt(token) {
    let base64Url = token.split('.')[1];
    let base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    let jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
}

function startTokenTimer(token, elementId) {
    try {
        let decoded = parseJwt(token);
        if (!decoded.exp) {
            console.error("JWT does not contain an expiration time.");
            return;
        }

        let expTime = decoded.exp * 1000; // Convert to milliseconds

        function updateTimer() {
            let now = Date.now();
            let remainingTime = expTime - now;

            let timerElement = document.getElementById(elementId);
            if (!timerElement) return;

            if (remainingTime <= 0) {
                timerElement.innerHTML = "Session has expired.";
                timerElement.style.color = "red";
                alert("Session has expired. Changes cannot be saved.");
                clearInterval(timer);
                return;
            } else if (remainingTime <= 1000 * 60 * 5) {
                timerElement.innerHTML = "Session is expiring soon (5m), save changes.";
                timerElement.style.color = "#FF8C00";
                return;
            }

            let seconds = Math.floor((remainingTime / 1000) % 60);
            let minutes = Math.floor((remainingTime / 1000 / 60) % 60);
            let hours = Math.floor((remainingTime / (1000 * 60 * 60)) % 24);

            timerElement.innerHTML = `Token expires in: ${hours}h ${minutes}m ${seconds}s`;
        }

        updateTimer();
        let timer = setInterval(updateTimer, 1000);
    } catch (e) {
        console.error("Error parsing JWT:", e);
    }
}