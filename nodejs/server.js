//init server 

var express = require("express");
var app = express();
var bodyParser = require("body-parser");
var session = require("express-session");
var fs = require("fs");
var mongoose = require("mongoose");

//cluster
var worker = require("./mutli.creator.js");

//init sockets
var socks = require("./Conn/sock_server.js")();

//init mongoose
var db = require("./Conn/DB_conn.js");
var DB_conn = db.Connect(mongoose,fs);


module.exports = {
    DB_conn : DB_conn,
    client_server_sock : socks[0],  //port 3000
    crawling_server_sock : socks[1],    //port 3002
    worker : worker
}


/*
//REST API -- not used

app.set('views',__dirname + '/views');
app.set('view engine','ejs');
app.engine('html',require('ejs').renderFile);

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
*/