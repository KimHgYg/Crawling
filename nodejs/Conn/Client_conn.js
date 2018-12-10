var net = require("net");
var client_server_sock;
module.exports = function(){
    client_server_sock = net.createServer((c) => {
        client_conn = c;
        console.log('client connected');
        console.log('   local = %s:%s', c.localAddress, c.localPort);
        console.log('   remote = %s:%s', c.remoteAddress, c.remotePort);
        //client_server_sock.setTimeout(500);
        c.setEncoding('utf8');
        c.setKeepAlive();
        //client disconnected
        c.on('end',function(){
            console.log('client_server_sock disconnectd;);');
            client_server_sock.getConnections(function(err, count){
                if(err){console.error(err);}
                console.log('Remaining Connections : ' + count);
            });
        });
        //error occured
        /*
        //if use timeout, implements heartbeat
        client_server_sock.on('timeout',function(){
            console.log('client_server_Socket Time out');
        });*/
    });
    
    client_server_sock.listen(3000,function(){
        console.log('Clinet Server is listening for connection ',client_server_sock.address());
        client_server_sock.on('close',function(){
            console.log('client_Server Terminated');
        });
        client_server_sock.on('error', function(err){
            if(err.code === 'EADDRINUSE'){
                console.log('Addr in use retry...');
                setTimeout(()=>{
                    client_server_sock.close();
                    client_server_sock.listen(3000);
                },3000);
            }
            else{
                console.log('client_server_Socket Error: ',JSON.stringify(err));
            }
        });
    });
    return client_server_sock;
};