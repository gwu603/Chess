let loginInstead = document.getElementById("loginInstead")
let createAccount = document.querySelector(".createAccount")
let usernameInput = document.getElementById("Username")
let firstpassInput = document.getElementById("Pass")
let secondpassInput = document.getElementById("Confirm")
let userText = document.getElementById("userText")

// firstpassInput.addEventListener("keyup", sendInfo )
usernameInput.addEventListener("keyup", function (e) {
    if (usernameInput.value.includes(" ")) {
        userText.innerText = "Sorry, your username cannot include spaces."
    } else {
        userText.innerText = ""
    }
    if (e.code == "Enter") {
        sendInfo()
    }
})

secondpassInput.addEventListener("keyup", function(e) {
    let isMatch = false
    if (secondpassInput.value != firstpassInput.value) {
        isMatch = false
        passText.innerText = "Sorry, your passwords do not match."
    } else {
        isMatch = true
        passText.innerText = ""
    }

    if (e.code == "Enter" && isMatch) {
        sendInfo()
    }

})



loginInstead.addEventListener("click", function () {
    window.location.href = "login.html"
})

createAccount.addEventListener("click", function () {

    console.log(usernameInput.value + firstpassInput.value )
    usernameInput.value = ""
    firstpassInput.value = ""
    secondpassInput.value = ""
    
})
