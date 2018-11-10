var redis = require("redis");
var client;
module.exports = {
    init : function(){
        client = redis.createClient();
            
        client.on('error',function(err){
            console.log("redis error : " + err);
        });
        client.on('connect',()=>{
            console.log('redit connected');
            require("../Conn/Crawling_conn.js")();
        })
    },
    client : client,
};