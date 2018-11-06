var express = require("express");
var app = express();
var bodyParser = require("body-parser");
var session = require("express-session");
var fs = require("fs");

app.set('views',__dirname + '/views');
app.set('view engine','ejs');
app.engine('html',require('ejs').renderFile);

//db-connect mudule
module.exports = function(mongoose){
    var tunnel = require("tunnel-ssh");
    
    //mongodb configure
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
    var db = mongoose.connection;
    
    var db_server = tunnel(config, function(error, server){
        console.log('Tunnel open');
        if(error) console.error(error);
        
        
        db.on('error',console.error.bind(console, 'DB connection error:'));
        db.once('open',function(){
            console.log("DB connection established");
        });
        mongoose.connect('mongodb://52.79.249.174:27017/crawling',{
            useNewUrlParser:true
        });
    });
};

//port connect and listen
var port = process.env.PORT || 8080;
var server = app.listen(port, function() {
    console.log("Express server has satrted on port "+port);
});

//express configure
app.use(express.static('public'));

//body-parser configure
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended:true}));


//session configure
app.use(session({
    secret:'@#@$MYSIGN#@$#$',
    resave : false,
    saveUninitialized: true
}));

var router = require('./router/main')(app, fs);