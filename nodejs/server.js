//init server 
//var fs = require("fs");
//var mongoose = require("mongoose");

//init redis

//init sockets
//require("./Conn/Crawling_conn.js")();


//db.Connect(mongoose,fs);


//module.exports = {
    //DB_conn : DB_conn,
    //client_server : socks.client_server,  //function port 3000
    //crawling_server_sock : crawling_server_sock,    //server port 3002
    //worker : worker
//};




/*
/Express module -- not used

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