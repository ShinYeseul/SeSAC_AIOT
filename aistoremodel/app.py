from flask import Flask, request, render_template, redirect, url_for, session,flash
import sys
from aistoremodel import *
import datetime
from wtforms import Form, StringField, PasswordField, TextAreaField, validators
import logging

app = Flask(__name__)

app.config['SECRET_KEY'] = 'aiot'

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=5)
    session.modified = True

@app.route("/", methods=['POST', 'GET'])
def index():
    return render_template('index.html')

@app.route("/sregister", methods=['POST', 'GET'])
def sregister():
    if request.method == 'POST':
        s_id = request.form['sId']
        s_name = request.form['sName']
        locate = request.form['locate']
        sPassword = request.form['sPassword']

        create_store(s_id, s_name, locate,sPassword)
        return redirect('/')

    return render_template('sregister.html')

@app.route("/stores", methods=['POST', 'GET'])
def stores():
    if request.method == 'POST':
        s_id = request.form['sId']

        return render_template('stores.html', stores = show_list(s_id))

    return render_template('stores.html', stores = show_list())

@app.route("/manage/<s_id>", methods=['POST', 'GET'])
def manage(s_id = 'nan'):
    if request.method == 'POST':
        if s_id == 'nan':
            s_id = request.form['sId']
            # Products 전체 쿼리 (리스트)
            products = Products.query.all()
            return render_template('manage.html',
                                    s_id = s_id,
                                    inventory=get_menu(s_id),
                                    products=products
                                    )
        else:
            p_id = request.form['pId']
            price = request.form['price']
            count = int(request.form['count'])
            set_product(s_id, p_id, price, count)
            # Products 전체 쿼리 (리스트)
            products = Products.query.all()
            return render_template('manage.html',
                                    s_id = s_id,
                                    inventory = get_menu(s_id),
                                    products = products)

    return render_template('manage.html', s_id = s_id, )

@app.route("/board/<s_id>", methods=['POST', 'GET'])
def board(s_id = 'nan'):
    # buy 페이지에서 뒤로가기 버튼 또는 메인페이지 버튼(nav바) 클릭시 세션에 이전 데이터가 저장되어있을수 있음
    # 따라서 다시 buy 페이지로 가기전에 미리 세션 초기화
    if 'count' in session:
        del session['count']
    if 'buy_product' in session:
        del session['buy_product']

    if request.method == 'POST':
        s_id = request.form['sId']
        sPassword = request.form['sPassword']
        ai_store = db_session.get(AiStore, s_id)
        pw = AiStore.query.filter(AiStore.s_id == s_id)
        for p in pw:
            if p.sPassword == sPassword:
                return render_template('board.html', s_id=s_id, sPassword=sPassword,menu=get_menu(ai_store.s_id))
            else:
                id = 'nan'
                print('로그인 안댕ㅠ')
                flash("이건 왜 안 뜨지")
                return render_template('board.html',
                                       s_id=id, )
    # if s_id != 'nan':
    #     ai_store = db_session.get(AiStore, s_id)
    #     return render_template('board.html',
    #                                s_id=s_id ,menu=get_menu(ai_store.s_id))
    else:
        return render_template('board.html',
                               s_id=s_id, )


@app.route("/buy/<s_id>/<p_id>", methods=['POST', 'GET'])
def buy(s_id, p_id):
    if 'buy_product' not in session:
        inventory = db_session.get(Inventory,(p_id,s_id))
        session['buy_product'] = {'p_name': inventory.product.name, 'price': inventory.price}

    alert = False
    if 'count' not in session:
        session['count'] = 1
    if request.method == 'POST':
        if request.form.get('plus') == '+':
            session['count'] +=1

        elif request.form.get('sub') == '-':
            if session['count'] > 1:
                session['count'] -=1

        else:
            if buy_product(p_id, s_id, session['count']):
                return redirect(url_for('board', s_id = s_id))
            else:
                alert = True

    return render_template('buy.html',
                           s_id=s_id, p_id = p_id,
                           product = session['buy_product'],
                           count = session['count'],
                           alert = alert
                           )

@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()



if __name__ == '__main__':
    app.run('0.0.0.0',9999, debug=True)