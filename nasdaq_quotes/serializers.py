# -*- coding: utf-8 -*-
from decimal import Decimal
import datetime
from flask_jsontools import DynamicJSONEncoder


class ApiJSONEncoder(DynamicJSONEncoder):
    def default(self, o):
        # Custom formats
        if isinstance(o, datetime.datetime):
            return o.isoformat(' ')
        if isinstance(o, datetime.date):
            return o.isoformat()
        if isinstance(o, set):
            return list(o)
        if isinstance(o, Decimal):
            return str(o)
        return super(ApiJSONEncoder, self).default(o)
