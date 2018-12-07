//db-connect mudule
var tunnel = require("tunnel-ssh");
var fs = require("fs");
var mongoose = require("mongoose");
module.exports = {
    //mongodb configure
    Connect : function(crawling_server_sock){
    
        var db = mongoose.connection;
        
        var config = {
            username:'ubuntu',
            host:'52.79.249.174',
            port:22,
            agent:process.env.SSH_AUTH_SOCK,
            privatekey:fs.readFileSync('/home/bitnami/.ssh/id_rsa'),
            dstHost:'127.0.0.1',
            dstPort:27017,
            localHost:'127.0.0.1',
            localPort:27017,
            keepAlive:true
        };
        
        
        
        var db_server = tunnel(config, function(error, server){
            console.log('Tunnel open');
            if(error) console.error(error);
            
            
            db.on('error',console.error.bind(console, 'DB connection error:'));
            db.once('open',function(){
                console.log("DB connection established");
                //cluster
                require("../multi/creator.js")(crawling_server_sock, db);
            });
            mongoose.connect('mongodb://52.79.249.174:27017/crawling',{
                useNewUrlParser:true
            });
        });
        
        return db;
    }
};