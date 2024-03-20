from pymongo import MongoClient
from pymongo import DESCENDING

from flask import Flask, render_template, jsonify, request
from flask.json.provider import JSONProvider
from flask_jwt_extended import JWTManager

import requests
import re
from bs4 import BeautifulSoup

import json
import sys
import hashlib
import datetime
import jwt

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.gonggu

SECRET_KEY = 'SECRETT'


db.users.delete_many({})
db.products.delete_many({})
db.party.delete_many({})

url_receive = 'https://www.coupang.com/vp/products/7455919074?itemId=18854921300&vendorItemId=85984112985&sourceType=srp_product_ads&clickEventId=48d7dd70-e651-11ee-b2bf-f0b2f521b948&korePlacement=15&koreSubPlacement=1&isAddedCart='
wow = True
minNum = 5
sid = 'abcd'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
           "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3"}
response = requests.get(url_receive, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
pname = soup.select_one(".prod-buy-header__title").text.strip()
img = soup.select_one(".prod-image__detail").get('src')
sale_price = soup.select_one(".prod-sale-price")
coupon_price = soup.select_one(".prod-coupon-price")
if wow and coupon_price:
    price = coupon_price.select_one(".total-price").text.strip()
elif wow and sale_price:
    price = sale_price.select_one(".total-price").text.strip()
elif not wow and sale_price:
    price = sale_price.select_one(".total-price").text.strip()
else:
    price = coupon_price.select_one(".total-price").text.strip()
now = datetime.datetime.now()
date = now + datetime.timedelta(days=7)

result = db.products.insert_one({'url': url_receive, 'price': price, 'imgurl': img,
                                'pname': pname, 'minNum': minNum, 'state': '모집 중', 'sid': sid, 'date': date})
pid = result.inserted_id
db.party.insert_one({'pid': pid, 'uid': sid})
db.users.insert_one({'uid':'abcd' , 'pw':'88d4266fd4e6338d13b845fcf289579d209c897823b9217da3e161936f031589',
'uname':'abcd', 'phoneNum': '01099999999'})

@app.route('/api/add/product', methods=['POST'])
def insert_prod():
    url_receive = request.form['url']
    wow = request.form['wow']
    minNum = request.form['minNum']
    sid = request.form['uid']

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
               "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3"}
    response = requests.get(url_receive, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    pname = soup.select_one(".prod-buy-header__title").text.strip()
    img = soup.select_one(".prod-image__detail").get('src')
    sale_price = soup.select_one(".prod-sale-price")
    coupon_price = soup.select_one(".prod-coupon-price")
    if wow and coupon_price:
        price = coupon_price.select_one(".total-price").text.strip()
    elif wow and sale_price:
        price = sale_price.select_one(".total-price").text.strip()
    elif not wow and sale_price:
        price = sale_price.select_one(".total-price").text.strip()
    else:
        price = coupon_price.select_one(".total-price").text.strip()

    now = datetime.datetime.now()
    date = now + datetime.timedelta(days=7)

    result = db.products.insert_one({'url': url_receive, 'price': price, 'imgurl': img,
                                    'pname': pname, 'minNum': minNum, 'state': '모집 중', 'sid': sid, 'date': date})

    pid = result.inserted_id
    db.party.insert_one({'pid': pid, 'uid': sid})
    if db.products.find_one({'_id': pid}):
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'failure'})


@app.route('/api/list', methods=['GET'])
def showlist():
    uid = request.args.get('uid')
    print(uid)
    print('받은 uid의 타입 : ', type(uid))
    products = list(db.products.find({}).sort("date"))
    for data in products:
        now = datetime.datetime.now()
        data['date'] = (data['date'] - now).days
        if data['date'] < 0:
            db.products.delete_one({'pid':pid})
            db.party.delete_one({'pid':pid})
            products.remove(data)
            continue
        pid = data['_id']
        print("find의 data type : ", type(db.party.find_one({'pid':pid})))
        curNum = len(list(db.party.find({'pid':pid})))
        data['curNum']=curNum
        if data['sid'] == uid:
            joined = 1
        ### 제안자면 joined == 1
        elif db.party.find_one({'pid':pid,'uid':uid}) is not None:
            joined = 2
        ### 참여한 구매자면 joined == 2
        else:
            joined = 3
        ### 참여 안한 구매자면 joined == 3
        data['joined'] = joined
        data['_id'] = str(data['_id'])
        sname = db.users.find_one({'uid':data['sid']})['uname']
        data['sname'] = sname
    print("find 결과 : ", db.party.find_one({'pid':pid,'uid':uid}))
    print("위에 거 type : ", type(db.party.find_one({'pid':pid,'uid':uid})))
    print(products[0])
    return jsonify({'result': 'success', 'list': products})

@app.route('/api/party', methods=['POST'])
def participate():
    print("참여 과정 시작!")
    pid = request.form['pid']
    uid = request.form['uid']
    print("pid : ", pid)
    print("uid : ", uid)
    print("파티에서의 uid 타입 : ", type(uid))
    print((db.party.find_one({'pid': pid, 'uid': uid})))
    result = db.party.insert_one({'pid': pid, 'uid': uid})
    ID = result.inserted_id
    print("참여 완료!")
    print(((db.party.find_one({'pid': pid, 'uid': uid}))))
    print("find의 data type : ", type(db.party.find_one({'pid': pid, 'uid': uid})))
    if db.party.find_one({'_id': ID}):
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'failure'})

