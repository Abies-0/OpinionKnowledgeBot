# 以下函式部分參考自 Iceloof/GoogleNews（MIT License）
# https://github.com/Iceloof/GoogleNews

import re
import base64
import urllib.request
import dateparser, copy
from bs4 import BeautifulSoup as Soup, ResultSet
from dateutil.parser import parse
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

def decode_base64_with_clean_url(b64_str):
    clean_b64 = b64_str.rstrip("]'\"")
    missing_padding = len(clean_b64) % 4
    if missing_padding:
        clean_b64 += '=' * (4 - missing_padding)
    decoded = base64.b64decode(clean_b64).decode("utf-8")
    match = re.search(r'https?://[^\s\"\']+', decoded)
    if match:
        return match.group(0)
    return decoded

def define_date(date):
    months = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Sept':9,'Oct':10,'Nov':11,'Dec':12, '01':1, '02':2, '03':3, '04':4, '05':5, '06':6, '07':7, '08':8, '09':9, '10':10, '11':11, '12':12}
    try:
        if ' ago' in date.lower():
            q = int(date.split()[-3])
            if 'minutes' in date.lower() or 'mins' in date.lower():
                return datetime.now() + relativedelta(minutes=-q)
            elif 'hour' in date.lower():
                return datetime.now() + relativedelta(hours=-q)
            elif 'day' in date.lower():
                return datetime.now() + relativedelta(days=-q)
            elif 'week' in date.lower():
                return datetime.now() + relativedelta(days=-7*q)
            elif 'month' in date.lower():
                return datetime.now() + relativedelta(months=-q)
        elif 'yesterday' in date.lower():
            return datetime.now() + relativedelta(days=-1)
        else:
            date_list = date.replace('/',' ').split(' ')
            if len(date_list) == 2:
                date_list.append(datetime.now().year)
            elif len(date_list) == 3:
                if date_list[0] == '':
                    date_list[0] = '1'
            return datetime(day=int(date_list[0]), month=months[date_list[1]], year=int(date_list[2]))
    except:
        return float('nan')

def fix_missing_year(date_str: str, year: int = None) -> str:
    
    if year is None:
        year = datetime.now().year

    match = re.fullmatch(r"(\d{1,2})月(\d{1,2})日", date_str)
    if match:
        month = int(match.group(1))
        day = int(match.group(2))
        return f"{year}年{month}月{day}日"
    return date_str

class GoogleNews:

    def __init__(self, lang="en", period="", start="", end="", encode="utf-8", region=None):
        self.__texts = []
        self.__links = []
        self.__results = []
        self.__totalcount = 0
        self.user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0'
        self.__lang = lang
        if region:
            self.region = region
            self.accept_language= lang + '-' + region + ',' + lang + ';q=0.9'
            self.headers = {'User-Agent': self.user_agent, 'Accept-Language': self.accept_language}
        else:
            self.region = "US"
            self.headers = {'User-Agent': self.user_agent}
        self.__period = period
        self.__start = start
        self.__end = end
        self.__encode = encode
        self.__exception = False
        self.__version = '1.6.15'
        self.__topic = None
        self.__section = None

    def clear(self):
        self.__texts = []
        self.__links = []
        self.__results = []
        self.__totalcount = 0

    def get_news(self, key="",deamplify=False):
        self.clear()
        if key != '':
            if self.__period != "":
                key += f" when:{self.__period}"
        else:
            if self.__period != "":
                key += f"when:{self.__period}"
        key = urllib.request.quote(key.encode(self.__encode))
        start = f'{self.__start[-4:]}-{self.__start[:2]}-{self.__start[3:5]}'
        end = f'{self.__end[-4:]}-{self.__end[:2]}-{self.__end[3:5]}'
        
        if self.__start == '' or self.__end == '':
            self.url = 'https://news.google.com/search?q={}&hl={}&gl={}'.format(
                key, self.__lang.lower(), self.region)
        else:
            self.url = 'https://news.google.com/search?q={}+before:{}+after:{}&hl={}&gl={}'.format(
                key, end, start, self.__lang.lower(), self.region)
        
        if self.__topic:
            self.url = 'https://news.google.com/topics/{}'.format(
                self.__topic)
            
            if self.__section:
                self.url = 'https://news.google.com/topics/{}/sections/{}'.format(
                self.__topic, self.__section)
            
        try:
            self.req = urllib.request.Request(self.url, headers=self.headers)
            self.response = urllib.request.urlopen(self.req)
            self.page = self.response.read()
            self.content = Soup(self.page, "html.parser")
            articles = self.content.select('article')
            for article in articles:
                try:
                    # title
                    try:
                        title=article.findAll('div')[2].findAll('a')[0].text
                    except:
                        try:
                            title=article.findAll('a')[1].text
                        except:
                            title=None
                    # description
                    try:
                        desc=None
                    except:
                        desc=None
                    # date
                    try:
                        date = fix_missing_year(article.find("time").text)
                        # date,datetime_tmp = lexial_date_parser(date)
                    except:
                        date = None
                    # datetime
                    try:
                        datetime_chars=article.find('time').get('datetime')
                        datetime_obj = parse(datetime_chars).replace(tzinfo=None)
                    except:
                        datetime_obj=None
                    # link
                    if deamplify:
                        try:
                            link = 'https://news.google.com/' + article.find('div').find("a").get("href")[2:]
                        except Exception as deamp_e:
                            print(deamp_e)
                            link = article.find("article").get("jslog").split('2:')[1].split(';')[0]
                    else:
                        try:
                            link = 'https://news.google.com/' + article.find('div').find("a").get("href")[2:]
                        except Exception as deamp_e:
                            print(deamp_e)
                            link = None
                    # jslog
                    try:
                        a_tags = article.find_all("a", href=True, jslog=True)
                        for a in a_tags:
                            raw_jslog = a.get("jslog", "")
                            if "aHR0c" in raw_jslog:
                                matches = re.findall(r'(aHR0c[A-Za-z0-9+/=]+)', raw_jslog)
                                source = decode_base64_with_clean_url(matches[0])
                    except:
                        source = ""
                    self.__texts.append(title)
                    self.__links.append(link)
                    if link.startswith('https://www.youtube.com/watch?v='):
                        desc = 'video'
                    # image
                    try:
                        img = 'https://news.google.com'+article.find("figure").find("img").get("src")
                    except:
                        img = None
                    # site
                    try:
                        site=article.find("time").parent.find("a").text
                    except:
                        site=None
                    try:
                        media=article.find("div").findAll("div")[1].find("div").find("div").find("div").text
                    except:
                        try:
                            media=article.findAll("div")[1].find("div").find("div").find("div").text
                        except:
                            media=None
                    # reporter
                    try:
                        reporter = article.findAll('span')[2].text
                    except:
                        reporter = None
                    # collection
                    self.__results.append({'title':title,
                                           'desc':desc,
                                           'date':date,
                                           'datetime':define_date(date),
                                           'link':link,
                                           'source': source,
                                           'img':img,
                                           'media':media,
                                           'site':site,
                                           'reporter':reporter})
                except Exception as e_article:
                    print(e_article)
            self.response.close()
        except Exception as e_parser:
            print(e_parser)
            if self.__exception:
                raise Exception(e_parser)
            else:
                pass
    def results(self,sort=False):
        """Returns the __results.
        New feature: include datatime and sort the articles in decreasing order"""
        results=self.__results
        if sort:
            try:
                results.sort(key = lambda x:x['datetime'],reverse=True)
            except Exception as e_sort:
                print(e_sort)
                if self.__exception:
                    raise Exception(e_sort)
                else:
                    pass
                results=self.__results
        return results
