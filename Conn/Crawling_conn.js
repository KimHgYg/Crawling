var net = require("net");


module.exports = function (redis_client){
    var crawling_server_sock;
    var crawling_server = net.createServer((crawling_sock) => {
        crawling_server_sock = crawling_sock;
        console.log('Crawling Connected ');
        console.log('   local = %s:%s', crawling_server_sock.localAddress, crawling_server_sock.localPort);
        console.log('   remote = %s:%s', crawling_server_sock.remoteAddress, crawling_server_sock.remotePort);
        crawling_server_sock.setEncoding('utf8');
        crawling_server_sock.setKeepAlive();
        crawling_server_sock.on('end',function(){
            console.log('Crawling server disconnected');
        });
        crawling_server_sock.on('error',function(err){
            console.log('crawling_Socket Error: ',JSON.stringify(err));
        });
    });
    crawling_server.listen(3002,() => {
        console.log('Crawling Server listening for connection');
        crawling_server.on('close',function(){
            console.log('Crawling Server Terminated');
        });
        crawling_server.on('error', function(err){
            console.log('Crawling Server Error: ', JSON.stringify(err));
        });
        crawling_server.on('connection',function(){
            //init mongoose
            require("./DB_conn.js").Connect(crawling_server_sock);
        });
    });
    return crawling_server_sock;
};