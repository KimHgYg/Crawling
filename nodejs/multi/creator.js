module.exports = function(){
    var cluster = require("cluster");
    //var num_thraed = require('os').cpus().length;
    var num_thread = 4;
    //create worker thread and start
    //master
    if(cluster.isMaster){
        var worker = [];
        //round robin scheduling
        cluster.schedulingPolicy = cluster.SCHED_RR;
        cluster.setupMaster({
            exec: "../multi/worker.js",
        });
        
        console.log('Creating Cluster');
        for(var t=0;t<num_thread;t++){
            worker[t] = cluster.fork();
        }
        
        cluster.on('exit',function(worker, code, signal){
            if(Object.keys(cluster.workers).length == 0)
                console.log('All worker shut down, cluster closeing');
            console.log('Exit worker ID : ' +worker.process.pid);
            console.log('Exit worker exit code : ' + code);
            console.log('Exit worker signal : ' + signal);
            //cluster.fork();
        });
        cluster.on('online',function(worker){
                console.log('Created Worker ID : '+ worker.process.pid);
        });
    }
};