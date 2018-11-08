var cluster = require("cluster");

var num_thread = 5;

//round robin scheduling
cluster.schedulingPolicy = cluster.SCHED_RR;
cluster.setupMaster({
    exec: './multi/worker.js'
});

var worker = [];

//master
console.log('Creating Cluster');
for(var t=0;t<num_thread;t++){
    worker[t] = cluster.fork();
    
    worker[t].on('online',function(worker){
        console.log('Created Worker ID : '+ worker.process.pid);
    });
    
    worker[t].on('exit',function(worker, code, signal){
        console.log('Exit worker ID : ' +worker.process.pid);
        console.log('Exit worker exit code : ' + code);
        console.log('Exit worker signal : ' + signal);
    });
};

module.exports(worker);