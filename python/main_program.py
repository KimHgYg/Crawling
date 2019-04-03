import Crawling_func
import RNN
import Server

import logging
import multiprocessing
import pymongo


class Main_Program:

    # 프로그램 객체 생성
    def __init__(self):
        #MongoDB와 연결
        self.Conn = pymongo.MongoClient('127.0.0.1', 27017)
        #MySQL과 연결 객체
        #크롤링객체 생성
        self.Crawling = Crawling_func.crawling_func()
        print('Crawling object created')
        self.model_obj = None


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
                             "2 : make training set" +
                             "3 : load model " +
                             "4 : build model " +
                             "5 : learn model " +
                             "6 : open socket for recommendation\n" +
                             "7 : exit program (warn : Data will be deleted)\n"))
            #  start crawling -- blocked
            if menu == 1:
                self.Crawling.crawling()
            elif menu == 2:
                # 모델 객체 생성
                vocab = self.Crawling.get_vacab()
                if vocab is None:
                    print('crawling must have been done first')
                    continue
                self.model_obj = RNN.Rnn(self.Conn, vocab)
                print('model object created')
                self.model_obj.data_manipulate()
            # load model --blocked
            elif menu == 3:
                if (self.model_obj.loadModel() == False):
                    print("There's no saved model, please build model first\n")

            # build model -- blocked
            elif menu == 4:
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
            elif menu == 5:
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
            elif menu ==6:
                self.server = Server('0.0.0.0', 3002, self.model_obj)
                self.server.start_server()

            elif menu == 7:
                print("Exitting program")
                break

        return

if __name__ == '__main__':
    print("Initiate program")
    main = Main_Program()
    print("Progarm is running")
    main.run_program()
