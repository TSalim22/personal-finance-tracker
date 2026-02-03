import os
import csv
import io
from datetime import date
from decimal import Decimal, InvalidOperation
from flask import render_template, request, redirect, session, flash, abort, Response
from auth import db, make_app, login_required

CATEGORIES = ['Salary', 'Food', 'Travel', 'Bills', 'Shopping', 'Entertainment', 'Other']


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(30), nullable=False)
    kind = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    day = db.Column(db.Date, nullable=False)


def parse_transaction(form):
    description = form.get('description', '').strip()
    category, kind = form.get('category'), form.get('kind')
    try:
        amount = Decimal(form.get('amount', ''))
        day = date.fromisoformat(form.get('day', ''))
    except (InvalidOperation, ValueError):
        raise ValueError('Enter a valid amount and date.')
    if not amount.is_finite() or amount <= 0 or amount > Decimal('9999999999.99') or amount != amount.quantize(Decimal('.01')):
        raise ValueError('Use a positive amount with at most two decimal places.')
    if not description or len(description) > 120 or category not in CATEGORIES or kind not in ('income', 'expense'):
        raise ValueError('Enter a description, category and transaction type.')
    return dict(description=description, category=category, kind=kind, amount=amount, day=day)


def totals(transactions):
    income = sum((t.amount for t in transactions if t.kind == 'income'), Decimal('0'))
    spending = sum((t.amount for t in transactions if t.kind == 'expense'), Decimal('0'))
    categories = {}
    for item in transactions:
        if item.kind == 'expense':
            categories[item.category] = categories.get(item.category, 0) + float(item.amount)
    return income, spending, categories


def create_app(config=None):
    app = make_app('Personal Finance', 'A clear picture of your income and spending.', config)

    def owned(identifier):
        item = db.session.get(Transaction, identifier)
        if not item or item.user_id != session['user_id']:
            abort(404)
        return item

    def records():
        query = db.select(Transaction).where(Transaction.user_id == session['user_id'])
        month = request.args.get('month', '')
        if month:
            try:
                start = date.fromisoformat(month + '-01')
                end = date(start.year + (start.month == 12), start.month % 12 + 1, 1)
            except ValueError:
                abort(400)
            query = query.where(Transaction.day >= start, Transaction.day < end)
        return db.session.scalars(query.order_by(Transaction.day.desc(), Transaction.id.desc())).all()

    @app.get('/')
    @login_required
    def index():
        items = records()
        income, spending, categories = totals(items)
        return render_template('index.html', title='Dashboard', items=items, income=income,
            spending=spending, balance=income-spending, categories=categories,
            choices=CATEGORIES, today=date.today(), month=request.args.get('month',''))

    @app.post('/transactions')
    @login_required
    def add():
        try:
            values = parse_transaction(request.form)
        except ValueError as error:
            flash(str(error))
            return redirect('/')
        db.session.add(Transaction(user_id=session['user_id'], **values))
        db.session.commit()
        return redirect('/')

    @app.route('/transactions/<int:identifier>/edit', methods=['GET','POST'])
    @login_required
    def edit(identifier):
        item = owned(identifier)
        if request.method == 'POST':
            try:
                values = parse_transaction(request.form)
            except ValueError as error:
                flash(str(error))
                return render_template('edit.html', title='Edit transaction', item=item, choices=CATEGORIES), 400
            for key, value in values.items():
                setattr(item, key, value)
            db.session.commit()
            return redirect('/')
        return render_template('edit.html', title='Edit transaction', item=item, choices=CATEGORIES)

    @app.post('/transactions/<int:identifier>/delete')
    @login_required
    def delete(identifier):
        db.session.delete(owned(identifier))
        db.session.commit()
        return redirect('/')

    @app.get('/export')
    @login_required
    def export():
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Date','Description','Category','Type','Amount'])
        for item in records():
            # Prevent formulas in exported CSV files.
            description = item.description
            if description.lstrip().startswith(('=','+','-','@')):
                description = "'" + description
            writer.writerow([item.day, description, item.category, item.kind, item.amount])
        return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition':'attachment; filename=transactions.csv'})

    with app.app_context():
        db.create_all()
    return app


if __name__ == '__main__':
    create_app().run(host=os.getenv('HOST','127.0.0.1'),port=5000)
