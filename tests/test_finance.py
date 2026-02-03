from decimal import Decimal
from auth import db
from app import Transaction,parse_transaction,totals
import pytest

def values(**overrides):
    return dict(description='Food shop',category='Food',kind='expense',amount='12.34',day='2026-10-01',**overrides)

def test_transactions_money_edit_export_and_delete(logged_in,app):
    logged_in.post('/transactions',data=values())
    logged_in.post('/transactions',data={'description':'Salary','category':'Salary','kind':'income','amount':'100.00','day':'2026-10-02'})
    with app.app_context():
        items = db.session.scalars(db.select(Transaction)).all()
        income,spending,categories = totals(items)
        assert income-spending==Decimal('87.66')
        identifier = items[0].id
    assert b'87.66' in logged_in.get('/').data
    logged_in.post(f'/transactions/{identifier}/edit',data={'description':'=formula','category':'Food','kind':'expense','amount':'10.00','day':'2026-10-01'})
    export = logged_in.get('/export?month=2026-10')
    assert b"'=formula" in export.data
    assert b'Salary' not in logged_in.get('/?month=2026-09').data.split(b'<tbody>')[-1]
    logged_in.post(f'/transactions/{identifier}/delete')
    assert b'=formula' not in logged_in.get('/').data

def test_other_user_and_invalid_filter(logged_in,app):
    logged_in.post('/transactions',data=values())
    with app.app_context(): identifier = db.session.scalar(db.select(Transaction.id))
    second = app.test_client()
    second.post('/register',data={'username':'another','password':'another-pass'})
    assert second.get(f'/transactions/{identifier}/edit').status_code==404
    assert second.post(f'/transactions/{identifier}/delete').status_code==404
    assert b'Food shop' not in second.get('/export').data
    assert logged_in.get('/?month=2026-99').status_code==400

@pytest.mark.parametrize('amount',['NaN','Infinity','-1','0','1.001','abc','99999999999'])
def test_invalid_amounts(amount):
    data = values(); data['amount']=amount
    with pytest.raises(ValueError): parse_transaction(data)
