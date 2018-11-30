
# coding: utf-8

# In[ ]:


import numpy as np
from keras.layers import *
from keras.models import *
from keras.utils import *
from keras.preprocessing.sequence import *
from keras.preprocessing.text import Tokenizer

from datetime import datetime
import pandas as pd




class rnn:
    split_ratio = 0.8
    max_pad = 15

    def __init__(self, Conn):
        self.Conn = Conn
        self.db = self.Conn.crawling
        self.background = self.db.background
        self.foreground = self.db.foreground
        self.user_tfdif = self.db.user_tfidf

    #training set 생성 여부
    def train_raedy(self):
        return self.train_X is not None

    # load model
    def loadModel(self):
        a = False
        date = input("input date you want to load model format : (yyyymmdd) : ")
        self.model = load_model('relu_model'+date)
        self.sig_model = load_model('sigmoid_model'+date)
        self.model_bi = load_model('bi_relu_model'+date)
        self.model_sig_bi = load_model('bi_sigmoid_model'+date)
        if(self.model):
            print('relu model loaded')
            a = True
        else:
            print('No model relu')
        if(self.sig_model):
            print('sigmoid model loaded')
            a = True
        else:
            print('No model sigmoid')
        if(self.model_bi):
            print('bi relu model loaded')
            a = True
        else:
            print('No model bi relu')
            
        if(self.model_sig_bi):
            print('bi sigmoid model loaded')
            a = True
        else:
            print('No model bi sigmoid')
            
        return a
    
    # bidirectional 모델 만들기!
    #activate = 'tanh'
    #kernel_init = 'glorot_uniform'
    #time_step,  output_shape, model_name_to_save
    #number of feature = 8
    def build_model(self, max_pad, categori_shape):
        activate = 'tanh'
        kernel_init = 'Orthogonal'
        model = Sequential()
        #한 timestep에 한 ID의 데이터 max_pad만큼 들어간다
        model.add(LSTM(256, return_sequences=True, input_shape=(max_pad,8), activation=activate, kernel_initializer = kernel_init))
        #return shape는
        model.add(Dense(categori_shape, activation='sigmoid', kernel_initializer = 'Orthogonal'))

        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

        model.summary()

        return model
    
    def build_model_sigmoid(self, max_pad, categori_shape):
        activate_1 = 'tanh'
        kernel_init = 'glorot_uniform'
        model = Sequential()
        model.add(LSTM(256, return_sequences=True, input_shape=(max_pad,8), activation=activate_1, kernel_initializer = kernel_init))
        model.add(Dense(categori_shape, activation=activate_1, kernel_initializer = kernel_init))

        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

        model.summary()

        return model
    
    def build_model_bi(self, max_pad, categori_shape):
        activate = 'tanh'
        kernel_init = 'Orthogonal'
        model = Sequential()
        model.add(Bidirectional(LSTM(256, return_sequences=True, activation=activate, kernel_initializer = kernel_init), input_shape=(max_pad,8)))
        model.add(Dense(categori_shape, activation='sigmoid', kernel_initializer = 'Orthogonal'))

        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

        model.summary()

        return model
    
    def build_model_sigmoid_bi(self, max_pad, categori_shape):
        activate_1 = 'tanh'
        kernel_init = 'glorot_uniform'
        model = Sequential()
        model.add(Bidirectional(LSTM(256, return_sequences=True, activation=activate_1, kernel_initializer = kernel_init), input_shape=(max_pad,8)))
        model.add(Dense(categori_shape, activation=activate_1, kernel_initializer = kernel_init))

        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

        model.summary()

        return model

    def learning(self, model, train_X, train_Y, test_X, test_Y, model_name):
        history = model.fit(train_X,train_Y, epochs=150, batch_size=1, validation_split=0.1)
        score = model.evaluate(test_X, test_Y)
        model.save(datetime.today().strftime("%Y%m%d")+model_name)
        return (history, score)

    def data_manipulate(self):
        print('Creating training set...')

        #db에서 데이터 불러오기
        user_tfidf_info = self.user_tfidf.find()
        user_pri_info = self.user_pri.find()

        #db에서 불러온 데이터 dataframe형태로 저장
        user_tfidf = pd.DataFrame(user_tfidf_info,columns = ['ID','tfidf'])
        user_pri = pd.DataFrame(user_pri_info,columns = ['ID','age','gender','inter1','inter2','inter3'])

        #tfidf 분할을 위해 따로 drop
        #tfidf
        user_tfidf_value = user_tfidf.drop(columns = ['ID']).values

        #ID
        user_tfidf = user_tfidf.drop(['tfidf'],axis=1)

        tmp = []
        #tfidf 분할
        for arg in user_tfidf_value:
            tmp.append(' '.join(arg).split(' '))

        # tokenizer
        self.token = Tokenizer()

        #tokenizer 학습
        self.token.fit_on_texts(tmp)

        #tfidf value를 tokenizer로 sequence로 바꾼다
        tmp = self.token.texts_to_sequences(tmp)
        
        self.idx_word = {}
        #key 와 value를 바꾼다
        for w in self.token.word_index :
            self.idx_word[self.token.word_index[w]] = w


        #분할 한 tfidf dataframe으로 만든 후 원본과 합친다
        tmp = pd.DataFrame(tmp,columns = ['tfidf','tfidf2','tfidf3'])

        user_tfidf = pd.concat([user_tfidf,tmp],axis=1)

        #tfidf와 사용자 정보를 merge
        merged = pd.merge(user_tfidf,user_pri)

        #ID별로 Y 구하기 위해 추출
        ID = user_tfidf.ID.unique()

        train_X = []
        train_Y = []
        
        #train_X max_pad 만큼 ID별로 데이터 추가하거나 삭제
        for id in ID:
            #ID의 각 원소에 해당하는 ID를 제외한 나머지 값들 transpose 해서 뽑는다
            #pad를 위한 .T
            tmp = merged.loc[merged['ID'] == id,'tfidf':].values.T
            #데이터가 부족한 사용자는 0값으로 더미 데이터 붙여준다
            #다시 .T
            tmp = pad_sequences(tmp,maxlen = self.max_pad).T
            train_X.extend(tmp)

        #(N,max_pad,8)로 reshape
        # max_pad는 한 사용자당 한번에 볼 데이터 수
        #위에서 pad_sequence 했기 때문에 ID데이터가 서로 섞이는 경우 없다
        # 8 은 각 데이터당 feature의 수
        #한 timpstep에 max pad만큼의 데이터가 들어있다
        train_X = np.array(train_X)[:,np.newaxis].reshape(-1,self.max_pad,8)

        #ID별로 train_Y

        for id in ID:
            #각 ID별로 tfidf값만 추출
            user_private = merged.loc[merged['ID'] == id, 'tfidf' : 'tfidf3' ].values.T
            #pad_sequence로 데이터 수 맞춰준다.
            user_private = pad_sequences(user_private, maxlen=self.max_pad).T
            # 각 ID별로 데이터를 하나씩 이동시킨다
            user_private = np.vstack((user_private[1:],user_private[0]))
            train_Y.extend(user_private)

        tmp = []
        self.categori = to_categorical(np.array(train_Y).reshape(-1,3))
        #one-hot 표현으로 바꾼다
        #데이터별로 to_categorical 하면 데이터 원소만큼 나눠져서 categorical 된다
        for target in self.categori:
            # 나눠진거 다시 합침
            tmp.append(sum(target))

        #한 timestep에 max_pad만큼의 Y값
        train_Y = np.array(tmp)[:,np.newaxis].reshape(-1,self.max_pad,len(tmp[0]))

        self.train_X = train_X
        self.train_Y = train_Y
        print('training set created, ready to build model')
        return
    
    def build_learn_all(self):
        #모델 구축
        split = int(len(self.train_X)*self.split_ratio)
        self.model = self.build_model(self.max_pad, self.train_Y.shape[2])
        self.model_sig = self.build_model_sigmoid(self.max_pad, self.train_Y.shape[2])
        self.model_bi = self.build_model_bi(self.max_pad, self.train_Y.shape[2])
        self.model_sig_bi = self.build_model_sigmoid_bi(self.max_pad, self.train_Y.shape[2])
        
        #모델 run
        (history, score) = self.learning(self.model, self.train_X[:split],self.train_Y[:split],self.train_X[split:],self.train_Y[split:],'_relu')
        (history2, score2) = self.learning(self.model_sig, self.train_X[:split],self.train_Y[:split],self.train_X[split:],self.train_Y[split:],'_sigmoid')
        (history3, score3) = self.learning(self.model_bi, self.train_X[:split],self.train_Y[:split],self.train_X[split:],self.train_Y[split:],'_relu_bi')
        (history4, score4) = self.learning(self.model_sig_bi, self.train_X[:split],self.train_Y[:split],self.train_X[split:],self.train_Y[split:],'_sigmoid_bi')

        return
    
    def build_learn_model(self):
        print('building relu model...')
        split = int(len(self.train_X)*self.split_ratio)
        self.model = self.build_model(self.max_pad, self.train_Y.shape[2])
        (history, score) = self.learning(self.model, self.train_X[:split],self.train_Y[:split],self.train_X[split:],self.train_Y[split:],'_relu')

        self.model.save('relu_model'+datetime.today().strftime("%Y%m%d"))
        print('relu model done')
        return
    
    def build_learn_model_sig(self):
        print('building sigmoid model')
        split = int(len(self.train_X)*self.split_ratio)
        self.model_sig = self.build_model_sigmoid(self.max_pad, self.train_Y.shape[2])
        (history, score) = self.learning(self.model_sig, self.train_X[:split],self.train_Y[:split],self.train_X[split:],self.train_Y[split:],'_relu')

        self.model.save('sigmoid_model'+datetime.today().strftime("%Y%m%d"))
        print('sigmoid model done')
        return
    
    def build_learn_model_bi(self):
        print('building bidirectional relu model')
        split = int(len(self.train_X)*self.split_ratio)
        self.model_bi = self.build_model_bi(self.max_pad, self.train_Y.shape[2])
        (history, score) = self.learning(self.model_bi, self.train_X[:split],self.train_Y[:split],self.train_X[split:],self.train_Y[split:],'_relu')

        self.model.save('bi_relu_model')
        print('bidirectional relu model done'+datetime.today().strftime("%Y%m%d"))
        return
    
    def build_learn_model_sig_bi(self):
        print('building bidirectional sigmoid model')
        split = int(len(self.train_X)*self.split_ratio)
        self.model_sig_bi = self.build_model_sig_bi(self.max_pad, self.train_Y.shape[2])
        (history, score) = self.learning(self.model_sig_bi, self.train_X[:split],self.train_Y[:split],self.train_X[split:],self.train_Y[split:],'_relu')

        self.model.save('bi_sigmoid_model'+datetime.today().strftime("%Y%m%d"))
        print('sigmoid model done')
        return

    def precit_model(self, X):
        if self.model is None:
            return False
        pred = self.model.predict(X)
        pred = np.argmax(pred, axis=2)
        temp = []
        for I in pred:
            for w in I:
                if w != 0:
                    temp.append(self.idx_word[w])
        _No = self.background.find({"$or": [
            {"tfidf": {"$regex": temp[0], "$options": "i"}},
            {"tfidf": {"$regex": temp[1], "$options": "i"}},
            {"tfidf": {"$regex": temp[2], "$options": "i"}}
        ]}, {"_No": 1, "tfidf": 0, "link": 0})
        Content = self.foreground.find({"_No": {"$in": _No}}, {"_No": 0, "title.Class": 1})

        return Content
    
    def precit_model_sig(self, X):
        if self.model_sig is None:
            return False
        pred = self.model_sig.predict(X)
        pred = np.argmax(pred, axis=2)
        temp = []
        for I in pred:
            for w in I:
                if w != 0:
                    temp.append(self.idx_word[w])
        _No = self.background.find({"$or": [
            {"tfidf": {"$regex": temp[0], "$options": "i"}},
            {"tfidf": {"$regex": temp[1], "$options": "i"}},
            {"tfidf": {"$regex": temp[2], "$options": "i"}}
        ]}, {"_No": 1, "tfidf": 0, "link": 0})
        Content = self.foreground.find({"_No": {"$in": _No}}, {"_No": 0, "title.Class": 1})

        return Content
    
    def precit_model_bi(self, X):
        if self.model_bi is None:
            return False
        pred = self.model_bi.predict(X)
        pred = np.argmax(pred, axis=2)
        temp = []
        for I in pred:
            for w in I:
                if w != 0:
                    temp.append(self.idx_word[w])
        _No = self.background.find({"$or": [
            {"tfidf": {"$regex": temp[0], "$options": "i"}},
            {"tfidf": {"$regex": temp[1], "$options": "i"}},
            {"tfidf": {"$regex": temp[2], "$options": "i"}}
        ]}, {"_No": 1, "tfidf": 0, "link": 0})
        Content = self.foreground.find({"_No": {"$in": _No}}, {"_No": 0, "title.Class": 1})

        return Content
    
    def precit_model_sig_bi(self, X):
        if self.model_sig_bi is None:
            return False
        pred = self.model_sig_bi.predict(X)
        pred = np.argmax(pred, axis=2)
        temp = []
        for I in pred:
            for w in I:
                if w != 0:
                    temp.append(self.idx_word[w])
        _No = self.background.find({"$or":[
            {"tfidf": {"$regex": temp[0],"$options":"i"}},
            {"tfidf": {"$regex": temp[1],"$options":"i"}},
            {"tfidf": {"$regex": temp[2],"$options":"i"}}
            ]},{"_No":1,"tfidf":0,"link":0})
        Content = self.foreground.find({"_No": {"$in" : _No}},{"_No":0, "title.Class":1})

        return Content