__author__ = "Frank Shen"

import requests
import time
import random
from bs4 import BeautifulSoup as BS
from multiprocessing import Pool


def getHtmlText(url):
    try:
        time.sleep(random.random())
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        r = requests.get(url, headers=headers)
        r.encoding = r.apparent_encoding
        r.raise_for_status()
        if r.status_code == 200:
            return r.text
    except:
        print('html异常')


def getBookList():
    book_list = []
    url = 'https://www.gulongwang.com/'
    html = getHtmlText(url)
    soup = BS(html, 'lxml')
    ul = soup.find('ul', attrs={'class': 'shuming'})
    lis = ul.find_all('li')
    for li in lis:
        book_url = 'https://www.gulongwang.com' + li.find('a').get('href')
        book_name = li.find('img').get('alt')
        book_list.append([book_name, book_url])
    return book_list


def getChapterList(book):
    html = getHtmlText(book[1])
    soup = BS(html, 'lxml')
    div = soup.find('div', attrs={'class': 'lb'})
    ul = div.find('ul')
    lis = ul.find_all('li')
    for li in lis:
        chapter_url = 'https://www.gulongwang.com' + li.find('a').get('href')
        chapter_name = li.find('a').get_text()
        yield [
            chapter_name, chapter_url
        ]


def getContent(chapter):
    html = getHtmlText(chapter[1])
    soup = BS(html, 'lxml')
    div = soup.find('div', attrs={'class': 'nr_con'})
    contents = div.find_all('p')
    for content in contents:
        content = content.get_text()
        yield content


def main(book):
    print('%s 开始下载' % book[0])
    for chapter in getChapterList(book):
        with open('d:\\data\\古龙\\%s.txt' % book[0], 'a', encoding='utf8') as f:
            f.write(chapter[0] + '\n')
            for content in getContent(chapter):
                f.write(content + '\n')
    print('%s 下载完毕' % book[0])


if __name__ == '__main__':
    temp = time.time()
    book_list = getBookList()
    pool = Pool(4)
    for book in book_list:
        pool.apply_async(main, args=(book,))
    pool.close()
    pool.join()
    print(time.time() - temp)