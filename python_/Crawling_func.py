import requests
from bs4 import BeautifulSoup
from datetime import datetime

from sklearn.feature_extraction.text import TfidfVectorizer
from konlpy.tag import Twitter
import re


from multiprocessing import Queue, Process, Lock, current_process

import pymongo
from pymongo import MongoClient

# 정치 경제 스포츠 연예 사회 국제
# politics economy sports enter national inter
#   0         1     2     3      4       5
# 조선일보 경제는 biz.chosun.com...
CHOSUN = [("http://news.chosun.com/politics", 'politics', 0), ("http://news.chosun.com/sports", 'sports', 2),
          ("http://news.chosun.com/ent", 'enter', 3), ("http://news.chosun.com/national", 'national', 4),
          ("http://news.chosun.com/international", 'inter', 5)]

# 동아일보는 패턴 통일
DONGA = [("http://news.donga.com/Politics", 'politics', 0), ("http://news.donga.com/Economy", 'economy', 1),
         ("http://news.donga.com/Sports", 'sports', 2), ("http://news.donga.com/Enter", 'enter', 3),
         ("http://news.donga.com/Society", 'national', 4), ("http://news.donga.com/Inter", 'inter', 5)]

# 중앙일보 연예가 가요, 방송, 영화로 나눠져있음
JOONGANG = [("http://news.joins.com/politics", 'politics', 0), ("http://news.joins.com/money", 'economy', 1),
            ("http://news.joins.com/sports", 'sports', 2), ("http://news.joins.com/society", 'national', 4),
            ("http://news.joins.com/world", 'inter', 5)]
JOONGANG_CUL = [("http://news.joins.com/culture/song/list", 'enter', 3),
                ("http://news.joins.com/culture/broadcast/list", 'enter', 3),
                ("http://news.joins.com/culture/movie/list", 'enter', 3)]


def get_html(url):
    _html = ""
    resp = requests.get(url)
    resp.encoding = 'utf-8'
    if resp.status_code == 200:
        _html = resp.text
    return _html

class crawling_func:
    def __init__(self):
        # 기사의 class 개수
        self.num_class = 6
        pass

    def crawling(self):
        print("Crawling Start...")
        Conn = MongoClient('52.79.249.174', 27017)
        ps = []
        crawling_list = [
            [joongang_crawling, 'joongang_crawling'],
            [joongang_cul, 'joongang_cul'],
            [chosun_crawling, 'chosun_crawling'],
            [chosun_biz, 'chosun_biz'],
            [donga_crawling, 'donga_crawglin']
        ]
        lock = Lock()
        lock_f = Lock()
        docs = [[] for i in range(self.num_class)]
        foreground = Conn.crawling.foreground
        background = Conn.crawling.background
        try:
            _id = Conn.crawling.foreground.find().sort([('_id', pymongo.DESCENDING)])[0]['_id'] + 1
        except:
            _id = 0
        #큐로 _id 동기화
        q = Queue()
        q.put(_id)
        #프로세스 생성해서 concurrent하게 크롤링
        for func in crawling_list:
            p = Process(target = func[0], name=func[1], args=(q, lock, docs, lock_f, foreground))
            ps.append(p)
            p.start()
        for p in ps:
            p.join()
        #프로세스 끝나면 큐 닫는다
        q.close()
        print("Crawling done...")
        #tfidf 값 계산 후 db에 넣는다
        self.cal_weight(docs, background)

    def cal_weight(self, docs, background):
        print('calculating weight...')

        stopwords = ['.', ',', '\n', '\xa0', re.compile('^A-Za-z*$')]
        tfidf_list = []
        t = Twitter()

        fitted = None

        for i in range(self.num_class):
            # for i in range(1):
            nouns = []
            for article in docs[i]:
                if article[0] is not '':
                    nouns.append(' '.join([noun for noun in t.nouns(str(article[0]))]))
            vec = TfidfVectorizer(stop_words=stopwords)
            fitted = vec.fit(nouns)
            tfidf_res = fitted.transform(nouns)
            vocab = fitted.get_feature_names()
            j = 0
            for article in tfidf_res.toarray():
                idf = sorted(zip(vocab, article), key=lambda kv: kv[1])[-3:]
                tmp = idf[0][0] + ' ' + idf[1][0] + ' ' + idf[2][0]
                tfidf_list.append({'_id': docs[i][j][2], 'tfidf': tmp, 'link': docs[i][j][1]})
                j = j + 1
        background.insert_many(tfidf_list)

        print('cal_weight done!')
        return