@app.route('/api/user/info', methods=['GET'])
def info():
    uid = request.args.get('uid')
    print("uid in user info request : ", uid)
    res = db.users.find_one({'uid':uid})
    res.pop('_id', None)
    res.pop('pw', None)
    print((res))

    return jsonify({'result':'success', 'info':res})

@app.route('/api/signup', methods=['POST'])
def api_register():
    id_receive = request.form['uid']
    pw_receive = request.form['pw']
    name_receive = request.form['name']
    phone_receive = request.form['phoneNum']
    print('id: '+id_receive+' pw: '+pw_receive +
          ' name: '+name_receive+' phone: '+phone_receive)
    pw_hash = hashlib.sha256(pw_receive.encode(
        'utf-8')).hexdigest()  # 해시 함수 sha256(단방향) 사용해 암호화

    result = db.users.insert_one(
        {'uid': id_receive, 'pw': pw_hash, 'uname': name_receive, 'phoneNum': phone_receive})

    return jsonify({'result': 'success'})


@app.route('/api/login', methods=['POST'])
def api_login():
    id_input = request.form['uid']
    pw_input = request.form['pw']
    pw_hash = hashlib.sha256(pw_input.encode(
        'utf-8')).hexdigest()  # 해시 함수 sha256(단방향) 사용해 암호화
    result = db.users.find_one({'uid': id_input, 'pw': pw_hash})

    print(result)

    if result is not None:
        payload = {
            'uid': id_input,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=5)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        print(token)
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 틀렸습니다'})


@app.route('/')
def home():
    return render_template('logIn.html')


@app.route('/toMain')
def toMain():
    return render_template('main.html')


@app.route('/toLogin')
def toLogin():
    return render_template('logIn.html')


@app.route('/toSignUp')
def toSignUp():
    return render_template('signUp.html')

@app.route('/toMyPage')
def toMyPage():
    return render_template('myPage.html')

@app.route('/getCookie', methods=['GET'])
def getCookie():
    try:
        userToken = request.cookies.get('usertoken')
        print(userToken)
        tokenDecode = jwt.decode(userToken, SECRET_KEY, algorithms=['HS256'])
        print(tokenDecode)
        return jsonify({'uid': tokenDecode})
    except:
        print('error')
        
@app.route('/api/check/Duplicate', methods=['POST'])
def check():
    id_give = request.form['inputId']
    print(id_give)

    if db.users.find_one({'uid':id_give}) is None:
        return jsonify({'result':'success'})
    else:
        return jsonify({'result':'failure'})
       

if __name__ == '__main__':
    print(sys.executable)
    app.run('0.0.0.0', port=5000, debug=True)


@app.route('/api/prod/ing/show', methods=['POST'])
def ingshow():
    uid = request.form['uid_give']
    prod_list = list(db.products.find({'sid': 'uid'}))
    if prod_list:
        return jsonify({'result': 'success', 'products_list': prod_list})
    else:
        return jsonify({'result': 'failure'})


@app.route('/api/prod/in/show', methods=['POST'])
def inshow():
    uid = request.form['uid_give']
    pidlist = list(db.party.find({'uid': uid}))
    prod_list = []
    for pid in pidlist:
        prod = db.products.find({'_id': pid})
        prod_list.append(prod)

    if prod_list:
        return jsonify({'result': 'success', 'products_list': prod_list})
    else:
        return jsonify({'result': 'failure'})


@app.route('/api/history/show', methods=['POST'])
def hisshow():
    uid = request.form['uid_give']
    his_list = list(db.history.find({'uid': uid}))
    if his_list:
        return jsonify({'result': 'success', 'products_list': his_list})
    else:
        return jsonify({'result': 'failure'})


@app.route('/api/complete', methods=['POST'])
def complete():
    pid = request.form['pid']
    product = db.products.find_one({'_id': pid})
    price = product['price']
    imgurl = product['img']
    pname = product['pname']
    uid = product['sid']
    date = datetime.datetime.now()
    phoneNum = db.users.find_one({'uid': uid})['phoneNum']

    res1 = db.history.insert_one({'pid': pid, 'price': price, 'imgurl': imgurl,
                                 'pname': pname, 'date': date, 'uid': uid, 'phoneNum': phoneNum})
    ID = res1.inserted_id
    res2 = db.products.delete_one({'pid': pid})
    delCount = res2.deleted_count
    if db.products.find_one({'_id': ID}) and delCount:
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'failure'})

      
@app.route('/api/party/cancel', methods=['POST'])
def cancel():
    pid = request.form['pid']
    uid = request.form['uid']

    result = db.party.delete_one({'pid': pid, 'uid': uid})
    if result.deleted_count:
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'failure'})


@app.route('/api/buy/', methods=['POST'])
def buy():
    pid = request.form['pid']
    result = db.products.update_one({'_id': pid}, {'$set': {'state': '배송중'}})
    if result.acknowledged:
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'failure'})

@app.route('/api/delete/product', methods=['POST'])
def delete():
    pid = request.form['pid']
    uid = request.form['uid']
    res1 = db.products.delete_one({'_id':pid})
    res2 = db.party.delete_many({'pid':pid})

    return jsonify({'result':'success'})