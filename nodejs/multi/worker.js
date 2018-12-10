console.log('%d pid worker is connected',process.pid);
var client_server_sock = require("../Conn/Client_conn.js")(); //creating client-server function
var crawling_server_sock = require("../Conn/Crawling_conn")(); // crawling socket
var mong = require("../Conn/DB_conn").Connect(); //mongoose connection


//get schema
var schema = require("../models/schema.js")(mong); //mongoose schema


var data;
var recommendation;
var label = 0;


//Before assign data, you should check whether this process is busy
//if busy, put it into buffer
//should manage buffer system. -> RR scheduling

var client_sock;
var crawling_sock;
crawling_server_sock.on('connect',(c)=>{
    crawling_sock = c;
    c.on('data', function(data){
        recommendation = data;
    });
});


//data : 'type', 'content'
client_server_sock.on('connection',(c)=>{
    cleint_sock = c;
    c.on('data', function(str){
        data = str.split(' ');
        label = data[0];
    });
});

while(1){
    if(label == 0){
        continue;
    }
    else if(label == 1){    //sign up, give user info ID, age, gender, ineter 1,2,3,
                            //interact directly with db
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
    }else if(label == 3){
        //get recommandation from crawling server, give ID
        console.log('%d pid worker is recommending',process.pid);
                                //ID
        writeData(crawling_sock,data[1],() => {writeData(client_sock,recommendation)});

        //find articles data including recommendation
        label = 0;
    }else if(label == 4){    //request article list
        //get directly from db
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
};