def chosun_crawling(q, arg):
    lock = arg[0]
    docs = arg[1]
    lock_f = arg[2]
    foreground = arg[3]
    data_foreground = []
    i = 0
    for clas in CHOSUN:
        html = get_html(clas[0])
        print(clas[0])
        soup = BeautifulSoup(html, "lxml", from_encoding="utf-8")
        for lt in soup.find_all("dt"):
            try:
                tmp = lt.find('a')
                link = tmp.get('href')
                day = link.split('/')
                day = day[6] + day[7] + day[8]
                text = tmp.get_text()
                _id = q.get()
                q.put(_id + 1)
                data_foreground.append(
                    {'_id': str(_id).zfill(10), 'title': text, 'press': 'chosun', 'link': link, 'day': day,
                     'class': clas[1]})
                html = get_html(link)
                soup2 = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
                lock.acquire()
                docs[i].append((soup2.find('div', attrs={'class': 'par'}).get_text(), link), _id)
                lock.release()
            except:
                print('error!!!', link)
        # self.docs[i].append(tmp_list)
        i = i + 1
        if i == 1:
            i = i + 1
    lock_f.acquire()
    foreground.insert_many(data_foreground)
    lock_f.release()
    print('{0} done!', format(current_process().name))
    return

def chosun_biz(q, lock, docs, lock_f, foreground):
    html = get_html('http://biz.chosun.com')
    print('http://biz.chosun.com')
    soup = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
    data_foreground = []
    head = soup.find("div", attrs={'class': 'mt_art_tit'})
    tmp = head.find('a')
    link = tmp.get('href')
    day = link.split('/')
    day = day[6] + day[7] + day[8]
    text = tmp.get_text()
    _id = q.get()
    q.put(_id + 1)
    j = 0
    data_foreground.append(
        {'_id': str(_id).zfill(10), 'title': text, 'press': 'chosun', 'link': link, 'day': day, 'class': 'economy'})

    html = get_html(link)
    soup2 = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
    lock.acquire()
    docs[1].append((soup2.find('div', id='article_2011', attrs={'class': 'article'}).get_text(), link), _id)
    lock.release
    art = soup.find("div", attrs={'class': 'mc_art_lst'})
    for lt in art.find_all("li", limit=30):
        try:
            tmp = lt.find('a')
            # print(tmp)
            link = tmp.get('href')
            day = link.split('/')
            day = day[6] + day[7] + day[8]
            text = tmp.get_text()
            _id = q.get()
            q.put(_id + 1)
            data_foreground.append(
                {'_id': str(_id).zfill(10), 'title': text, 'press': 'chosun', 'link': link, 'day': day,
                 'class': 'economy'})

            html = get_html(link)
            soup2 = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
            lock.acquire()
            docs[1].append((soup2.find('div', id='article_2011', attrs={'class': 'article'}).get_text(), link), _id)
            lock.release()
        except:
            print('error!!!', link)
    lock_f.acquire()
    foreground.insert_many(data_foreground)
    lock_f.release()
    print('{0} done!', format(current_process().name))
    return

