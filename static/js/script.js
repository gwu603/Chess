var squares = document.querySelectorAll('.square');
var pieces = document.querySelectorAll(".blackrook, .whiterook, .blackbishop, .whitebishop, .blackknight, .whiteknight, .blackpawn, .whitepawn, .blackqueen, .whitequeen, .blackking, .whiteking");
var background = document.querySelector(".wholeboard");
var board = document.querySelector(".board");


var textbar = document.querySelector(".messageinput")
var messages = document.querySelector(".messageoutput")
var topbar = document.querySelector(".gameInfo")

var draggedpiece = null;
var lastaction;
var parent;
var fen; 
// var socket = io.connect("https://gwuchess.herokuapp.com")

var socket = io()

var flip; //Whether or not the board should be flipped
var gameCode = localStorage["code"] //The code of the overall game
var posMoves = {} //dictionary of possible moves that can be made with each move mapped to their respective fen
var dstate; //whether or not the given player is allowed to move
var playercolor; //color of the current person playing
var opponentcolor; //color of the opponent playing

var pastFens = ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR White KQkq - 0 1"]
var pastMoves = []
var movesearch = pastMoves.length
var chatHistory = []

var standardMove = new Audio('static/audio/standardMove.mp3');
var standardMove2 = new Audio('static/audio/standardMove.mp3');
var outOfBound = new Audio('static/audio/outOfBound.mp3');
var capturePiece = new Audio('static/audio/capturePiece.mp3');
var capturePiece2 = new Audio('static/audio/capturePiece.mp3');
var check = new Audio('http://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/move-check.mp3');
var gameEnd = new Audio('http://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/game-end.mp3');


socket.on("connect", function(){

    if (localStorage["MOJ"] == "1") {
        playercolor = "White"
        opponentcolor = "Black"
        flip = false
    } else if (localStorage["MOJ"] == "2"){
        playercolor = "Black"
        opponentcolor = "White"
        flip = true
        for (let i = squares.length-1; i >= 0; i --) {
            board.appendChild(squares[i])
        }
    }
    socket.emit("joinGame", gameCode)
    socket.emit("get-data", gameCode)
    socket.on("posMoves", function (moves) {
        posMoves = moves
    })
    socket.on("set-data", function (data) {
        dstate = false
        pastMoves = data["pastMoves"]
        pastFens = data["pastFens"]
        chatHistory = data["chatHistory"]
        fen = pastFens[pastFens.length-1]

        if (fen.split(" ")[1] == playercolor) {
            dstate = true
        }
        if (!data["twoplayer"]) {
            waitingOverlay()
        }
        reloadMoveDisplay(pastMoves)
        reloadChatHistory(chatHistory)
        reloadBoard(fen, flip)
    })
})

function waitingOverlay () {
    const overlay = document.createElement("div")
    overlay.className = "overlay"
    const text = document.createElement("div")
    text.className = "text"
    text.innerText = "Waiting ..." + "\n" + "Code: " + gameCode;
    overlay.appendChild(text)
    document.querySelector(".wholeboard").append(overlay)
}


socket.on("playerJoin", function() {
    removeWaitingOverlay()
    console.log("other player joined")
})

function removeWaitingOverlay () {
    document.querySelector(".overlay").style.display = "none"
}


// topbar.innerText = "gwuChess \n \n playing friend"


textbar.addEventListener("keyup", function(e) {
    if (e.code == "Enter") {
        if (textbar.value.length != 0) {
            newMessage(playercolor, textbar.value)
            socket.emit("chatmessage", {"gameCode":gameCode, "chatHistory":chatHistory})
        }
        textbar.value = ""
    }
})

socket.on("chatmessage", function (ch) {
    chatHistory = ch
    reloadChatHistory(chatHistory)
})



for (let i = 0; i < squares.length; i ++) {
    if (Math.floor(i/8) % 2 == 0) {
        squares[i].style.backgroundColor = (i % 2 == 0) ? 'bisque' : 'burlywood' 
    } else {
        squares[i].style.backgroundColor = (i % 2 == 0) ? 'burlywood' : 'bisque' 
    }
}

for (let i = 0; i < pieces.length; i ++) {
    const piece = pieces[i]
    piece.style.height = "3.75vw"
    piece.style.width = "3.75vw"
    piece.style.margin = "0.6125vw"
    piece.addEventListener("dragstart", dragStart);
    piece.addEventListener("dragend", dragEnd);
}

