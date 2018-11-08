var mongoose = require("mongoose");

var Schema = mongoose.Schema;

var background = new Schema({
    tfidf1:String,
    tfidf2:String,
    tfidf3:String,
    link:String
});

var foreground = new Schema({
    title:String,
    press:String,
    link:String,
    day:Date,
    Class:String
});

var user_info = new Schema({
    ID:String,
    pswd:String
});

var user_pri = new Schema({
    ID:String,
    age:Number,
    gender:String,
    inter1:Number,
    intre2:Number,
    inter3:Number
});

var user_tfidf = new Schema({
    ID:String,
    tfidf:String
});
var    background_model = mongoose.model('background',mongoose.background);
var    foreground_model = mongoose.model('foreground',mongoose.foreground);
var    user_info_model = mongoose.model('user_info',mongoose.user_info);
var    user_pri_model = mongoose.model('user_pri',mongoose.user_pri);
var    user_tfidf_model = mongoose.model('user_tfidf',mongoose.user_tfidf);

module.exports = {
    background_model,
    foreground_model,
    user_tfidf_model,
    user_pri_model,
    user_info_model
};