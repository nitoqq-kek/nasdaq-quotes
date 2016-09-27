# -*- coding: utf-8 -*-
from main_app import db
from flask_jsontools import JsonSerializableBase


class Quote(db.Model, JsonSerializableBase):
    __tablename__ = 'quote'

    id = db.Column(db.BigInteger, primary_key=True)
    stock_name = db.Column(db.String(20), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    close = db.Column(db.Numeric)
    volume = db.Column(db.Numeric)
    open = db.Column(db.Numeric)
    high = db.Column(db.Numeric)
    low = db.Column(db.Numeric)
    __table_args__ = (
        db.UniqueConstraint('stock_name', 'date', name='quote--stock_name-date-unique'),
    )

    def diff(self, other):
        assert self.stock_name == other.stock_name, "Can't compute diff with different stocks"
        res = {}
        for f in ('close', 'volume', 'open',  'high',  'low'):
            res[f] = getattr(self, f) - getattr(other, f)
        return res


class InsiderTrade(db.Model, JsonSerializableBase):
    __tablename__ = 'insider_trade'

    id = db.Column(db.BigInteger, primary_key=True)

    insider_name = db.Column(db.String(), nullable=False)
    insider_id = db.Column(db.String(), nullable=False, index=True)
    relation = db.Column(db.String(), nullable=False)

    stock_name = db.Column(db.String(20), nullable=False, index=True)

    last_date = db.Column(db.Date, nullable=False, index=True)
    transaction_type = db.Column(db.String())
    owner_type = db.Column(db.String())
    shares_traded = db.Column(db.Integer())
    last_price = db.Column(db.Numeric)
    shares_held = db.Column(db.Numeric)
