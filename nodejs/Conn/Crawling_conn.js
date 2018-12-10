var net = require("net");

var crawling_conn;
module.exports = function (){
    crawling_conn = net.connect({host:'192.168.0.5',port:'3002'}, () => {
        console.log('crawling connected ');
        console.log('   local = %s:%s', crawling_conn.localAddress, crawling_conn.localPort);
        console.log('   remote = %s:%s', crawling_conn.remoteAddress, crawling_conn.remotePort);
        crawling_conn.setEncoding('utf8');
        crawling_conn.setKeepAlive();
        crawling_conn.on('end',() => {
            console.log('crawling server disconnected\n trying reconnect');
            this();
        });
        crawling_conn.on('close',(err)=>{
            console.log(err);
            crawling_conn.close();
            this();
        });
        crawling_conn.on('error',(err)=>{
            console.log(err, 'retry...');
            crawling_conn.close();
            this();
        });
    });
    return crawling_conn;
};