var socks = require("server.js");
var schema = require("./models/schema.js");
var mutex_crawling = require("node-mutex");
var DB_conn = socks.DB_conn;
var crawling_sock = socks.crawling_server_sock;

var buffer = [];
var data;
var tfidf;
var flag = 1;
var label;

//Before assign data, you should check whether this process is busy
//if busy, put it into buffer
//should manage buffer system.
process.on('message', function(message){
    data = message.split(' ');
    label = data[0];
});

crawling_sock.on('data', function(data){
    tfidf = data;
    flag = 0;
})

while(1){
    if(label == 0){
        continue;
    }
    else if(label == 1){    //sign up
        console.log('%d pid worker is signing up',process.pid);
        if(data.length != 7){
            console.log('%d pid sign up data is incorrect');
            label = 0;
            continue;
        }
        var values = {ID : data[1], age: data[2], gender: data[3], inter1: data[4],
            inter2: data[5], inter3: data[6]
        };
        schema.user_pri_model(values).save(function(err){
            if(err){console.error(err+ process.pid);}
        });
        console.log('%d pid worker\'s sign up process completed',process.pid);
        label = 0;
    }else if(label == 2){    //login
        //get session if id, pswd are correct
        label = 0;
    }else if(label == 3){    //recommend article list for user get ID from server
                        //send ID to crawling server and receive tfidf for user from there
        console.log('%d pid worker is recommanding',process.pid);
        //var values = {age :};
        mutex_crawling.lock('key').then(function (unlock){
            writeData(crawling_sock,data[1]);
            while(flag);
            flag=1;
            unlock();
        });
        schema.background_model.find({tfidf1: })
        label = 0;
    }else if(label == 4){    //request article list
        
        label = 0;
    }
}

function writeData(socket, data){
    var success = !socket.write(data);
    if(!success){
        (function(socket, data){
            socket.once('drain',function(){
                writeData(socket,data);
            });
        })(socket,data);
    }
}
