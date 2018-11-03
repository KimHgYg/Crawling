module.exports = function(app, fs){
    app.get('/',function(req,res){
        var sess = req.session;
        res.render('index',{
            title: "MY HomePage",
            length: 5,
            name : sess.name,
            username: sess.username
        });
    });
    //throw user list
    app.get('/list',function (req,res){
        fs.readFile(__dirname + "/../data/" + "user.json",'utf8',function(err, data){
            if(err) return console.log(err);
            console.log(data);
            res.end(data);
        });
    });
    //throw username's info
    app.get('/getUser/:username', function(req,res){
        fs.readFile(__dirname + '/../data/user.json', 'utf8', function(err, data){
            if(err) return console.log(err);
            var users = JSON.parse(data);
            res.json(users[req.params.username]);
        });
    });
    
    //login
    app.get('/login/:username/:password',function(req, res){
        var sess;
        sess = req.session;
        
        fs.readFile(__dirname + "/../data/user.json",'utf8', function(err, data){
            if(err) {console.log(err); return;}
            var users = JSON.parse(data);
            var username = req.params.username;
            var password = req.params.password;
            var result = {};
            if(!users[username]){
                result["success"] = 0;
                result["error"] = "not found";
                res.json(result);
                return;
            }
            
            if(users[username]["password"] == password){
                result["success"] = 1;
                sess.username = username;
                sess.name = users[username]["name"];
                res.json(result);
            }else{
                result["success"] = 0;
                result["error"] = "incorrect";
                res.json(result);
            }
        });
    });
    
    //logout
    app.get('/logout',function(req,res){
        var sess = req.session;
        if(sess.username){
            req.session.destroy(function(err){
                if(err) console.log(err);
                else res.redirect('/');
            });
        }else{
            res.redirect('/');
        }
    });
    
    //add user (Post)
    app.post('/addUser/:username', function(req,res){
        var result = {};
        var username = req.params.username;
        
        if(!req.body["password"] || !req.body["name"]){
            result["success"] = 0;
            result["error"] = "invalid request";
            res.json(result);
            return;
        }
        
        fs.readFile(__dirname + "/../data/user.json", 'utf8', function(err, data){
            if(err) return console.log(err);
            var users = JSON.parse(data);
            console.log(users);
            if(users[username]){
                result["sucess"] = 0;
                result["error"] = "duplicate";
                res.json(result);
                return;
            }
            
            users[username] = req.body;
            console.log(users);
            fs.writeFile(__dirname + "/../data/user.json", 
                    JSON.stringify(users, null, '\t'), 'utf8', function(err,data){
                if(err) return console.log(err);
                result = {"success":1};
                res.json(result);
            });
        });
    });
    
    
    //update or add user (Get)
    app.put('/updateUser/:username', function(req,res){
        var result = {};
        var username = req.params.username;
        
        if(!req.body["password"] || !req.body["name"]){
            result["success"] = 0;
            result["error"] = "invalid request";
            res.json(result);
            return;
        }
        
        fs.readFile(__dirname + "/../data/user.json", 'utf8', function(err, data){
            if(err) return console.log(err);
            var users = JSON.parse(data);
            
            users[username] = req.body;
            fs.writeFile(__dirname + "/../data/user.json", 
                    JSON.stringify(users, null, '\t'), 'utf8', function(err,data){
                if(err) return console.log(err);
                result = {"success":1};
                res.json(result);
            });
        });
    });
    
    
    //delete username from user list
    app.delete('/deleteUser/:username', function(req, res){
        var result = {};
        
        fs.readFile(__dirname + "/../data/user.json", 'utf8', function(err, data){
            if(err) return console.log(err);
            
            var users = JSON.parse(data);
            
            if(!users[req.params.username]){
                result["success"] = 0;
                result["error"] = "not found";
                res.json(result);
                return;
            }
            
            delete users[req.params.username];
            
            fs.writeFile(__dirname + "/../data/user.json",
                        JSON.stringify(users, null,'\t'), 'utf8', function(err, data){
                            if(err) return console.log(err);
                            
                            result["success"] = 1;
                            res.json(result);
                            return;
                        });
        });
    });
};