def donga_crawling(q, lock, docs, lock_f, foreground):
    data_foreground = []
    # self.docs = []
    i = 0

    for clas in DONGA:
        html = get_html(clas[0])
        print(clas[0])
        soup = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
        try:
            tmp = soup.find('div', attrs={'class': 'articleTop'})
            head = tmp.find("div", attrs={'class': 'articleMain'})
            # 해드라인_main
            head_main = head.find('a')
            link = head_main.get('href')
            day = link.split('/')[6]
            text = head.find(attrs={'class': 'title'}).get_text()
            _id = q.get()
            q.put(_id + 1)
            data_foreground.append(
                {'_id': str(_id).zfill(10), 'title': text, 'press': 'donga', 'link': link, 'day': day,
                 'class': clas[1]})

            # print(data_foreground)
            html = get_html(link)
            soup2 = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
            lock.acquire()
            docs[i].append((soup2.find('div', attrs={'class': 'article_txt'}).get_text(), link), _id)
            lock.release()
            for head_sub in tmp.find_all('li'):
                art = head_sub.find('a')
                link = art.get('href')
                day = link.split('/')[6]
                text = art.find(attrs={'class': 'title'}).get_text()
                _id = q.get()
                q.put(_id + 1)
                data_foreground.append(
                    {'_id': str(_id).zfill(10), 'title': text, 'press': 'donga', 'link': link, 'day': day,
                     'class': clas[1]})

                html = get_html(link)
                soup2 = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
                lock.acquire()
                docs[i].append((soup2.find('div', attrs={'class': 'article_txt'}).get_text(), link), _id)
                lock.release()
        except:
            for head in tmp.find_all('div', attrs={'class': 'artivleMain'}):
                art = head.find('a')
                link = art.get('href')
                day = link.split('/')[6]
                text = art.find(attrs={'class': 'title'}).get_text()
                _id = q.get()
                q.put(_id + 1)
                data_foreground.append(
                    {'_id': str(_id).zfill(10), 'title': text, 'press': 'donga', 'link': link, 'day': day,
                     'class': clas[1]})

                html = get_html(link)
                soup2 = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
                lock.acquire()
                docs[i].append((soup2.find('div', attrs={'class': 'article_txt'}).get_text(), link), _id)
                lock.release()

            for head in tmp.find_all('div', attrs={'class': 'artivleMain02'}):
                art = head.find('a')
                link = art.get('href')
                day = link.split('/')[6]
                text = art.find(attrs={'class': 'title'}).get_text()
                _id = q.get()
                q.put(_id + 1)
                data_foreground.append(
                    {'_id': str(_id).zfill(10), 'title': text, 'press': 'donga', 'link': link, 'day': day,
                     'class': clas[1]})

                html = get_html(link)
                soup2 = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
                lock.acquire()
                docs[i].append((soup2.find('div', attrs={'class': 'article_txt'}).get_text(), link), _id)
                lock.release()
        try:
            # issue
            content_issue = soup.find('div', attrs={'class': 'issueList'})
            issue = content_issue.find('a', attrs={'class': 'tit'})
            link = issue.get('href')
            day = link.split('/')[6]
            text = issue.get_text()
            _id = q.get()
            q.put(_id + 1)
            data_foreground.append(
                {'_id': str(_id).zfill(10), 'title': text, 'press': 'donga', 'link': link, 'day': day,
                 'class': clas[1]})

            html = get_html(link)
            soup2 = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
            lock.acquire()
            docs[i].append((soup2.find('div', attrs={'class': 'atrticle_txt'}).get_text(), link), _id)
            lock.release()

            for issue_sub in content_issue.find_all('li'):
                art = issue_sub.find('a')
                link = art.get('href')
                day = link.split('/')[6]
                text = art.get_text()
                _id = q.get()
                q.put(_id + 1)
                data_foreground.append(
                    {'_id': str(_id).zfill(10), 'title': text, 'press': 'donga', 'link': link, 'day': day,
                     'class': clas[1]})

                html = get_html(link)
                soup2 = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
                lock.acquire()
                docs[i].append((soup2.find('div', attrs={'class': 'article_txt'}).get_text(), link), _id)
                lock.release()

        except:
            print('error!!!', link)

        try:
            # 최신기사
            contents = soup.find('div', attrs={'class': 'articleList_con'})
            for art in contents.find_all('div', attrs={'class': 'rightList'}):
                tmp = art.find('a')
                link = tmp.get('href')
                day = link.split('/')[6]
                text = tmp.find(attrs={'class': 'tit'}).get_text()
                _id = q.get()
                q.put(_id + 1)
                data_foreground.append(
                    {'_id': str(_id).zfill(10), 'title': text, 'press': 'donga', 'link': link, 'day': day,
                     'class': clas[1]})

                html = get_html(link)
                soup2 = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
                lock.acquire()
                docs[i].append((soup2.find('div', attrs={'class': 'article_txt'}).get_text(), link), _id)
                lock.release()
        except:
            print('error!!!', link)
        i = i + 1
    lock_f.acquire()
    foreground.insert_many(data_foreground)
    lock_f.release()
    print('{0} done!', format(current_process().name))
    return

