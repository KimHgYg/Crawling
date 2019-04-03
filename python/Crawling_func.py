import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer

import model

'''
KONLPY GPL v3 이상
박은정, 조성준, “KoNLPy: 쉽고 간결한 한국어 정보처리 파이썬 패키지”, 제 26회 한글 및 한국어 정보처리 학술대회 논문집, 2014.

@inproceedings{park2014konlpy,
  title={KoNLPy: Korean natural language processing in Python},
  author={Park, Eunjeong L. and Cho, Sungzoon},
  booktitle={Proceedings of the 26th Annual Conference on Human & Cognitive Language Technology},
  address={Chuncheon, Korea},
  month={October},
  year={2014}
}
'''
import re

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
        self.model = model.model()
        self.vocab = None

    def crawling(self):
        print("Crawling Start...")

        crawling_list = [
            [self.joongang_crawling, 'joongang_crawling'],
            [self.chosun_crawling, 'chosun_crawling'],
            [self.donga_crawling, 'donga_crawglin']
        ]

        for list in crawling_list:
            print('start '+ list[1])
            list[0]()

        print("Crawling done...")
        #tfidf 값 계산 후 db에 넣는다
        self.cal_weight()

    def cal_weight(self):
        print('calculating weight...')

        #twitter로 명사 추출
        t = Okt()

        #foregrounds 모델에서 데이터 select한 cursor
        cols = ['id', 'class', 'press', 'link']
        cursor = pd.DataFrame(self.model.selectForeground(projection=cols, join=None), columns=cols)

        # text를 담을 변수
        docs = [[] for i in range(6)]

        #class별로 cursor 데이터 분류해서 기사 내용 가져온 뒤 docs에 넣는다
        for clas, i in [('politics', 0), ('economy', 1), ('sports', 2), ('enter', 3), ('national', 4), ('inter', 5)]:
            df_tmp = cursor.loc[cursor['class'] == clas]
            for article in df_tmp.values:
                html = get_html(article[3])
                soup = BeautifulSoup(html,'lxml', from_encoding='utf-8')
                try:
                    if article[2] == 'chosun' and clas == 'economy':
                        body = soup.find('div', id='news_body_id')
                        body = body.find_all('div', attrs={'class':'par'})
                        text = ''
                        for par in body:
                            text += par.get_text()
                        docs[1].append([text, article[0]])
                    elif article[2] == 'chosun' and clas != 'economy':
                        text = ""
                        body = soup.find('div', id='news_body_id')
                        body = body.findAll('div', attrs={'class':'par'})
                        for par in body:
                            text += (par.get_text() + " ")
                        docs[i].append([text, article[0]])
                    elif article[2] == 'donga':
                        docs[i].append([soup.find('div', attrs={'class' : 'article_txt'}).get_text(), article[0]])
                    elif article[2] == 'joongang' and clas != 'enter':
                        docs[i].append([soup.find('div', id='article_body').get_text(), article[0]])
                    elif article[2] == 'joongang' and clas == 'enter':
                        docs[3].append([soup.find('div', attrs={'class' : 'article_body'}, id='article_body').get_text(), article[0]])
                except Exception as e:
                    print(e, article[3])
                    pass

        #text 수집 안된 기사 foregrounds에서 제거 ... 보통 이미지만 있거나 칼럼 또는 없는 기사링크...
        self.model.arrangeForeground()

        #기사 별 tfidf를 담을 변수
        tfidf_list = []
        stopwords = ['.', ',', '\n', '\xa0', re.compile('^A-Za-z*$')] #영어 제외
        for i in range(self.num_class):
            pos = lambda d:['/'.join(p) for p in t.pos(d, stem=True, norm=True)]
            nouns = [' '.join(pos(article[0]) for article in docs[i])] #각 기사별 명사 담음
                                                                    #명사, 태거 tuple로 되있어서 article[0]으로 명사만
                                                                    #pos를 사용하여 normalization 및 stemming 가능
            vec = TfidfVectorizer(stop_words=stopwords) #tfidf vectorizer 모델 만든다
            tfidf_res = vec.fit_transform(nouns) #해당 class의 단어들에 대한 가중치 계산
                                                 #+ tf-idf-weighted document-term matrix 반환
            self.vocab = vec.get_feature_names() #feature에 해당하는 단어 배열
            j = 0
            for article in tfidf_res.toarray(): #한 문서씩 단어들의 가중치 배열을 읽으며 vocab과 매치시키고
                                                #정렬해서 큰 순서대로 3개만 가져온다
                idf = sorted(zip(self.vocab, article), key=lambda kv: kv[1])[-3:]
                idf_converted = [self.vocab.index(i) for i in idf]
                tfidf_list.append([docs[i][j][1], idf_converted[2], idf_converted[1], idf_converted[0]])
                j += 1

        self.model.insertBackground(tfidf_list)

        print('cal_weight done!')
        return

    def get_vocab(self):
        return self.vocab

    def chosun_crawling(self):
        data_foregrounds = []
        for clas in CHOSUN:
            if clas[1] == 'economy':
                pass
            html = get_html(clas[0])
            soup = BeautifulSoup(html, "lxml", from_encoding="utf-8")
            for lt in soup.find_all("dt"):
                try:
                    tmp = lt.find('a')
                    link = tmp.get('href')
                    day = link.split('/')
                    day = day[6] + day[7] + day[8]
                    title = tmp.get_text()
                    data_foregrounds.append([title, 'chosun', link, day, clas[1]])
                except :
                    #토론마당 그냥 넘긴다
                    pass

        #chosun biz
        html = get_html('http://biz.chosun.com')
        soup = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
        # 헤드라인
        sub = soup.find("div", attrs={'class': 'left_area'})
        head = sub.find("div", attrs={'class': 'main_visual'})
        tmp = head.find('a')
        link = tmp.get('href')
        day = link.split('/')
        day = day[6] + day[7] + day[8]
        title = tmp.get_text()

        data_foregrounds.append([title, 'chosun', link, day, 'economy'])

        # 메인 기사
        for lt in sub.find_all("dt"):
            try:
                tmp = lt.find('a')
                link = tmp.get('href')
                day = link.split('/')
                day = day[6] + day[7] + day[8]
                title = tmp.get_text()
                data_foregrounds.append([title, 'chosun', link, day, 'economy'])
            except:
                # 이코노미 조선 넘긴다
                pass

        # sub_news
        for lt in sub.find_all('li'):
            try:
                tmp = lt.find('a')
                link = tmp.get('href')
                day = link.split('/')
                day = day[6] + day[7] + day[8]
                title = tmp.get_text()
                data_foregrounds.append([title, 'chosun', link, day, 'economy'])

            except:
                # 키워드 검색 넘긴다
                pass
        try:
            self.model.insertForeground(data_foregrounds)
        except:
            print("조선일보 뉴스 정보를 가져올 수 없습니다.")
            return
        print('chosun_crawling done')
        return

    def donga_crawling(self):
        data_foregrounds = []

        for clas in DONGA:
            html = get_html(clas[0])
            soup = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
            head = soup.find('div', attrs={'class': 'articleTop'})

            for art in head.find_all('a'):
                link = art.get('href')
                day = link.split('/')[6]
                title = art.find(attrs={'class': 'title'}).get_text()
                data_foregrounds.append([title, 'donga', link, day, clas[1]])
            # issue
            try:
                content_issue = soup.find('div', attrs={'class': 'issueList'})
                for art in content_issue.find_all('a'):
                    try:
                        link = art.get('href')
                        day = link.split('/')[6]
                        title = art.get_text()
                        data_foregrounds.append([title, 'donga', link, day, clas[1]])
                    except:
                        pass

            except:  #스포츠는 이슈 따로 없음
                pass
            # 최신기사
            contents = soup.find('div', attrs={'class': 'articleList_con'})
            for art in contents.find_all('div', attrs={'class': 'rightList'}):
                tmp = art.find('a')
                link = tmp.get('href')
                day = link.split('/')[6]
                title = tmp.find(attrs={'class': 'tit'}).get_text()
                data_foregrounds.append([title, 'donga', link, day, clas[1]])

        try:
            self.model.insertForeground(data_foregrounds)
        except:
            print("동아일보 뉴스 정보를 가져올 수 없습니다.")
            return
        print('donga_crawling done')
        return

    def joongang_crawling(self):
        day = datetime.today().strftime("%Y%m%d")
        data_foregrounds = []

        for clas in JOONGANG:
            if clas[1] == 'enter':
                pass
            html = get_html(clas[0])
            soup = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
            for art in soup.find_all(attrs={'class':'headline mg'}):
                try:
                    tmp = art.find('a')
                    link = tmp.get('href')
                    if "http" not in link:
                        link = "https://news.joins.com" + link
                    title = tmp.get_text()
                    data_foregrounds.append([title, 'joongang', link, day, clas[1]])
                except :
                    #아래 이미지에 대한 텍스트 넘긴다
                    pass

        #joongang culture
        for clas in JOONGANG_CUL:
            html = get_html(clas[0])
            soup = BeautifulSoup(html, 'lxml', from_encoding='utf-8')

            origin = soup.find('div', id='content')
            for content in origin.find_all('li'):
                art = content.find(attrs={'class': 'headline mg'})
                tmp = art.find('a')
                link = 'http://news.joins.com' + tmp.get('href')
                title = tmp.get_text()
                data_foregrounds.append([title, 'joongang', link, day, clas[1]])

        try:
            self.model.insertForeground(data_foregrounds)
        except:
            print("중앙일보 뉴스 정보를 가져올 수 없습니다.")
            return
        print('joongang_crawling done')
        return
