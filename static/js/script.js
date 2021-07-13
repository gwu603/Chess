
const squares = document.querySelectorAll('.square');
const pieces = document.querySelectorAll(".blackrook, .whiterook, .blackbishop, .whitebishop, .blackknight, .whiteknight, .blackpawn, .whitepawn, .blackqueen, .whitequeen, .blackking, .whiteking");
const background = document.querySelector(".wholeboard");
let draggedpiece = null;
var lastaction;
let parent;
let fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR White"
var socket = io.connect("https://frozen-tor-58069.herokuapp.com")

const gameCode = localStorage["code"]

socket.on("connect", function(){
    if (localStorage["MOJ"] == "1") {
        socket.emit("createGame", gameCode)
    } else {
        socket.emit("joinGame", gameCode)
    }
})

if (localStorage["MOJ"] == "1") {
    const overlay = document.createElement("div")
    overlay.id = "overlay"
    const text = document.createElement("div")
    text.id = "text"
    text.innerText = "Waiting ..." + "\n" + "Code: " + gameCode;
    overlay.appendChild(text)
    document.querySelector(".wholeboard").append(overlay)
} else {
    socket.emit("playJoin", gameCode)
}

socket.on("playerJoin", function() {
    document.getElementById("overlay").style.display = "none"
    console.log("other player joined")
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
    piece.style.height = "5vw"
    piece.style.width = "5vw"
    piece.addEventListener("dragstart", dragStart);
    piece.addEventListener("dragend", dragEnd);
}

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
        reloadBoard(fen)
    }
});

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
                let trialmove = firstletter + move[0] + move[1] + extra + move[2] + move[3];
                const input = trialmove + fen

                //httpPost("http://127.0.0.1:5000/make_move", input, console.log)
                socket.emit("makemove", gameCode, input)

            } else {
                reloadBoard(fen)
            }

        }
    });
}

socket.on('makemove', function(msg) {
    console.log("msg recieved")
    if (msg[0] == "T") {
        fen = msg.substring(1,)
    }
    reloadBoard(fen)
})





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
            reloadBoard(fen)
        }
    }
}


function reloadBoard (fen) {
    const squares = document.querySelectorAll(".square")
    const onlyPieces = fen.split(" ")[0]
    const lowercase = "prnbqk"
    const uppercase = "PRNBQK"
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
    element.draggable = true;
    element.className = color + name
    element.style.height = "5vw"
    element.style.width = "5vw"
    element.style.postion = "relative"
    element.style.cursor = "pointer"
    element.addEventListener("dragstart", dragStart);
    element.addEventListener("dragend", dragEnd);
    return element
}