document.addEventListener("keyup", function(e) {
    if (e.code == "ArrowLeft" && movesearch > 0) {
        movesearch -= 1
        reloadBoard(pastFens[movesearch], flip)
    }
    if (e.code == "ArrowRight" && movesearch < pastFens.length-1) {
        movesearch += 1
        reloadBoard(pastFens[movesearch], flip)
    }
})

background.addEventListener("dragover", function (event) {
    if (draggedpiece != null) {
        event.preventDefault();
    }
});
background.addEventListener("dragenter", function (event) {
    if (draggedpiece != null) {
        event.preventDefault();
    }
});

background.addEventListener("dragleave", function () {
});

background.addEventListener("drop", function(){

    if (lastaction == "dragleave") {
        reloadBoard(fen, flip)
        outOfBound.play()
    }
});



socket.on("oppoMove", function (data) {
    // posMoves = data["posMove"]
    fen = data["fen"]
    pastFens.push(fen)
    pastMoves.push(data["move"])
    movesearch = pastMoves.length
    // newMove(opponentcolor, data["move"])

    if (data["move"][3] == "x") {
        capturePiece2.play()
    } else {
        standardMove2.play()
    }
    dstate = true
    reloadMoveDisplay(pastMoves)
    reloadBoard(fen,flip)
})


socket.on("check", function(color) {
    check.play()
})

socket.on("gameOver", function (ending) {
    gameOver(ending)
})

function gameOver (ending) {
    gameEnd.play()
    const overlay = document.createElement("div")
    overlay.className = "overlay"
    const text = document.createElement("div")
    text.className = "text"
    text.innerText = ending.substring(0,5) + " " + ending.substring(5,) + "d"
    overlay.appendChild(text)
    document.querySelector(".wholeboard").append(overlay)
}


// socket.on("updatedFen", function(newfen) {

//     newMove(opponentcolor, newfen.split(" ")[0])
//     reloadBoard(newfen.split(" ").splice(1).join(" "), flip)

//     fen = newfen.split(" ").splice(1).join(" ")
    
//     if (newfen.split(" ")[0][3] == "x"){
//         capturePiece2.play()
//     } else {
//         standardMove2.play()
//     }
//     pastFens.push(fen)
    
// })




for (let j = 0; j < squares.length; j ++) {
    const square = squares[j];

    square.addEventListener("dragover", function (event) {
        if (draggedpiece != null) {
            event.preventDefault();
            lastaction = "dragenter"
        }
    });
    square.addEventListener("dragenter", function (event) {
        if (draggedpiece != null) {
            event.preventDefault();
        }

    });

    square.addEventListener("dragleave", function () {
        if (draggedpiece != null) {
            lastaction = "dragleave"
        }

    });
    square.addEventListener("drop", function () { 
        if (draggedpiece != null) {            
            
            const color = draggedpiece.className.substring(0,5);
            const name = draggedpiece.className.substring(5,);
            
            let extra = ""
            if (square.children.length == 1) {
                extra = "x"
                square.innerHTML = ""
            }
            if (parent.getAttribute("id") != j) {
                const move = calculateMove(parent.getAttribute("id"), j)
                let firstletter = name[0].toUpperCase()
                if (name.substring(0,2) == "kn") {
                    firstletter = "N"
                }

                if (firstletter == "P" && move[0] != move [2]){
                    extra = "x"
                }
                let trialmove = firstletter + move[0] + move[1] + extra + move[2] + move[3];
                console.log(trialmove)

                if (posMoves[trialmove] != null && fen.split(" ")[1] == playercolor) {

 
                    fen = posMoves[trialmove]
                    pastMoves.push(trialmove)
                    
                    movesearch = pastMoves.length
                    if (trialmove[0] == "P" && (trialmove[trialmove.length - 1] == "8" || trialmove[trialmove.length - 1] == "1")) {
                        fen = createProScreen(playercolor, fen)
                    } else {
                        pastFens.push(fen)
                        socket.emit("makemove", {"gameCode": gameCode, "move": trialmove, "fen":fen})
                    }

                    if (extra == "x") {
                        capturePiece.play()
                    } else {
                        standardMove.play()
                    }

                    dstate = false
                    reloadMoveDisplay(pastMoves)
                    // newMove(playercolor, trialmove)


                } else {
                    outOfBound.play()
                }
                reloadBoard(fen, flip)
                //const input = trialmove + fen

                //httpPost("http://127.0.0.1:5000/make_move", input, console.log)
                //socket.emit("makemove", gameCode, input)

            } else {
                reloadBoard(fen, flip)
            }

        }
    });
}



