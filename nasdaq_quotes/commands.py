# -*- coding: utf-8 -*-
import itertools
from datetime import datetime
from urlparse import urlparse, parse_qsl
import csv

from concurrent import futures
import requests
import click
from scrapy.selector import Selector

from nasdaq_quotes.main_app import app


class DataLoader(object):
    def __init__(self, workers, tickers):
        self.thread_pool = futures.ThreadPoolExecutor(max_workers=workers)
        self.tickers = tickers
        super(DataLoader, self).__init__()

    def _load_insider_trades_page(self, stock_name, page=None):
        params = {'sortname': 'lastdate', 'sorttype': 1}
        if page:
            params['page'] = page

        res = requests.get('http://www.nasdaq.com/symbol/%s/insider-trades' % stock_name, params=params)
        if res.status_code == 200:
            hxs = Selector(text=res.content)
            if page is None:
                last_page = urlparse(hxs.xpath('//a[@id="quotes_content_left_lb_LastPage"]/@href').extract_first())
                last_page = int(dict(parse_qsl(last_page.query)).get('page', 0))
                last_page = last_page if last_page <= 10 else 10
                yield last_page

            table = hxs.xpath("//div[@class='genTable']//tr[position() > 1]")
            for tr in table:
                item = {
                    'stock_name': stock_name,
                    'insider_name': tr.xpath('./td[1]/a/text()').extract_first(),
                    'insider_id': tr.xpath('./td[1]/a/@href').extract_first().split('/')[-1],
                    'relation': tr.xpath('./td[2]/text()').extract_first(),
                    'last_date': datetime.strptime(tr.xpath('./td[3]/text()').extract_first(), '%m/%d/%Y'),
                    'transaction_type': tr.xpath('./td[4]/text()').extract_first(),
                    'owner_type': tr.xpath('./td[5]/text()').extract_first(),
                    'shares_trades': tr.xpath('./td[6]/text()').extract_first().replace(',', ''),
                    'last_price': tr.xpath('./td[7]/text()').extract_first(),
                    'shares_held': tr.xpath('./td[8]/text()').extract_first().replace(',', '')
                }
                yield item

    def _load_insider_trades(self, ticker):
        from nasdaq_quotes.models import db, InsiderTrade
        first_page = self._load_insider_trades_page(ticker)
        last_page = next(first_page)
        pages = xrange(2, last_page + 1)  # page=None - основная страница, далее нумерация с 2х
        results = self.thread_pool.map(lambda x: self._load_insider_trades_page(ticker, x), pages)
        with db.engine.begin() as t:
            t.execute(InsiderTrade.__table__.delete().where(InsiderTrade.stock_name == ticker))
            t.execute(InsiderTrade.__table__.insert(), list(itertools.chain(first_page, *results)))

    def _load_quote(self, quote):
        from nasdaq_quotes.models import db, Quote
        src_fields = ['date', 'close', 'volume', 'open', 'high', 'low']
        quote = quote.strip().lower()
        res = requests.post(
            'http://www.nasdaq.com/symbol/%s/historical' % quote,
            data='3m|true|%s' % (quote),
            headers={'Content-Type': 'application/json'}
        )
        data = list(csv.DictReader(res.content.split()[2:], src_fields))
        for i, row in enumerate(data):
            row['date'] = row['date'].replace('/', '-')
            row['stock_name'] = quote
            data[i] = row

        with db.engine.begin() as t:
            t.execute(Quote.__table__.delete().where(Quote.stock_name == quote))
            t.execute(Quote.__table__.insert(), data)

    def load(self):
        fs = []
        for quote in self.tickers:
            fs.append(self.thread_pool.submit(self._load_insider_trades, quote))
            fs.append(self.thread_pool.submit(self._load_quote, quote))
        futures.wait(fs)


@app.cli.command()
@click.option('-N', required=False, default=15, type=int, help='Threads count')
@click.argument('tickers')
def parse(n, tickers):
    with open(tickers) as tickers:
        tickers = {q.strip().lower() for q in tickers.readlines()}
        DataLoader(n, tickers).load()
