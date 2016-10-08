#!/usr/bin/env python
# -*- coding:utf-8 -*-

import urllib
import time
import traceback
import datetime
from tornado import httpclient, gen, ioloop, queues
import urllib.request
import random
import math
import re
import os
import platform
from AdvancedHTMLParser import AdvancedHTMLParser
import json
from collections import OrderedDict

class AsyncSpider(object):
    """A simple class of asynchronous spider."""
    def __init__(self, url, headers, file, concurrency=10, **kwargs):
        """inherit this method"""
        self.url = url
        self.headers = headers
        self.file = file
        self.concurrency = concurrency

    def show_record(self, content):
        print(content)
        print(content, file=self.file)
        
    @gen.coroutine
    def fetch(self):
        """inherit and rewrite this method"""
        print('handling ...')

    @gen.coroutine
    def get_page(self):
        try:
            response = yield self.fetch()
        except Exception as e:
            print('Exception: %s\nURL: %s' % (e, self.url))
            raise gen.Return(e)
        raise gen.Return(response)

    @gen.coroutine
    def _run(self):
        response = yield self.get_page()
        self.handle_response(response)

    def handle_response(self, response):
        if response.code == 200:
            self.handle_content(response.body)
        elif response.code == 599:
            self._run()

    def handle_content(self, content):
        """inherit and rewrite this method"""
        print('handling content...')

    def run(self):
        ioloop.IOLoop.current().run_sync(self._run)



class GetSpider(AsyncSpider):
    def __init__(self, url, headers, file, concurrency=10, **kwargs):
        self.method = 'GET'
        super(GetSpider, self).__init__(url, headers, file)

    @gen.coroutine
    def fetch(self):  
        self.show_record('\n------------------------------------------------------ Get Shanghai Data ------------------------------------------------------')
        response = yield httpclient.AsyncHTTPClient().fetch(self.url, headers=self.headers, method=self.method, connect_timeout=200, request_timeout=600)#, raise_error=False)
        raise gen.Return(response)
    
    def handle_content(self, html):
        htmlstr = html.decode('utf-8').strip()
        htmlstr = htmlstr[htmlstr.rindex('"result":') + len('"result":') : htmlstr.rindex('],') + 1]
        data = json.loads(htmlstr)   

        isHead = False
        for dic in data:
            t = OrderedDict(sorted(dic.items(),key = lambda t:t[0]))
            if not isHead:
                self.show_record(list(t.keys()))
            isHead = True
            self.show_record(list(t.values()))
        self.show_record('\n--------------------------------------------------------- %d results in all -------------------------------------------------------' % len(data))

        #pattern = r'\"\bbulletinType\b\"\:\"(\w+)\"\,\"\bproductCode\b\"\:\"(\w+)\"\,\"\bproductName\b\"\:\"([\*]{0,2}\w+)\"\,\"\bseq\b\"\:(\d+)\,\"\bshowDate\b\"\:\"(\d{4}-\d{2}-\d{2})\"\,\"\bstopDate\b\"\:\"(\d{4}-\d{2}-\d{2}|[-])\"\,\"\bstopReason\b\"\:\"([-\w]+)\"\,\"\bstopTime\b\"\:\"(\w*(\d{4}-\d{2}-\d{2}\w*){1,2}|\w+)\"'
        #htmlstr = html.decode('utf-8').strip()
        #htmlstr = htmlstr[htmlstr.rindex('result')::]
        #m = re.findall(pattern, htmlstr)
        #self.show_record('\nbulletinType, productCode, productName, seq, showDate, stopDate, stopReason, stopTime')
        #for item in m:
        #    self.show_record(item)



