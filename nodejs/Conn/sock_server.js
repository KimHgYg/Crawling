var net = require("net");

module.exports = function create_Server() {
    var client_server_sock;
    var crawling_server_sock;
    var server = net.createServer(function(client_server_sock){
        console.log('client_server connected');
        console.log('   local = %s:%s', client_server_sock.localAddress, client_server_sock.localPort);
        console.log('   remote = %s:%s', client_server_sock.remoteAddress, client_server_sock.remotePort);
        client_server_sock.setTimeout(500);
        client_server_sock.setEncoding('utf8');
        
        client_server_sock.on('end',function(){
            console.log('client_server_sock disconnectd;);');
            server.getConnections(function(err, count){
                if(err){console.error(err);}
                console.log('Remaining Connections : ' + count);
            });
        });
        
        client_server_sock.on('error', function(err){
            console.log('client_server_Socket Error: ',JSON.stringify(err));
        });
        //if use timeout, implements heartbeat
        client_server_sock.on('timeout',function(){
            console.log('client_server_Socket Time out');
        });
    });
    
    var crawling_server = net.createServer(function(crawling_server_sock){
        console.log('Crawling Server connected');
        console.log('   local = %s:%s', crawling_server_sock.localAddress, crawling_server_sock.localPort);
        console.log('   remote = %s:%s', crawling_server_sock.remoteAddress, crawling_server_sock.remotePort);
        crawling_server_sock.setEncoding('utf8');

        crawling_server_sock.on('end',function(){
            console.log('Crawling server disconnected');
        });
        crawling_server_sock.on('error',function(err){
            console.log('crawling_Socket Error: ',JSON.stringify(err));
        });
    });

    server.listen(3000,function(){
        console.log('Clinet Server listening for connection');
        server.on('close',function(){
            console.log('crawling_Server Terminated');
        });
        server.on('error', function(err){
            console.log('client_Server Error: ', JSON.stringify(err));
        });
    });
    
    crawling_server.listen(3002,function(){
        console.log('Crawling Server listening for connection');
        crawling_server.on('close',function(){
            console.log('Crawling Server Terminated');
        });
        crawling_server.on('error', function(err){
            console.log('Crawling Server Error: ', JSON.stringify(err));
        });
    });
    
    return {client_server_sock, crawling_server_sock};
};