# -*- coding: utf-8 -*-
from operator import itemgetter

from flask import Blueprint, render_template, request
from flask_jsontools import make_json_response

from nasdaq_quotes.forms import DateRangeForm, DeltaCriteriaForm
from nasdaq_quotes.main_app import app, db
from nasdaq_quotes.models import Quote, InsiderTrade

website = Blueprint('site', __name__, url_prefix='', template_folder='templates')
api = Blueprint('api', __name__, url_prefix='/api', url_defaults={'json': True})


@website.route('/')
def index():
    # TODO: по хорошему нужно нормализовать данные и вынести названия акций компаний в отдельную таблицу
    tickers = map(itemgetter(0), Quote.query.with_entities(Quote.stock_name).distinct(Quote.stock_name).all())
    return render_template('index.html', **{
        'tickers': tickers
    })


@website.route('/<ticker>')
@api.route('/<ticker>')
def ticker(ticker, json=False):
    quotes = Quote.query.filter(Quote.stock_name.ilike(ticker)).all()
    ctx = {
        'quotes': quotes,
        'ticker': ticker
    }
    if json:
        return make_json_response(ctx)
    return render_template('ticker.html', **ctx)


@website.route('/<ticker>/analytics')
@api.route('/<ticker>/analytics')
def analytics(ticker, json=False):
    ctx = {
        'ticker': ticker
    }
    quotes = Quote.query.filter(Quote.stock_name.ilike(ticker))
    form = DateRangeForm(request.args, csrf_enabled=False)
    if form.validate():
        date_from, date_to = form.date_from.data, form.date_to.data
        if date_from and date_to:
            date_from, date_to = sorted([date_from, date_to])

        if date_from:
            quotes = quotes.filter(Quote.date >= date_from)
        if date_to:
            quotes = quotes.filter(Quote.date <= date_to)

        start = quotes.order_by(Quote.date).first()
        end = quotes.order_by(Quote.date.desc()).first()
        if start and end:
            diff = end.diff(start)
            ctx['diff'] = diff
            ctx['start'] = start
            ctx['end'] = end

    if json:
        if form.errors:
            ctx['errors'] = form.errors
        return make_json_response(ctx)

    ctx['form'] = form

    return render_template('analytics.html', **ctx)


@website.route('/<ticker>/delta')
@api.route('/<ticker>/delta')
def delta(ticker, json=False):
    ctx = {
        'ticker': ticker
    }
    form = DeltaCriteriaForm(request.args, csrf_enabled=False)
    if (json or 'submit' in request.args) and form.validate():

        field = getattr(Quote, form.type.data)
        a = db.alias(db.select([
            (db.func.first_value(Quote.date).over(order_by=Quote.date)).label('date_from'),
            Quote.date.label('date_to'),
            (field - db.func.first_value(field).over(order_by=Quote.date)).label('diff')
        ]).order_by(Quote.date), name='a')
        value = form.value.data
        if value > 0:
            criteria = a.c.diff > value
        else:
            criteria = a.c.diff < value
        result_delta = db.select([a], from_obj=a, bind=db.engine).where(criteria).limit(1).execute().fetchone()
        ctx['delta'] = dict(result_delta or {})

    if json:
        if form.errors:
            ctx['errors'] = form.errors
        return make_json_response(ctx)
    ctx['form'] = form
    return render_template('delta.html', **ctx)


@website.route('/<ticker>/insider')
@api.route('/<ticker>/insider')
@website.route('/<ticker>/insider/<insider_id>')
@api.route('/<ticker>/insider/<insider_id>')
def insider_trades(ticker, insider_id=None, json=False):
    trades = InsiderTrade.query.filter(InsiderTrade.stock_name.ilike(ticker))
    if insider_id:
        trades = trades.filter(InsiderTrade.insider_id.ilike(insider_id))
    trades = trades.all()
    ctx = {
        'trades': trades,
        'ticker': ticker
    }
    if json:
        return make_json_response(ctx)
    return render_template('insider_trades.html', **ctx)


app.register_blueprint(website)
app.register_blueprint(api)
