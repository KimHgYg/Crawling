var net = require("net");

module.exports = function(){
    var client_server_sock;
    var client_server = net.createServer(function(client_sock){
        client_server_sock = client_sock;
        console.log('client_server connected');
        console.log('   local = %s:%s', client_server_sock.localAddress, client_server_sock.localPort);
        console.log('   remote = %s:%s', client_server_sock.remoteAddress, client_server_sock.remotePort);
        //client_server_sock.setTimeout(500);
        client_server_sock.setEncoding('utf8');
        client_server_sock.setKeepAlive();
        client_server_sock.on('end',function(){
            console.log('client_server_sock disconnectd;);');
            client_server.getConnections(function(err, count){
                if(err){console.error(err);}
                console.log('Remaining Connections : ' + count);
            });
        });
        
        client_server_sock.on('error', function(err){
            console.log('client_server_Socket Error: ',JSON.stringify(err));
        });
        /*
        //if use timeout, implements heartbeat
        client_server_sock.on('timeout',function(){
            console.log('client_server_Socket Time out');
        });*/
    });
    
    client_server.listen(3000,function(){
        console.log('Clinet Server listening for connection');
        client_server.on('close',function(){
            console.log('client_Server Terminated');
        });
        client_server.on('end',function(){
            console.log('client disconnected');
        });
        client_server.on('error', function(err){
            console.log('client_Server Error: ', JSON.stringify(err));
        });
    });
    return client_server_sock;
};