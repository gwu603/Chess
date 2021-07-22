let createAccount = document.querySelector(".createAccount")
let usernameInput = document.getElementById("Username")
let passwordInput = document.getElementById("Password")



createAccount.addEventListener("click", function () {
    window.location.href = "createAccount.html"
})

usernameInput.addEventListener("keyup", sendLoginInfo)

passwordInput.addEventListener("keyup", sendLoginInfo)

function sendLoginInfo (event) {
    if (event.code == "Enter") {
        // socket.emit("loginAttempt", usernameInput.value + " " + passwordInput.value)
        usernameInput.value = ""
        passwordInput.value = ""
    }

}