module.exports = function(mongoose){
    var Schema = mongoose.Schema;
    
    var background = new Schema({
        _No: [{ type: Schema.Types.ObjectId, ref: 'foreground' }],
        tfidf:String,
        link:String,
    });
    
    var foreground = new Schema({
        _No:Schema.Types.ObjectId,
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
    var    background_model = mongoose.model('background',background);
    var    foreground_model = mongoose.model('foreground',foreground);
    var    user_info_model = mongoose.model('user_info',user_info);
    var    user_pri_model = mongoose.model('user_pri',user_pri);
    var    user_tfidf_model = mongoose.model('user_tfidf',user_tfidf);
    return {
        background_model : background_model,
        foreground_model :foreground_model,
        user_info_model :user_tfidf_model,
        user_pri_model :user_pri_model,
        user_info_model :user_info_model
    }
};