class PostSpider(AsyncSpider):
    def __init__(self, url, headers, body, file, concurrency=10, **kwargs):
        self.body = body
        self.method = 'POST'
        super(PostSpider, self).__init__(url, headers, file)

    @gen.coroutine
    def fetch(self):  
        self.show_record('\n------------------------------------------------------ Post Shenzhen Data Form -----------------------------------------------------')
        response = yield httpclient.AsyncHTTPClient().fetch(self.url, headers=self.headers, method=self.method, body=self.body, connect_timeout=200, request_timeout=600)#, raise_error=False)
        raise gen.Return(response)
    
    def handle_content(self, content):
        parser = AdvancedHTMLParser()
        parser.feed(content.decode('gbk'))
        self.show_record('')

        hdrNode = parser.getElementsByClassName('cls-data-th')
        strHdr = '';
        for childnode in hdrNode:
            strHdr += childnode.innerHTML.ljust(16) + '\t'
        self.show_record(strHdr)
        conStr = ''
        count = 0
        lineCount = 0;
        node = parser.getElementsByClassName ('cls-data-td')
        for childnode in node:
            conStr += childnode.innerHTML.ljust(16) + '\t'
            count +=1
            if (count == len(hdrNode)):
                self.show_record(conStr)
                count = 0
                lineCount += 1
                conStr = '';
        self.show_record('\n--------------------------------------------------------- %d results in all ---------------------------------------------------------' % lineCount)
    
    

def GetNormalWorkDay():
    now = datetime.datetime.now()
    if now.weekday() == 5:
        return (now - datetime.timedelta(1)).strftime("%Y-%m-%d")
    elif now.weekday() == 6:
        return (now - datetime.timedelta(2)).strftime("%Y-%m-%d")
    else: 
        return now.strftime("%Y-%m-%d")


def GetMillionSecs():
    now = datetime.datetime.now()
    timeArray = time.strptime(now.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    return int(time.mktime(timeArray))


def main():
    fileName = 'suspension.txt';
    if not os.path.isfile(fileName):
        print('Create file %s' % fileName)
        
    with open(fileName,'w') as file:
        date = GetNormalWorkDay()
        print('--------------------------------------------------------- %s ----------------------------------------------------------'% date, file=file)

        url = '%sjsonCallBack=jsonpCallback%d&isPagination=%s&searchDate=%s&bgFlag=%s&searchDo=%d\
&pageHelp.pageSize=%d&pageHelp.pageNo=%d&pageHelp.beginPage=%d&pageHelp.cacheSize=%d&pageHelp.endPage=%d&_=%d' %\
              ('http://query.sse.com.cn/infodisplay/querySpecialTipsInfoByPage.do?', int(math.floor(random.random() * (100000 + 1))), 'true', date, 1, 1, 150, 1, 1, 1, 5, GetMillionSecs())
        headers = {
                'Accept' : "*/*",
                'Host' : 'query.sse.com.cn',
                'Method' : 'GET',
                'Referer' : 'http://www.sse.com.cn/disclosure/dealinstruc/suspension/',
                'UserAgent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
        }
        sh = GetSpider(url, headers, file)
        sh.run()
        
        url = 'http://www.szse.cn/szseWeb/FrontController.szse?randnum=%.16f' % random.random()
        postData = urllib.parse.urlencode({'ACTIONID': 7,
                                           'AJAX': 'AJAX-TRUE',
                                           'CATALOGID': 1798,
                                           'TABKEY' : 'tab1',
                                           'REPORT_ACTION' : 'search',
                                           'txtZzrq' : date,
                                           'txtKsrq' : date
                                       }).encode('utf-8')
        headers = {
            'Accept' : "*/*",
            'ContentType' : 'application/x-www-form-urlencoded; charset=UTF-8',
            'ContentLength' : str(len(postData)),
            'Host' : 'www.szse.cn',
            'Method' : 'POST',
            'Referer' : 'http://www.szse.cn/main/disclosure/news/tfpts/',
            'UserAgent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
        }
        sz = PostSpider(url, headers, postData, file)
        sz.run()

        file.close()

    sys = platform.system()
    if (sys == 'Windows'):
        os.system('pause')
    elif (sys == 'Linux'):
        os.system('echo "Press any key to continue..." && read') 


if __name__ == '__main__':
    main()
