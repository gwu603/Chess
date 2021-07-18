
let squares = document.querySelectorAll('.square');
const pieces = document.querySelectorAll(".blackrook, .whiterook, .blackbishop, .whitebishop, .blackknight, .whiteknight, .blackpawn, .whitepawn, .blackqueen, .whitequeen, .blackking, .whiteking");
const background = document.querySelector(".wholeboard");

let textbar = document.querySelector(".messageinput")
let messages = document.querySelector(".messageoutput")
let topbar = document.querySelector(".gameInfo")

let draggedpiece = null;
var lastaction;
let parent;
var fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR White KQkq - 0 0"
// var socket = io.connect("https://gwuchess.herokuapp.com")
var socket = io.connect("http://127.0.0.1:5000")

let flip;
const gameCode = localStorage["code"]
var posMoves = {}
var dstate = true
var playercolor = ""

var pastmoves = ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR White KQkq - 0 1"]
var movesearch = pastmoves.length


socket.on("connect", function(){
    if (localStorage["MOJ"] == "1") {
        socket.emit("createGame", gameCode)
        flip = false
        socket.emit("initialMoves")
        socket.on("initialMoves", function(moves) {
            posMoves = moves
        })
        playercolor = "White"
        opponentcolor = "Black"
        reloadBoard(fen, flip)

    } else if (localStorage["MOJ"] == "2") {
        socket.emit("joinGame", gameCode)
        flip = true
        //reloadBoard(fen, flip)
        let board = document.querySelector(".board")
        const squares = document.querySelectorAll(".square")
        board.innerHTML = "" 
        for (let i = squares.length-1; i >= 0; i --) {
            board.appendChild(squares[i])
        }
        playercolor = "Black"
        opponentcolor = "White"

        dstate = false
    } else {
        flip = false
        socket.emit("createGame", gameCode)
        socket.emit("initialMoves")
        socket.on("initialMoves", function(moves) {
            posMoves = moves
        })
        playercolor = "White"
        opponentcolor = "Black"
        reloadBoard(fen, flip)

    }
})

socket.on("message", function(msg) {
    console.log(msg)
})


if (localStorage["MOJ"] == "1") {
    const overlay = document.createElement("div")
    overlay.className = "overlay"
    const text = document.createElement("div")
    text.className = "text"
    text.innerText = "Waiting ..." + "\n" + "Code: " + gameCode;
    overlay.appendChild(text)
    document.querySelector(".wholeboard").append(overlay)
} else if (localStorage["MOJ"] == "2") {
    socket.emit("playJoin", gameCode)
}

socket.on("playerJoin", function() {
    document.querySelector(".overlay").style.display = "none"
    document.querySelector(".overlay").remove()
    console.log("other player joined")
})


topbar.innerText = "gwuChess \n \n playing friend"
messages.scrollTop = messages.scrollHeight


textbar.addEventListener("keyup", function(e) {
    if (e.code == "Enter") {
        if (textbar.value.length != 0) {
            const msg = textbar.value
            newMessage(playercolor, msg)
            socket.emit("chatmessage", gameCode, msg)
        }
        textbar.value = ""
    }
})

socket.on("chatmessage", function (msg) {
    newMessage(opponentcolor, msg)
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
        reloadBoard(pastmoves[movesearch], flip)
    }
    if (e.code == "ArrowRight" && movesearch < pastmoves.length-1) {
        movesearch += 1
        reloadBoard(pastmoves[movesearch], flip)
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
    }
});



socket.on("oppoMove", function (moves) {
    
    posMoves = moves
    dstate = true
    if (posMoves == "stalemate" || posMoves == "checkmate"){
        socket.emit("gameOver", gameCode, opponentcolor+posMoves)
    }
    movesearch = pastmoves.length
})

socket.on("gameOver", function (ending) {
    const overlay = document.createElement("div")
    overlay.className = "overlay"
    const text = document.createElement("div")
    text.className = "text"
    text.innerText = ending.substring(0,5) + " " + ending.substring(5,) + "d"
    overlay.appendChild(text)
    document.querySelector(".wholeboard").append(overlay)
})

socket.on("updatedFen", function(newfen) {

    newMove(opponentcolor, newfen.split(" ")[0])
    reloadBoard(newfen.split(" ").splice(1).join(" "), flip)

    fen = newfen.split(" ").splice(1).join(" ")
    
    pastmoves.push(fen)
})


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

                if (posMoves[trialmove] != null && fen.split(" ")[1] == playercolor) {
                    fen = posMoves[trialmove]

                    if (trialmove[0] == "P" && (trialmove[trialmove.length - 1] == "8" || trialmove[trialmove.length - 1] == "1")) {
                        fen = createProScreen(playercolor, fen)
                    } else {
                        
                        socket.emit("makemove", gameCode, trialmove +" " +fen)
                        pastmoves.push(fen)
                        movesearch = pastmoves.length
                    }

                    dstate = false
                    newMove(playercolor, trialmove)

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
    pastmoves.push(fen)
    movesearch = pastmoves.length

    return fakefen
}

function removeDisplay () {
    document.querySelector(".overlay").style.display = "none"
    document.querySelector(".overlay").remove()
    console.log("display removed")
}

// socket.on('makemove', function(msg) {
//     console.log("msg recieved")
//     if (msg[0] == "T") {
//         fen = msg.substring(1,)
//     }
//     reloadBoard(fen, flip)
// })





// function nextFunction (response, element, square) {
//     console.log(response, "YOOOOOO")
//     if (response[0] == "F") {
//         dropped = false
//         console.log("invalid")
        
//     } else {
//         fen = response.substring(1, response.length)
//         square.appendChild(element)
//     }
    
//     newstatus = status + 1
//     console.log(newstatus, status)
// }

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


function newMessage (mcolor, msg) {
    let messages = document.querySelector(".messageoutput")
    let newmessage = document.createElement("p")
    newmessage.innerText = msg
    newmessage.className = "message"
    newmessage.innerText = "[" + mcolor + "] " + newmessage.innerText
    messages.appendChild(newmessage)
    messages.scrollTop = messages.scrollHeight
}



function newMove (movecolor, move) {
    let pastMoves = document.querySelector(".pastMoves")
    let moveNum = document.querySelector(".moveNum")
    let whiteMoves = document.querySelector(".whiteMoves")
    let blackMoves = document.querySelector(".blackMoves")
    if (movecolor == "White") {
        whiteMove = document.createElement("li")
        whiteMove.innerText = move
        whiteMoves.appendChild(whiteMove)
    } else {
        blackMove = document.createElement("li")
        blackMove.innerText = move
        blackMoves.appendChild(blackMove)
    }
    pastMoves.scrollTop = pastMoves.scrollHeight
}