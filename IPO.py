import requests
import re
import math
import random
import datetime
import json
import os
import string

class IpoDetail(object):
    """A simple class of IPO detail information."""
    def __init__(self, item):
        self.name = item[3]
        self.code = item[4]
        self.applyCode = item[5]
        self.totalIssueVolumn = 0 if item[6] == '' else float(item[6])
        self.onlineIssueVolumn = 0 if item[7] == '' else float(item[7])
        self.issuePrice = 0 if item[10] == '' else float(item[10]) 
        self.applyDate = item[11]
        self.issueDate = item[12]
        self.issuePE = 0 if item[14] == '' else float(item[14]) 
        self.hitRate = 0 if item[15] == '' else float(item[15]) 
        #print (self.applyDate + " " + self.issueDate)        
        

TIME_OUT = 30
ipoDetailDict = {}
dailyIpoCodeDict = {}
dailyLotteryCodeDict = {}

def getTradeDay():
    now = datetime.datetime.now()
    if now.weekday() == 5:
        return (now - datetime.timedelta(1)).strftime("%Y-%m-%d")
    elif now.weekday() == 6:
        return (now - datetime.timedelta(2)).strftime("%Y-%m-%d")
    else: 
        return now.strftime("%Y-%m-%d")


def loadIpoInfo():
    '''example urls
    'http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?type=NS&sty=NSSTV5&st=12&sr=-1&p=2&ps=50&js=var%20OZrNiRKx={pages:(pc),data:[(x)]}&stat=1&rt=4917635'
    'http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?type=NS&sty=NSSTV5&st=12&sr=-1&p=3&ps=50&js=var%20qhObDDyl={pages:(pc),data:[(x)]}&stat=1&rt=4917637'
    '''
    urlStr = 'http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?type=NS&sty=NSSTV5&st={}&sr={}&p={}&ps={}&js={}&stat={}&rt={}'\
             .format(12, -1, 1, 50, 'var%20'+ ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(8)) +'={pages:(pc),data:[(x)]}'\
                     , 1, int(math.floor(random.random() * (100000000 + 1))))
    #print(urlStr)
    response = requests.get(urlStr, timeout=TIME_OUT)
    if response.status_code == 200:
        r = response.text[response.text.find('["') :response.text.rindex('"]') + 2]
        jsonLst = eval(r)
        #tempDict = dict()
        for item in jsonLst:
            detailItem = IpoDetail(item.split(','))
            ipoDetailDict[detailItem.code] = detailItem
            if detailItem.applyDate in dailyIpoCodeDict.keys():
                dailyIpoCodeDict[detailItem.applyDate].append(detailItem.code)
            else:
                dailyIpoCodeDict[detailItem.applyDate] = [detailItem.code]

            if detailItem.issueDate in dailyLotteryCodeDict.keys():
                dailyLotteryCodeDict[detailItem.issueDate].append(detailItem.code)
            else:
                dailyLotteryCodeDict[detailItem.issueDate] = [detailItem.code]

        #dailyIpoCodeDict = sorted(tempDict.items(), reverse = True) 
        print('IPO detail items: {}'.format(len(ipoDetailDict)))
    else:
        print('Response Status Code: {}'.format(response.status_code))
        response.raise_for_status()
    

def getSecuritiesCode(date):
    print('date: {}'.format(date))
    if date in dailyIpoCodeDict.keys():
        for code in dailyIpoCodeDict[date]:
            print('申购 {} 代码: {}, 申购代码: {} '.format(ipoDetailDict[code].name, code, ipoDetailDict[code].applyCode))
    else:
        print('今日没有新股发布')

    lotteryLst = list()
    if date in dailyLotteryCodeDict.keys():
        for code in dailyLotteryCodeDict[date]:
            print('中签 {} 代码: {}, 申购代码: {} '.format(ipoDetailDict[code].name, code, ipoDetailDict[code].applyCode))
            lotteryLst.append(code)
    else:
        print('今日没有新股中签公布')
        return

    sum = 0
    for code in lotteryLst:
        print('代码：{}'.format(code))
        lotteryCode = input('请输入起始配号：')
        count = input('请输入配号个数：')
        sum += getSecurityWinningCode(code, lotteryCode, count)
    print('共需余额：{}元'.format(sum))


def getSecurityWinningCode(code, ownCode, count):
    balance = 0
    secUrl = 'http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?type=MD&sty=MDTOR&code={}'.format(code)
    r = requests.get(secUrl, timeout=TIME_OUT)
    if r.status_code == 200:
        #双引号
        #print(r.text[r.text.find('[') + 1: r.text.rindex(']')])
        #print(jsonLikeStr)
        #print(list(r.text)) 
        #print(json.loads(list(r.text)))
        
        jsonLikeStr = r.text[r.text.find('[{"'): r.text.rindex('"}]') + 3]
        d = eval(jsonLikeStr)
        winningCode = dict()
        for item in d:
            if('name' in item.keys() and 'value' in item.keys()):
                winningCode[int(item['name'])] = item['value'].split(',')

        print('证券代码：{}'.format(code))
        winList = matchSecurityWinningCode(winningCode, ownCode, int(count))
        if len(winList) > 0 and ipoDetailDict[code].issuePrice > 0:
            times = 1
            if code[:3] in ['600', '601', '603', '900']: #730 沪市
                times = 1000
            elif code[:3] in ['000', '002', '300']: # 深市
                times = 500
            else:
                print('Illegal code format: {}'.format(code))
                return 0
            balance = ipoDetailDict[code].issuePrice * times * len(winList)
            print('需为此新股留下余额：{}元\n'.format(balance))
    else:
        print('Response Status Code: {}'.format(r.status_code))
        r.raise_for_status()
    return balance


def matchSecurityWinningCode(dictCode, ownCode, length = 1):
    winningLst = list()
    while (length > 0):
        for key in dictCode:
            for item in dictCode[key]:
                if (ownCode[-key:] == item):
                    winningLst.append(ownCode)
                    print('中签号： {}'.format(ownCode))                
        length -= 1
        ownCode = str(int(ownCode) + 1)
    pass
    if (len(winningLst) == 0):
        print('无中签号')
    return winningLst

def main():
    loadIpoInfo()
    date = getTradeDay()
    getSecuritiesCode(date)


if __name__ == '__main__':
    main()

