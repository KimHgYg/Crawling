module.exports = function(crawling_sock, mong){
    var cluster = require("cluster");
    
    //push crawling socket & mongoose into redis
    var redis_client = require("../Conn/redis.js").client;
    
    redis_client.on('error',function(err){
        console.log("redis error : " + err);
    });
    
    redis_client.rpush('Conn',[(crawling_sock), (mong)]);
    
    //var os = require("os");
    //var num_thread = os.cpus().length;
    
    var num_thread = 4;
    
    //master
    if(cluster.isMaster){
        var worker = [];
        //round robin scheduling
        cluster.schedulingPolicy = cluster.SCHED_RR;
        cluster.setupMaster({
            exec: "./multi/worker.js",
        });
        console.log('Creating Cluster');
        for(var t=0;t<num_thread;t++){
            worker[t] = cluster.fork();
        }
        
        cluster.on('exit',function(worker, code, signal){
            console.log('Exit worker ID : ' +worker.process.pid);
            console.log('Exit worker exit code : ' + code);
            console.log('Exit worker signal : ' + signal);
        });
        cluster.on('online',function(worker){
                console.log('Created Worker ID : '+ worker.process.pid);
        });
        
        cluster.on('exit',function(){
            if(Object.keys(cluster.workers).length == 0)
                console.log('All worker shut down, cluster closeing');
        });
    }
};