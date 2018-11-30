import Crawling_func
import RNN
import Server

from multiprocessing import Process
import multiprocessing
import logging

from pymongo import MongoClient
import pymongo
#aasdf
class Main_Program:

    # 프로그램 객체 생성
    def __init__(self):
        #몽고디비와 연결 객체
        self.Conn = MongoClient('52.79.249.174',27017)
        #크롤링객체 생성
        self.Crawling = Crawling_func.crawling_func()
        #모델 객체 생성
        self.model_obj = RNN.rnn(self.Conn)


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
        while (1):
            menu = int(input("1 : crawling " +
                             "2 : load model" +
                             "3 : build model " +
                             "4 : start recommand program\n"))
            #  start crawling -- blocked
            if (menu == 1):
                self.Crawling.crawling()
                self.model_obj.data_manipulate()
            # load model --blocked
            elif (menu == 2):
                if (self.model_obj.loadModel() == False):
                    print("There's no saved model, please build model first\n")

            # build model -- blocked
            elif (menu == 3):
                if (self.model_obj.train_ready() is None):
                    print("Training set not exist")
                    continue

                p = int(input("1: build relu model\n" +
                              "2 : build sigmoid model\n" +
                              "3 : build bidirectional relu model\n" +
                              "4 : build bidirectional sigmoid model\n" +
                              "5 : build all model\n"))
                if (p == 1):
                    p = Process(target=self.model_obj.build_learn_model)
                    p.start()
                elif (p == 2):
                    p = Process(target=self.model_obj.build_learn_model_sig)
                    p.start()
                elif (p == 3):
                    p = Process(target=self.model_obj.build_learn_model_bi)
                    p.start()
                elif (p == 4):
                    p = Process(target=self.model_obj.build_learn_model_sig_bi)
                    p.start()
                elif (p == 5):
                    p = Process(target=self.model_obj.build_model_all)
                    p.start()

                p.join()

            # start recommand program
            elif (menu == 4):
                self.server = Server('0.0.0.0',3002,self.model_obj)
                self.server.start_server()

        return

if __name__ == '__main__':
    print("Initiate program")
    main = Main_Program()
    print("Progarm is running")
    main.run_program()
