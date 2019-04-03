
#  coding: utf-8

#  In[ ]:

from keras.layers import *
from keras.models import *
from keras.utils import *
from keras.preprocessing.sequence import *

from datetime import datetime
import pandas as pd

import model

class Rnn:
    split_ratio = 0.8
    max_pad = 15

    def __init__(self, conn, vocab):
        self.vocab = vocab
        self.conn = conn
        self.db = conn.get_database('crawling')
        self.user_tfidf = self.db.get_collection('user_tfidfs')
        self.user_pri = self.db.get_collection('user_pris')
        self.mysql_conn = model.model()
        self.model = None
        self.sig_model = None
        self.model_bi = None
        self.model_sig_bi = None
        self.categori_shape = None
        self.categori = None
        self.train_x = None
        self.train_y = None

    # training set 생성 여부
    def train_ready(self):
        return self.train_x is not None

    #  load model
    def load_model(self):
        a = False
        date = input("input date you want to load model format : (yyyymmdd) : ")
        self.model = load_model('relu_model'+date)
        self.sig_model = load_model('sigmoid_model'+date)
        self.model_bi = load_model('bi_relu_model'+date)
        self.model_sig_bi = load_model('bi_sigmoid_model'+date)
        if self.model:
            print('relu model loaded')
            a = True
        else:
            print('No model relu')
        if self.sig_model:
            print('sigmoid model loaded')
            a = True
        else:
            print('No model sigmoid')
        if self.model_bi:
            print('bi relu model loaded')
            a = True
        else:
            print('No model bi relu')
            
        if self.model_sig_bi:
            print('bi sigmoid model loaded')
            a = True
        else:
            print('No model bi sigmoid')
            
        return a
    
    #  bidirectional 모델 만들기!
    # activate = 'tanh'
    # kernel_init = 'glorot_uniform'
    # time_step,  output_shape, model_name_to_save
    # number of feature = 8
    def build_model(self):
        activate = 'tanh'
        kernel_init = 'Orthogonal'
        model = Sequential()
        # 한 timestep에 한 ID의 데이터 max_pad만큼 들어간다
        model.add(LSTM(256, return_sequences=True, input_shape=(self.max_pad, 8), activation=activate, kernel_initializer=kernel_init))
        # return shape는
        model.add(Dense(self.categori_shape, activation='sigmoid', kernel_initializer = 'Orthogonal'))

        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

        model.summary()

        return model
    
    def build_model_sigmoid(self):
        activate_1 = 'tanh'
        kernel_init = 'glorot_uniform'
        model = Sequential()
        model.add(LSTM(256, return_sequences=True, input_shape=(self.max_pad,8), activation=activate_1, kernel_initializer = kernel_init))
        model.add(Dense(self.categori_shape, activation=activate_1, kernel_initializer = kernel_init))

        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

        model.summary()

        return model
    
    def build_model_bi(self):
        activate = 'tanh'
        kernel_init = 'Orthogonal'
        model = Sequential()
        model.add(Bidirectional(LSTM(256, return_sequences=True, activation=activate, kernel_initializer = kernel_init), input_shape=(self.max_pad,8)))
        model.add(Dense(self.categori_shape, activation='sigmoid', kernel_initializer='Orthogonal'))

        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

        model.summary()

        return model
    
    def build_model_sigmoid_bi(self):
        activate_1 = 'tanh'
        kernel_init = 'glorot_uniform'
        model = Sequential()
        model.add(Bidirectional(LSTM(256, return_sequences=True, activation=activate_1, kernel_initializer=kernel_init), input_shape=(self.max_pad, 8)))
        model.add(Dense(self.categori_shape, activation=activate_1, kernel_initializer=kernel_init))

        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

        model.summary()

        return model

    def learning(self, model, train_X, train_Y, test_X, test_Y, model_name):
        history = model.fit(train_X, train_Y, epochs=150, batch_size=1, validation_split=0.1)
        score = model.evaluate(test_X, test_Y)
        model.save(datetime.today().strftime("%Y%m%d")+model_name)
        return history, score

    def data_manipulate(self):
        print('Creating training set...')

        # db에서 데이터 불러오기
        user_tfidf_info = self.user_tfidf.find({'ID', 'tfidf1', 'tfidf2', 'tfidf3'})
        user_pri_info = self.user_pri.find({'ID', 'age', 'gender', 'inter1', 'inter2', 'inter3'})

        if user_tfidf_info.count() == 0:
            print("열람 기록이 없습니다.")
            return

        if user_pri_info.count() == 0:
            print("사용자 정보가 없습니다.")
            return

        # db에서 불러온 데이터 dataframe형태로 저장
        user_tfidf = pd.DataFrame(user_tfidf_info, columns=['ID', 'tfidf1', 'tfidf2', 'tfidf3'])
        user_pri = pd.DataFrame(user_pri_info, columns=['ID', 'age', 'gender', 'inter1', 'inter2', 'inter3'])
        # 각 데이터의 값을 0 - 1 로 scailing
        user_pri.age /= 80
        user_pri.inter1 /= 6
        user_pri.inter2 /= 6
        user_pri.inter3 /= 6

        user_tfidf.tfidf1 /= len(user_tfidf.size)
        user_tfidf.tfidf2 /= len(user_tfidf.size)
        user_tfidf.tfidf3 /= len(user_tfidf.size)

        # tfidf 분할을 위해 따로 drop
        # tfidf
        # user_tfidf_value = user_tfidf.drop(columns = ['_id']).values
        tmp = user_tfidf.drop(columns=['ID']).values

        # ID
        user_tfidf = user_tfidf['ID']

        # tmp = []
        # tfidf 분할
        # for arg in user_tfidf_value:
         #    tmp.append(' '.join(arg).split(' '))
        '''
        background 저장 시 vocab의 index로 저장하기 때문에 문자열 정수로 변환 필요 없다
        #  tokenizer
        self.token = Tokenizer()

        # tokenizer 학습
        self.token.fit_on_texts(tmp)
        
        # tfidf value를 tokenizer로 sequence로 바꾼다
        tmp = self.token.texts_to_sequences(tmp)
        

        self.idx_word = {}
        # key 와 value를 바꾼다
        for w in self.token.word_index:
            self.idx_word[self.token.word_index[w]] = w
        '''

        # 분할한 tfidf dataframe으로 만든 후 원본과 합친다
        tmp = pd.DataFrame(tmp, columns=['tfidf1', 'tfidf2', 'tfidf3'])

        user_tfidf = pd.concat([user_tfidf, tmp],axis=1)

        # tfidf와 사용자 정보를 merge merge는 inner join -> index가 안겹치면 결과에서 제외
        merged = pd.merge(user_tfidf, user_pri, on=['ID'])

        # ID별로 Y 구하기 위해 추출
        ID = user_tfidf.ID.unique()

        train_x = []
        train_y = []
        
        #  train_x max_pad 만큼 ID별로 데이터 추가하거나 삭제
        for _id in ID:
            #  ID의 각 원소에 해당하는 ID를 제외한 나머지 값들 transpose 해서 뽑는다
            #  pad를 위한 .T
            tmp = merged.loc[merged['ID'] == _id, 'tfidf1':].values.T
            #  데이터가 부족한 사용자는 -1 값으로 더미 데이터 붙여준다
            #  다시 .T
            tmp = pad_sequences(tmp, maxlen=self.max_pad, value=-1).T
            train_x.extend(tmp)

        #  (N,max_pad,8)로 reshape
        #  max_pad는 한 사용자당 한번에 볼 데이터 수
        #  위에서 pad_sequence 했기 때문에 ID데이터가 서로 섞이는 경우 없다
        #  8 은 각 데이터당 feature의 수
        #  한 timpstep에 max pad만큼의 데이터가 들어있다
        train_x = np.array(train_x)[:, np.newaxis].reshape(-1, self.max_pad, 8)
        # 0-1 의 값으로 scaling

        #  ID별로 train_y

        for _id in ID:
            #  각 ID별로 tfidf값만 추출
            user_private = merged.loc[merged['ID'] == _id, 'tfidf1':'tfidf3'].values.T
            #  pad_sequence로 데이터 수 맞춰준다.
            user_private = pad_sequences(user_private, maxlen=self.max_pad).T
            #  각 ID별로 데이터를 하나씩 이동시킨다
            user_private = np.vstack((user_private[1:], user_private[0]))
            train_y.extend(user_private)

        tmp = []

        category = to_categorical(np.array(train_y).reshape(-1, 3))

        # one-hot 표현으로 바꾼다
        # 데이터별로 to_categorical 하면 데이터 원소만큼 나눠져서 categorical 된다
        for target in category:
            #  나눠진거 다시 합침
            tmp.append(sum(target))

        # 한 timestamp 에 max_pad 만큼의 Y값
        self.categori_shape = len(tmp[0])
        train_y = np.array(tmp).reshape(-1, self.max_pad, self.categori_shape)

        self.train_x = train_x
        self.train_y = train_y
        print('training set created, ready to build model')
        return
    
    def learn_model(self):
        if self.model is None:
            print("모델이 없습니다.")
            return
        print('building relu model...')
        split = int(len(self.train_x) * self.split_ratio)
        (history, score) = self.learning(self.model, self.train_x[:split], self.train_y[:split],
                                         self.train_x[split:], self.train_y[split:], '_relu')

        self.model.save('relu_model'+datetime.today().strftime("%Y%m%d"))
        print('relu model done')
        return
    
    def learn_model_sig(self):
        if self.model_sig is None:
            print("모델이 없습니다.")
            return
        print('building sigmoid model')
        split = int(len(self.train_x) * self.split_ratio)
        (history, score) = self.learning(self.model_sig, self.train_x[:split], self.train_y[:split],
                                         self.train_x[split:], self.train_y[split:], '_relu')

        self.model.save('sigmoid_model'+datetime.today().strftime("%Y%m%d"))
        print('sigmoid model done')
        return
    
    def learn_model_bi(self):
        if self.model_bi is None:
            print("모델이 없습니다.")
            return
        print('building bidirectional relu model')
        split = int(len(self.train_x) * self.split_ratio)
        (history, score) = self.learning(self.model_bi, self.train_x[:split], self.train_y[:split],
                                         self.train_x[split:], self.train_y[split:], '_relu')

        self.model.save('bi_relu_model')
        print('bidirectional relu model done'+datetime.today().strftime("%Y%m%d"))
        return
    
    def learn_model_sig_bi(self):
        if self.model_sig_bi is None:
            print("모델이 없습니다.")
            return
        print('building bidirectional sigmoid model')
        split = int(len(self.train_x) * self.split_ratio)
        (history, score) = self.learning(self.model_sig_bi, self.train_x[:split], self.train_y[:split],
                                         self.train_x[split:], self.train_y[split:], '_relu')

        self.model.save('bi_sigmoid_model'+datetime.today().strftime("%Y%m%d"))
        print('sigmoid model done')
        return

    def predict_model(self, _id):
        if self.model is None:
            return False

        #  db에서 데이터 불러오기
        user_tfidf_info = pd.DataFrame(self.user_tfidf.find({'ID', 'tfidf1', 'tfidf2', 'tfidf3'}))
        user_pri_info = pd.DataFrame(self.user_pri.find({'ID', 'age', 'gender', 'inter1', 'inter2', 'inter3'}))

        # 위 두 데이터 ID로 조인 merge는 inner join이라 없으면 지우기 때문에 join사용
        joined = user_tfidf_info.join(user_pri_info.set_index('ID'), on='ID').fillna(-1)
        # ID를 제외한 값
        data = joined.loc[joined['ID' == _id]].drop(columns='ID').values
        #부족하거나 넘치는 데이터 padding 한다
        data = pad_sequences(data.T, maxlen=self.max_pad, value=-1).T

        # model을 이용 키워드 추천
        pred = self.model.predict(data)
        # 0.5 보다 큰 값의 키워드는 1로 나머지는 0으로
        get = lambda x: 1 if x > 0.5 else 0.5
        pred = [get(i) for i in pred]

        # 값이 1인 key의 index를 추가
        ret = []
        for index, key in enumerate(pred):
            if key is 1:
                ret.append(index)

        # 각 인덱스를 DB에서 찾은 후 set에 넣는다
        ret_set = set([])
        for key in ret:
            key = str(key)
            set.update(self.mysql_conn.selectBackgrounds(
                projection='id', join='tfidf1 = ' + key + ' or tfidf2 = ' + key + ' or tfidf3 = ' + key))
        '''
        _No = self.background.find({"$or": [
            {"tfidf": {"$regex": temp[0], "$options": "i"}},
            {"tfidf": {"$regex": temp[1], "$options": "i"}},
            {"tfidf": {"$regex": temp[2], "$options": "i"}}
        ]}, {"_No": 1, "tfidf": 0, "link": 0})
        content = self.foreground.find({"_No": {"$in": _No}}, {"_No": 0, "title.Class": 1})
        '''
        return list(ret_set)
    
    def predict_model_sig(self, X):
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
        content = self.foreground.find({"_No": {"$in": _No}}, {"_No": 0, "title.Class": 1})

        return content
    
    def predict_model_bi(self, X):
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
        content = self.foreground.find({"_No": {"$in": _No}}, {"_No": 0, "title.Class": 1})

        return content
    
    def predict_model_sig_bi(self, X):
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
        content = self.foreground.find({"_No": {"$in" : _No}},{"_No":0, "title.Class":1})

        return content