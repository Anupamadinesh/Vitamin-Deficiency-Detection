document.addEventListener("DOMContentLoaded", function() {
    const loginForm = document.getElementById("login-form");
    const signupForm = document.getElementById("signup-form");
    const toggleText = document.getElementById("toggle-text");
    const toggleLink = document.getElementById("toggle-link");
    const formTitle = document.getElementById("form-title");

    toggleLink.addEventListener("click", function(event) {
        event.preventDefault();
        
        if (loginForm.style.display === "none") {
            loginForm.style.display = "block";
            signupForm.style.display = "none";
            formTitle.textContent = "Login";
            toggleText.innerHTML = `Don't have an account? <a href="#" id="toggle-link">Sign Up</a>`;
        } else {
            loginForm.style.display = "none";
            signupForm.style.display = "block";
            formTitle.textContent = "Sign Up";
            toggleText.innerHTML = `Already have an account? <a href="#" id="toggle-link">Login</a>`;
        }
    });
});