def joongang_crawling(q, lock, docs, lock_f, foreground):
    day = datetime.today().strftime("%Y%m%d")
    data_foreground = []
    i = 0

    for clas in JOONGANG:
        html = get_html(clas[0])
        print(clas[0])
        soup = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
        origin = soup.find('div', id='content')
        # 해드라인
        try:
            art = origin.find('dt')
            tmp = art.find('a')
            link = tmp.get('href')
            text = tmp.get_text()
            _id = q.get()
            q.put(_id + 1)
            data_foreground.append(
                {'_id': str(_id).zfill(10), 'title': text, 'press': 'joongang', 'link': link, 'day': day,
                 'class': clas[1]})

            html2 = get_html(link)
            soup2 = BeautifulSoup(html2, 'lxml', from_encoding='utf-8')
            lock.acquire()
            docs[i].append(soup2.find('div', attrs={'class': 'article_body'}, id='article_body').get_text(), link,
                           _id)
            lock.release()

        except:
            # sport 해드라인
            try:
                for art in origin.find_all('div', attrs={'class': 'slide'}):
                    tmp = art.find(attrs={'class': 'headline mg'})
                    tmp2 = tmp.find('a')
                    link = tmp2.get('href')
                    text = tmp2.get_text();
                    _id = q.get()
                    q.put(_id + 1)
                    data_foreground.append(
                        {'_id': str(_id).zfill(10), 'title': text, 'press': 'joongang', 'link': link, 'day': day,
                         'class': clas[1]})

                    html2 = get_html(link)
                    soup2 = BeautifulSoup(html2, 'lxml', from_encoding='utf-8')
                    lock.acquire()
                    docs[i].append(soup2.find('div', attrs={'class': 'article_body'}, id='article_body').get_text(),
                                   link, _id)
                    lock.release()

            except:
                print('error!!!', link)

        # 실시간 주요뉴스
        try:
            art = origin.find('div', attrs={'class': 'default_realtime'})
            art = art.find('ul', id='ulItems')
            # print(art)
            for content in art.find_all('li'):
                # print(content)
                tmp = content.find(attrs={'class': 'headline mg'})
                tmp2 = tmp.find('a')
                link = 'http://news.joins.com/' + tmp2.get('href')
                text = tmp2.get_text()
                _id = q.get()
                q.put(_id + 1)
                data_foreground.append(
                    {'_id': str(_id).zfill(10), 'title': text, 'press': 'joongang', 'link': link, 'day': day,
                     'class': clas[1]})

                html2 = get_html(link)
                soup2 = BeautifulSoup(html2, 'lxml', from_encoding='utf-8')
                lock.acquire()
                docs[i].append(soup2.find('div', attrs={'class': 'article_body'}, id='article_body').get_text(),
                               link, _id)
                lock.release()

        except:
            try:
                art = origin.find('div', attrs={'class': 'combination_today'})
                art = art.find('div', attrs={'class': 'bd'})
                for content in art.find_all('li'):
                    tmp = content.find(attrs={'class': 'headline mg'})
                    tmp2 = tmp.find('a')
                    link = 'http://news.joins.com/' + tmp2.get('href')
                    text = tmp2.get_text()
                    _id = q.get()
                    q.put(_id + 1)
                    data_foreground.append(
                        {'_id': str(_id).zfill(10), 'title': text, 'press': 'joongang', 'link': link, 'day': day,
                         'class': clas[1]})

                    html2 = get_html(link)
                    soup2 = BeautifulSoup(html2, 'lxml', from_encoding='utf-8')
                    lock.acquire()
                    docs[i].append(soup2.find('div', attrs={'class': 'article_body'}, id='article_body').get_text(),
                                   link, _id)
                    lock.release()

            except:
                print('error!!!', link)
        i = i + 1
        if i == 3:
            i = i + 1

    lock_f.acquire()
    foreground.insert_many(data_foreground)
    lock_f.release()
    print('{0} done!', format(current_process().name))
    return

def joongang_cul(q, lock, docs, lock_f, foreground):
    day = datetime.today().strftime("%Y%m%d")
    dosc = []

    # tmp_list = []
    data_foreground = []
    for clas in JOONGANG_CUL:
        html = get_html(clas[0])
        print(clas[0])
        soup = BeautifulSoup(html, 'lxml', from_encoding='utf-8')

        origin = soup.find('div', id='content')
        for content in origin.find_all('li'):
            art = content.find(attrs={'class': 'headline mg'})
            tmp = art.find('a')
            link = 'http://news.joins.com' + tmp.get('href')
            text = tmp.get_text()
            _id = q.get()
            q.put(_id + 1)
            data_foreground.append(
                {'_id': str(_id).zfill(10), 'title': text, 'press': 'joongang', 'link': link, 'day': day,
                 'class': clas[1]})
            html2 = get_html(link)
            soup2 = BeautifulSoup(html2, 'lxml', from_encoding='utf-8')
            lock.acquire()
            docs[3].append(soup2.find('div', attrs={'class': 'article_body'}, id='article_body').get_text(), link,
                           _id)
            lock.release()
    lock_f.acquire()
    foreground.insert_many(data_foreground)
    lock_f.release()
    print('{0} done!', format(current_process().name))
    return