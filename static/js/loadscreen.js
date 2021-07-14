let createGame = document.getElementById("createGame")
let joinGame = document.getElementById("joinGame")
let submit = document.getElementById("submit")

var socket = io.connect("http://127.0.0.1:5000")

socket.on("connect", function () {
    console.log("connected")
})

createGame.addEventListener("click", function () {
    const code = Math.random().toString(36).substring(7)
    localStorage["code"] = code
    localStorage["MOJ"] = "1"
    window.location.href = "test"
    //socket.emit("switchScreen")
})

submit.addEventListener("click", function () {
    const code = joinGame.value
    joinGame.value = ""
    socket.emit("checkCode", code)
    socket.on("checkCode", function(msg) {
        if (msg) {
            localStorage["code"] = code
            localStorage["MOJ"] = "2"
            //socket.emit("switchScreen")
            window.location.href = "test"
            
        } else {
            console.log("Code DNE")
        }
    })

})