function createProScreen (color, fakefen) {
    const overlay = document.createElement("div")
    overlay.className = "overlay"
    const proback = document.createElement("div")
    proback.className = "proback"
    overlay.appendChild(proback)

    for (let i = 0; i < 4; i ++) {
        proback.append(createSquare("prosquare"))
    }

    document.querySelector(".wholeboard").append(overlay)
    const prosquares = document.querySelectorAll(".prosquare")

    let fourpieces = ["R","B", "N", "Q"]
    for (let i = 0; i < 4; i ++) {
        placepiece = createPiece(fourpieces[i], color)
        placepiece.draggable = false
        prosquares[i].append(placepiece)
        placepiece.addEventListener("click", function () {
            console.log(this.className)
            removeDisplay()
            // document.querySelector(".overlay").style.display = "none"
            //document.querySelector(".overlay").remove()
            let piece = this.className
            let placeholder = fakefen.split(" ")
            let piecefen = placeholder[0]
            if (piece.substring(5,7) == "kn") {
                piece = piece.substring(0,5) + piece.substring(6,)
            }
            if (piece[0] == "B") {
                console.log(piece)

                for (let i = piecefen.length-1; i >= 0; i --) {
                    if (piecefen[i].toLowerCase() == "p") {
                        let chosenpiece = piece[5].toLowerCase()
                        piecefen = piecefen.substring(0,i) + chosenpiece + piecefen.substring(i+1,)
                        break
                    }
                }

            } else {
                for (let i = 0; i < fakefen.length; i++) {
                    if (piecefen[i].toLowerCase() == "p") {
                        let chosenpiece = piece[5].toUpperCase()
                        piecefen = piecefen.substring(0,i) + chosenpiece + piecefen.substring(i+1,)
                        break
                    }
                }
            }
            fakefen = piecefen + " " + placeholder[1] + " " + placeholder[2] + " " + placeholder[3] + " " + placeholder[4] + " " + placeholder[5]
            reloadBoard(fakefen, flip)
            socket.emit("makemove", gameCode, fakefen)
            dstate = false

            //console.log(fakefen)
        })
    }
    fen = fakefen
    pastFens.push(fen)
    return fakefen
}

function removeDisplay () {
    document.querySelector(".overlay").style.display = "none"
    document.querySelector(".overlay").remove()
    console.log("display removed")
}


function createSquare (name) {
    const text = document.createElement("div")
    text.className = name
    return text
}


function calculateMove (start, end) {
    start = parseInt(start)
    end = parseInt(end)
    let endRow = Math.floor((end) / 8);
    let endCol = end - endRow*8;
    let startRow = Math.floor((start) / 8) ;
    let startCol = start - startRow*8;


    endRow = 8 - endRow;
    endCol = endCol + 1;
    startRow = 8 - startRow;
    startCol = startCol + 1

    let output = [startCol, startRow, endCol, endRow]
    return output
}

function dragStart () {
    draggedpiece = this;
    left = true
    leave = 10000;
    parent = draggedpiece.parentNode
    setTimeout(function() {
        draggedpiece.style.display = 'none';
    })
}

function dragEnd () {
    if (draggedpiece != null) {        
        setTimeout(function () {
                draggedpiece.style.display = 'block';
                draggedpiece.remove()
                draggedpiece = null   
        })
    }
}    
// function httpGetAsync(theUrl, callback) {
//     var xmlHttp = new XMLHttpRequest();
//     xmlHttp.onreadystatechange = function() { 
//         if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
//             callback(xmlHttp.responseText);
//     }
    
//     xmlHttp.open("GET", theUrl, true); // true for asynchronous 
//     xmlHttp.send(null);
// }

function httpPost(theURL, input, callback) {
    const xmlHttp = new XMLHttpRequest();

    sender = JSON.stringify(input)
    xmlHttp.open('POST', theURL);
    xmlHttp.send(sender);

    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            if (String(xmlHttp.responseText)[0] == "T") {
                fen = String(xmlHttp.responseText).substring(1,)
            }
            reloadBoard(fen, flip)
        }
    }
}


