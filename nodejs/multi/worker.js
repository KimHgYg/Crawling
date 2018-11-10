var client_sock = require("../Conn/Client_conn.js")(); //creating client-server function
var redis_client = require("../Conn/redis.js").client;
var crawling_sock; //socket
var mong; //mongoose connection

//get crawling sock & mong
redis_client.lrange('Conn',0,-1, (err, arr) => {
     if(err) console.log('redis error : ' + err);
     else {crawling_sock = (arr[0]); 
     mong = (arr[1]);}
});

//get schema
var schema = require("../models/schema.js")(mong); //mongoose schema

//mutex for crawling
var mutex_crawling = require("node-mutex"); //for crawling server mutex


var data;
var tfidf;
var flag = 1;
var label;

//Before assign data, you should check whether this process is busy
//if busy, put it into buffer
//should manage buffer system. -> RR scheduling

crawling_sock.on('data', function(data){
    tfidf = data;
    flag = 0;
});

client_sock.on('data', function(str){
    data = str.split(' ');
    label = data[0];
});

console.log('%d pid worker is connected',process.pid);

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
        tfidf = tfidf.split(' ');
        //find articles data including tfidf
        schema.background_model.find({$or:[
            {tfidf: {"$regex": tfidf[0],"$options":"i"}},
            {tfidf: {"$regex": tfidf[1],"$options":"i"}},
            {tfidf: {"$regex": tfidf[2],"$options":"i"}}
            ]},{_id:0,link:1,tfidf:0},function(err, links){
                if(err) console.error(err + ' before popululate');
                if(links.length == 0) console.log("%d pid worker : found no matching tfidf");
            }).populate('_No').exec(function(err, articles){
                if(err) console.log(err + 'after poplulate');
                writeData(client_sock,articles);//articles == dictionary
            });
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
