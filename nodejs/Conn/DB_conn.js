//db-connect mudule
var mongoose = require("mongoose");
module.exports = {
    //mongodb configure
    Connect : function(){
        mongoose.connect('mongodb://localhost:27017/crawling',{
            useNewUrlParser:true
        },(error)=>{
            console.log(error, 'trying reconnect..');
            this.Connect();
        });
        console.log('db connected');
        return mongoose;
    }
};