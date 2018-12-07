import Crawling_func
import RNN
import Server

import logging
import multiprocessing

from pymongo import MongoClient

class Main_Program:

    # 프로그램 객체 생성
    def __init__(self):
        #몽고디비와 연결 객체
        self.Conn = MongoClient('52.79.249.174', 27017)
        print('DB connected')
        #크롤링객체 생성
        self.Crawling = Crawling_func.crawling_func(self.Conn)
        print('Crawling object created')
        #모델 객체 생성
        self.model_obj = RNN.rnn(self.Conn)
        print('model object created')

    #크롤링...
    #크롤링 객체, RNN 객체, _id 값

        #training set 생성

    #메뉴 생성 및 실제 프로그램 run
    def run_program(self):
        multiprocessing.log_to_stderr()
        logger = multiprocessing.get_logger()
        logger.setLevel(logging.INFO)

        p = None

        #  Menu
        while True:
            menu = int(input("1 : crawling " +
                             "2 : load model " +
                             "3 : build model " +
                             "4 : learn model " +
                             "5 : open socket for recommendation\n" +
                             "6 : exit program (warn : Data will be deleted)\n"))
            #  start crawling -- blocked
            if menu == 1:
                self.Crawling.crawling()
                self.model_obj.data_manipulate()
            # load model --blocked
            elif menu == 2:
                if (self.model_obj.loadModel() == False):
                    print("There's no saved model, please build model first\n")

            # build model -- blocked
            elif menu == 3:
                p = int(input("1 : build relu model\n" +
                              "2 : build sigmoid model\n" +
                              "3 : build bidirectional relu model\n" +
                              "4 : build bidirectional sigmoid model\n"))
                if (p == 1):
                    self.model_obj.build_model()
                elif (p == 2):
                    self.model_obj.build_model_sig()
                elif (p == 3):
                    self.model_obj.build_model_bi()
                elif (p == 4):
                    self.model_obj.build_model_sig_bi()
            elif menu == 4:
                if (self.model_obj.train_ready() == False):
                    print("Training set not exist")
                    continue
                p = int(input("1: learn relu model\n" +
                              "2 : learn sigmoid model\n" +
                              "3 : learn bidirectional relu model\n" +
                              "4 : learn bidirectional sigmoid model\n"))
                if (p == 1):
                    self.model_obj.laern_model()
                elif (p == 2):
                    self.model_obj.learn_model_sig()
                elif (p == 3):
                    self.model_obj.learn_model_bi()
                elif (p == 4):
                    self.model_obj.learn_model_sig_bi()

            # start recommand program
            elif menu == 5:
                self.server = Server('0.0.0.0',3002,self.model_obj)
                self.server.start_server()

            elif menu == 6:
                print("Exitting program")
                break

        return

if __name__ == '__main__':
    print("Initiate program")
    main = Main_Program()
    print("Progarm is running")
    main.run_program()