function reloadBoard (fen, flip) {
    const squares = document.querySelectorAll(".square")
    let onlyPieces = fen.split(" ")[0]
    const lowercase = "prnbqk"
    const uppercase = "PRNBQK"

    

    if (flip) {
        let placeholder =""
        for (let i = onlyPieces.length-1; i >= 0; i --){
            placeholder += onlyPieces[i]
        }
        onlyPieces = placeholder
    }

    let j = 0
    for (let i = 0; i < squares.length; i ++) {
        squares[i].innerHTML = ""
    }
    for (let i = 0; i < onlyPieces.length; i ++) {
        if (lowercase.includes(onlyPieces[i])) {
            const element = createPiece(onlyPieces[i], "black")
            squares[j].appendChild(element)
            j += 1
        } 
        if (uppercase.includes(onlyPieces[i])) {

            const element = createPiece(onlyPieces[i], "white")
            squares[j].appendChild(element)
            j += 1
        }
        if (!isNaN(onlyPieces[i])) {
            j += parseInt(onlyPieces[i])
        }
    }
}



function getFen() {
    const squares = document.querySelectorAll(".square")
    let fen = ""
    let space = 0
    for (let i = 0; i < squares.length; i ++) {
        if (i % 8 == 0 && i != 0) {
            if (space != 0) {
                fen += space
                space = 0
            }
            fen += "/"
        } 
        if (squares[i].children.length == 1) {
            const piece = squares[i].children[0].className
            let name = ""
            console.log(piece)
            if (piece.substring(5,7) == "kn") {
                name = "n"
            } else {
                name = piece[5]
            }
            if (piece.substring(0,5) == "white") {
                fen += name.toUpperCase()
            } else {
                fen += name
            }
            if (space != 0) {
                fen += space
                space = 0
            }
        }
        else {
            space += 1
        }
    }
    if (space != 0) {
        fen += space
    }
    return fen
}

function createPiece (name, color) {
    name = name.toUpperCase()

    if (name == "P") {
        name = "pawn"
    } else if (name == "R") {
        name = "rook"
    } else if (name == "N") {
        name = "knight"
    } else if (name == "B") {
        name = "bishop"
    } else if (name == "Q") {
        name = "queen"
    } else if (name == "K") {
        name = "king"
    }

    let element = document.createElement("img");
    element.src = "static/images/" + color + name +".jpg";
    element.draggable = dstate
    element.className = color + name
    element.style.height = "3.75vw"
    element.style.width = "3.75vw"
    element.style.margin = "0.6125vw"
    element.style.postion = "relative"
    element.style.cursor = "pointer"
    element.addEventListener("dragstart", dragStart);
    element.addEventListener("dragend", dragEnd);
    return element
}


function reloadChatHistory (ch) {
    let messages = document.querySelector(".messageoutput")
    messages.innerHTML = ""
    for (let i = 0; i<ch.length; i ++) {
        newmessage = document.createElement("p")
        newmessage.innerText = ch[i]
        newmessage.className = "message"
        messages.appendChild(newmessage)
        messages.scrollTop = messages.scrollHeight
    }
}

function newMessage(color, msg) {
    let messages = document.querySelector(".messageoutput")
    newmessage = document.createElement("p")
    newmessage.innerText = "[" + color + "] " + msg
    chatHistory.push(newmessage.innerText)
    newmessage.className = "message"
    messages.appendChild(newmessage)
    messages.scrollTop = messages.scrollHeight
}

function reloadMoveDisplay (moves) {
    console.log(moves)
    let pastMovesDisplay = document.querySelector(".pastMovesDisplay")
    let moveNum = document.querySelector(".moveNum")
    let whiteMoves = document.querySelector(".whiteMoves")
    let blackMoves = document.querySelector(".blackMoves")
    moveNum.innerHTML = ""
    whiteMoves.innerHTML = ""
    blackMoves.innerHTML = ""
    for (let i = 0; i < moves.length; i ++) {
        if (i%2 == 0) {
            newNum = document.createElement("li")
            whiteMove = document.createElement("li")
            newNum.innerText = String(i+1)
            whiteMove.innerText = moves[i]
            moveNum.appendChild(newNum)
            whiteMoves.appendChild(whiteMove)
        } else {
            blackMove = document.createElement("li")
            blackMove.innerText = moves[i]
            blackMoves.appendChild(blackMove)
        }

    }
    // if (movecolor == "White") {
    //     newNum = document.createElement("li")
    //     newNum.innerText = moveNum.childElementCount + 1
    //     moveNum.appendChild(newNum)
    //     whiteMove = document.createElement("li")
    //     whiteMove.innerText = move
    //     whiteMoves.appendChild(whiteMove)
    // } else {
    //     blackMove = document.createElement("li")
    //     blackMove.innerText = move
    //     blackMoves.appendChild(blackMove)
    // }
    pastMovesDisplay.scrollTop = pastMovesDisplay.scrollHeight
}