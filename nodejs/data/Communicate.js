var socks = require("../server.js");

var DB_conn = socks.DB_conn;
var client = socks.client_server_sock;
var crawling = socks.crawling_server_sock;
var worker = socks.worker;

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

//between client and nodejs server
client.on('data',function(data){
    var label = 0; // For menu
    console.log('client_server sent' + data.toString());
    
    var str = data.split(' ');
    label = str[0];
    //쓰레드 풀 만들어 놓고 worker_thread에 데이터 전달해서 밑에 함수 수행?
    //쓰레드 내에 버퍼 만들어서 여러 작업 수행?
    //만약 버퍼가 다 찼으면 대기? -> 버퍼 찼는지 어떻게 알지는 생각...
    
    writeData(client,'data');
});

crawling.on('data',function(data){
    
});