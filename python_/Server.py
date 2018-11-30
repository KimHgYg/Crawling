import socket
import multiprocessing
from multiprocessing import current_process

class server:
    #클래스 객체 초기화
    def __init__(self, hostname, port, model_obj):
        import logging
        self.model_obj = model_obj
        self.logger = logging.getLogger("server")
        self.hostname = hostname
        self.port = port

    #연결 후 handler
    def handle(self, conn, address, logger):
        try:
            #ID 정보를 받아 예측 후 추천 tf-idf값 전송
            logger.debug("Connected %r at %r process-%r", conn, address,current_process().name)
            ID = conn.recv(1024)
            #받은 값이 없다면 리턴
            if ID == "":
                logger.debug("Socket closed remotely")
                return
            #ID 값을 받았다면 model_obj로 부터 predict
            logger.debug("Received ID %r", ID)
            Content = self.model_obj.predict_model(ID)
            conn.sendall(Content)
        except:
            logger.exception("Problem handling request")
        finally:
            logger.debug("Closing socket")
            conn.close()

        return


    #listening socket on
    def _start(self):
        self.logger.debug("listening")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(1)

        #연결 받으면 연결 객체 넘기고 새로운 연결 기다린다
        while True:
            conn, address = self.socket.accept()
            self.logger.debug("Got connection")
            process = multiprocessing.Process(target=self.handle, args=(conn,address))
            process.daemon = True
            process.start()
            self.logger.debug("Started process %r", process)

    #listening socket 생성 프로세스 시작
    def start_server(self):
        process = multiprocessing.Process(target=self._start)
        process.start()
        self.logger.debug("Started listening socket process")
