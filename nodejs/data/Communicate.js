var socks = require("./server.js");

var DB_conn = socks.DB_conn;
var client = socks.client_server_sock;
var crawling = socks.crawling_server_sock;

var label = 0; // For menu

function writeData(socket, data){
    var success = !socket.write(data);
    if(!success){
        (function(socket, data){
            socket.once('drain',function(){
                writeData(socket,data);
            });
        })(socket,data);
    }
}

client.on('data',function(data){
    console.log('client_server sent' + data.toString());
    if(label == 0){
        label = data;
    }
    else if(label == 1){    //sign up
        var str = data;
        data = data.split(' '); //user_pri
        label = 0;
    }else if(label == 2){    //login
        
        label = 0;        
    }else if(label == 3){    //recommend article list for user
        
        label = 0;
    }else if(label == 4){    //request article list
        
        label = 0;
    }
    writeData(client,'data');
});

crawling.on('data',function(data){
    
});