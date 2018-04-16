# -*- coding:utf-8 -*-
import re
import os
import json
import random
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from pymongo import MongoClient

from tornado.options import define, options
import requests

define("port", default=8000, help="run on the given port", type=int)

client=MongoClient('localhost',27017)
db = client['industry']['loan_home']

TITLE = {'popularity': '人气指数',
         'volume': '成交指数'}
URL = {u'成交人气指数': 'https://shuju.wdzj.com/industry-p2pindex.html',
       u'行业参考收益率': 'https://shuju.wdzj.com/index-i-5-1.html',
       u'行业期限': 'https://shuju.wdzj.com/index-i-6-1.html',
       u'新增累计平台': 'https://shuju.wdzj.com/index-i-0-1.html',
       u'区域分布': 'https://shuju.wdzj.com/index-i-1-1.html',
       u'平台类型': 'https://shuju.wdzj.com/index-i-2-1.html',
       u'行业成交量': 'https://shuju.wdzj.com/index-i-4-1.html',
       u'行业人气': 'https://shuju.wdzj.com/index-i-3-1.html'}

def loan_info(argu):
    data = db.find_one({'url': URL.get(argu)})['data']
    popularity = data['popularity']
    volume = data['volume']
    date = data['date']

    _dic = {"title": argu,
            "legend": ["人气指数", "成交指数"],
            "xAxis": date,
            "series": {"人气指数": popularity,
                       "成交指数": volume},
            "start": 60,
            "end": 80}
    return _dic


def new_info(argu):
    with open('./html/wang.html', 'r') as f:
        data = f.read()
    from lxml import html
    doc = html.fromstring(data)
    data = []
    a = doc.xpath('//ul[@class="numlist"]//li//a')
    for i in a[14:80]:
        _dic = {}
        _dic[i.xpath('@title')[0]] = i.xpath('@href')[0]
        data.append(_dic)

    if argu == u'网贷之家':
        data = data[:10]
    elif argu == u'第一财经':
        data = data[10:]
    elif argu == u'中证网':
        data = data[20:]
    return {'data': data}


class LoanHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, param):
        if param in ['loan_home.html', 'loan_home']:
            data = json.dumps(loan_info(u'成交人气指数'))
        elif param in ['news.html', 'news']:
            data = new_info(u'网贷之家')['data']
        elif param in ['app.html', 'app']:
            with open('./html/app.json','r') as f:
                data = json.loads(f.read())['datas']['list']
        elif param in ['zhishu.html', 'zhishu']:
            data = {"title": "微贷网",
                    "legend": ["微贷网"],
                    "xAxis": ["周一","周二","周三","周四","周五","周六","周日"],
                    "series": {"微贷网": [10, 12, 21, 54, 260, 830, 710]},
                    "start": 20,
                    "end": 80}
            data = json.dumps(data)
        elif param in ['stock.html', 'stock']:
            data = {}
        self.render('templates/%s' % param, chart_data=data)


class AjaxHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        print('--------data_received----------')

    def post(self):
        web = self.get_argument("web")
        argu = self.get_argument("message")
        if web == 'loan':
            data = loan_info(argu)
        elif web == 'new':
            data = new_info(argu)
        elif web == 'zhishu':
            data = {"title": "微贷网",
                    "legend": ["微贷网"],
                    "xAxis": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
                    "series": {"微贷网": []},
                    "start": 20,
                    "end": 80}
            if argu == u'搜索热度':
                data['series']['\xe5\xbe\xae\xe8\xb4\xb7\xe7\xbd\x91'].extend([10, 12, 21, 54, 260, 830, 710])
            elif argu == u'微信热度':
                data['series']['\xe5\xbe\xae\xe8\xb4\xb7\xe7\xbd\x91'].extend([20, 22, 41, 374, 160, 230, 110])
        elif web == 'stock':
            res = requests.get('http://hq.sinajs.cn/list=%s'%argu.strip()).content
            stock_info = re.findall('"(.*?)"', res)[0]
            list_info = stock_info.split(',')
            list_info[0] = list_info[0].decode('gbk')
            data = {'data': list_info[:10]}

        self.write(data)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    settings = {"templates_path": os.path.join(os.path.dirname(__file__), "templates"),
                "static_path": os.path.join(os.path.dirname(__file__), "static")}
    app = tornado.web.Application(
        [(r"/loan/(.*?)", LoanHandler,),
         (r"/ajax", AjaxHandler,)],
        debug=True,
        **settings
    )

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
