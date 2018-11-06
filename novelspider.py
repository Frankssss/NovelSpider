import random
import requests
import time
from multiprocessing import Process, Queue
from bs4 import BeautifulSoup as bs


class NovelDownload(Process):
    def __init__(self, name, url_queue):
        super(NovelDownload, self).__init__()
        self.name = name
        self.url_queue = url_queue

    def run(self):
        print('%s 开始' % self.name)
        time.sleep(1)
        while 1:        
            if self.url_queue.empty():
                break
            book = self.url_queue.get()
            print('%s 开始下载' % book[0])
            for chapter in self.getChapterList(book):
                with open('d:\\data\\金庸\\%s.txt' % book[0], 'a', encoding='utf8') as f:
                    f.write(chapter[0] + '\n')
                    for content in self.getContent(chapter):
                        f.write(content + '\n')
            print('%s 下载完毕' % book[0])
        print('%s 结束' % self.name)

    @staticmethod
    def getBookList(url_queue):
        book_list = []
        url = 'http://www.jinyongwang.com/book/'
        html = NovelDownload.getHtmlText(url)
        soup = bs(html, 'lxml')
        booklist = soup.find('div', attrs={"class": 'booklist'})
        ul = booklist.find('ul', attrs={'class': 'list'})
        lis = ul.find_all('li')
        for li in lis:
            book_url = url.rsplit('/', 2)[0] + li.find('a').get('href')
            book_name = li.find('img').get('alt')
            book_list.append([book_name, book_url])
            url_queue.put([book_name, book_url])
        return book_list

    def getChapterList(self, book):
        html = NovelDownload.getHtmlText(book[1])
        soup = bs(html, 'lxml')
        ul = soup.find('ul', attrs={'class', 'mlist'})
        lis = ul.find_all('li')
        for li in lis:
            chapter_url = 'http://www.jinyongwang.com' + li.find('a').get('href')
            chapter_name = li.find('a').get_text()
            yield [
                chapter_name, chapter_url
            ]

    def getContent(self, chapter):
        html = NovelDownload.getHtmlText(chapter[1])
        soup = bs(html, 'lxml')
        div = soup.find('div', attrs={'class': 'vcon'})
        ps = div.find_all('p')
        for p in ps:
            content = p.get_text()
            yield content

    @staticmethod
    def getHtmlText(url):
        time.sleep(random.random())
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
        try:
            r = requests.get(url, headers=headers)
            r.encoding = r.apparent_encoding
            r.raise_for_status()
            if r.status_code == 200:
                return r.text
        except:
            return None


def create_pool(url_queue):
    pool_list = [] 
    pool_name = ['进程1', '进程2', '进程3', '进程4']
    for name in pool_name:
        p = NovelDownload(name, url_queue)
        pool_list.append(p)
    return pool_list


def create_queue():
    url_queue = Queue()
    return url_queue


def main():
    url_queue = create_queue()
    NovelDownload.getBookList(url_queue)
    pool_list = create_pool(url_queue)
    for p in pool_list:
        p.start()
    for p in pool_list:
        p.join()


if __name__ == '__main__':
    temp = time.time()
    main()
    print(time.time() - temp)