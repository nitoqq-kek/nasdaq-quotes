# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import DateField, SubmitField, SelectField, DecimalField
from wtforms.validators import Optional, DataRequired


class DateRangeForm(Form):
    date_from = DateField('Date from', validators=[Optional()], render_kw={'placeholder': 'YYYY-MM-DD'})
    date_to = DateField('Date to', validators=[Optional()], render_kw={'placeholder': 'YYYY-MM-DD'})
    submit = SubmitField('Go')


class DeltaCriteriaForm(Form):
    type = SelectField('Type', validators=[DataRequired()], choices=zip(*[['open', 'high', 'low', 'close']] * 2))
    value = DecimalField('Value', validators=[DataRequired()])
    submit = SubmitField('Go')
