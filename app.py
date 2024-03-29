from pymongo import MongoClient
from pymongo import DESCENDING
from bson.objectid import ObjectId

from flask import Flask, render_template, jsonify, request, redirect, url_for
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
db.history.delete_many({})

url_receive = 'https://www.coupang.com/vp/products/7455919074?itemId=18854921300&vendorItemId=85984112985&sourceType=srp_product_ads&clickEventId=48d7dd70-e651-11ee-b2bf-f0b2f521b948&korePlacement=15&koreSubPlacement=1&isAddedCart='
wow = True
minNum = 3
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
                                'pname': pname, 'minNum': minNum, 'state': '모집중', 'sid': sid, 'date': date, 'wow':1})
pid = str(result.inserted_id)
db.party.insert_one({'pid': pid, 'uid': sid})
db.users.insert_one({'uid':'abcd' , 'pw':'88d4266fd4e6338d13b845fcf289579d209c897823b9217da3e161936f031589',
'uname':'홍길동', 'phoneNum': '01083719379'})
db.users.insert_one({'uid':'xkdl3301' , 'pw':'88d4266fd4e6338d13b845fcf289579d209c897823b9217da3e161936f031589',
'uname':'이연준', 'phoneNum': '01012345678'})
db.users.insert_one({'uid':'dnwjd' , 'pw':'88d4266fd4e6338d13b845fcf289579d209c897823b9217da3e161936f031589',
'uname':'심우정', 'phoneNum': '01009871123'})
db.users.insert_one({'uid':'fufu98' , 'pw':'88d4266fd4e6338d13b845fcf289579d209c897823b9217da3e161936f031589',
'uname':'김혁준', 'phoneNum': '01012341234'})
firstfind = db.party.find({'pid':pid})
print("데이터를 넣자마자 find했을 때의 find 결과값 : ", firstfind)
listed = list(firstfind)
print(listed)
print(len(listed))

@app.route('/api/isToken', methods=['GET'])
def isToken():
    access_token = request.cookies.get('usertoken')
    try:
        decoded_token = jwt.decode(access_token, SECRET_KEY, algorithms=['HS256'])
        exp_time = decoded_token['exp'] #토큰 유효시간
        exp_datetime = datetime.datetime.utcfromtimestamp(exp_time) #토큰의 유효시간으로 UTC 시간대의 datetime 객체 생성
        current_time = datetime.datetime.utcnow() #현재시간
        if current_time > exp_datetime: #현재시간이 만료시간을 초과했는지
            print('2로그인 이동')
            return jsonify({'result': 'end'})
        # 만료된 토큰을 디코드
        decoded_token = jwt.decode(access_token, SECRET_KEY, algorithms=['HS256'])
    except jwt.exceptions.ExpiredSignatureError:
        # 만료된 토큰일 경우 로그인 페이지로 이동합니다.
        print('isToken 만료 로그인 이동')
        key = 'fail'
        return jsonify({'result': 'end'})
    return jsonify({'result': 'is'})

@app.route('/api/add/product', methods=['POST'])
def insert_prod():
    access_token = request.cookies.get('usertoken')
    print('access_token', access_token)
    if access_token is None:
        return render_template('logIn.html')
    try:
        decoded_token = jwt.decode(access_token, SECRET_KEY, algorithms=['HS256'])
        exp_time = decoded_token['exp'] #토큰 유효시간
        exp_datetime = datetime.datetime.utcfromtimestamp(exp_time) #토큰의 유효시간으로 UTC 시간대의 datetime 객체 생성
        current_time = datetime.datetime.utcnow() #현재시간
        if current_time > exp_datetime: #현재시간이 만료시간을 초과했는지
            return render_template('logIn.html')
        # 만료된 토큰을 디코드
        decoded_token = jwt.decode(access_token, SECRET_KEY, algorithms=['HS256'])
    except jwt.exceptions.ExpiredSignatureError:
        # 만료된 토큰일 경우 로그인 페이지로 이동합니다.
        key = 'fail'
        return render_template('logIn.html')

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
                                    'pname': pname, 'minNum': minNum, 'state': '모집중', 'sid': sid, 'date': date, 'wow':wow})

    pid = str(result.inserted_id)
    db.party.insert_one({'pid': pid, 'uid': sid})
    if db.products.find_one({'_id': ObjectId(pid)}):
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'failure'})


@app.route('/api/list', methods=['GET'])
def showlist():
    uid = request.args.get('uid')
    products = list(db.products.find({}).sort({"date":-1}))
    for data in products:
        now = datetime.datetime.now()
        data['date'] = (data['date'] - now).days
        if data['date'] < 0:
            db.products.delete({'pid':pid})
            db.party.delete({'pid':pid})
            products.remove(data)
            continue
        pid = str(data['_id'])
        #print("pid : ", pid)
        #print("find의 data type : ", type(db.party.find({'pid':pid})))
        print("find의 결과 : ", db.party.find({'pid':pid}))
        print("pid : ", pid, " uid : ", uid)
        list_founded = list(db.party.find({'pid':pid}))
        print(list_founded)
        curNum = len(list_founded)
        print("curNum : ", curNum)
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

    return jsonify({'result': 'success', 'list': products})


@app.route('/api/complete', methods=['POST'])
def complete():
    pid = request.form['pid']
    product = db.products.find_one({'_id': ObjectId(pid)})
    print("product found : ", product)
    price = product['price']
    imgurl = product['imgurl']
    pname = product['pname']
    uid = product['sid']
    date = datetime.datetime.now()
    phoneNum = db.users.find_one({'uid': uid})['phoneNum']

    db.history.insert_one({'pid': pid, 'price': price, 'imgurl': imgurl,
                                 'pname': pname, 'date': date, 'uid': uid, 'phoneNum': phoneNum})

    print("프로덕트 findone : ", db.products.find_one({'pid': pid}))
    db.products.delete_one({'_id': ObjectId(pid)})

    if db.history.find_one({'pid':pid}):
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'failure'})



@app.route('/api/party/data', methods=['POST'])
def showdata():
    pid = request.form['pid']
    uid = request.form['uid']
    ret = []
    
    data = list(db.party.find({'pid':str(pid)}))
    for person in data:
        print(person)
        uidfind = person['uid']
        if uid == uidfind:
            continue
        else :
            found = db.users.find_one({'uid':uidfind})
            found.pop('uid', None)
            found.pop('pw', None)
            found.pop('_id', None)
            ret.append(found)
        
    return jsonify({'result':'success', 'list':ret})


@app.route('/api/buy/', methods=['POST'])
def buy():
    pid = request.form['pid']
    print("pid : ", pid)
    result = db.products.update_one({'_id': ObjectId(pid)}, {'$set': {'state': '배송중'}})
    print("구매 버튼을 눌렀습니다")
    if result.acknowledged:
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'failure'})


@app.route('/api/delete/product', methods=['POST'])
def delete():
    pid = request.form['pid']
    uid = request.form['uid']
    access_token = request.cookies.get('usertoken')
    try:
        decoded_token = jwt.decode(access_token, SECRET_KEY, algorithms=['HS256'])
        res1 = db.products.delete_one({'_id': ObjectId(pid)})
        res2 = db.party.delete_many({'pid':pid})
        return jsonify({'result':'success'})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'failure', 'message': '로그인 만료!'}) #만료된 토큰
    except jwt.DecodeError:
        return jsonify({'result': 'failure', 'message': '유효하지 않은 토큰!'}) #유효하지 않은 토큰

      
@app.route('/api/party/cancel', methods=['POST'])
def cancel():
    pid = request.form['pid']
    uid = request.form['uid']
    print(db.party.find_one({'pid':str(pid),'uid':uid}))
    access_token = request.cookies.get('usertoken')
    try:
        decoded_token = jwt.decode(access_token, SECRET_KEY, algorithms=['HS256'])
        result = db.party.delete_one({'pid': str(pid), 'uid': uid})
        if result.deleted_count:
            return jsonify({'result': 'success'})
        else:
            return jsonify({'result': 'failure'})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'failure', 'message': '로그인 만료!'}) #만료된 토큰
    except jwt.DecodeError:
        return jsonify({'result': 'failure', 'message': '유효하지 않은 토큰!'}) #유효하지 않은 토큰

        

@app.route('/api/party', methods=['POST'])
def participate():
    print("참여 과정 시작!")
    pid = request.form['pid']
    uid = request.form['uid']
    access_token=request.cookies.get('usertoken')
    try:
        decode_token = jwt.decode(access_token, SECRET_KEY, algorithms=['HS256'])
        result = db.party.insert_one({'pid': pid, 'uid': uid})
        ID = result.inserted_id
        if db.party.find_one({'_id': ID}):
            return jsonify({'result': 'success'})
        else:
            return jsonify({'result': 'failure'})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'failure', 'message': '로그인 만료!'}) #만료된 토큰
    except jwt.DecodeError:
        return jsonify({'result': 'failure', 'message': '유효하지 않은 토큰!'}) #유효하지 않은 토큰


@app.route('/api/user/info', methods=['GET'])
def info():
    uid = request.args.get('uid')
    print("uid in user info request : ", uid)
    res = db.users.find_one({'uid':uid})
    res.pop('_id', None)
    res.pop('pw', None)
    print((res))

    return jsonify({'result':'success', 'info':res})

@app.route('/api/list/my',methods=['GET'])
def mylist():
    uid = request.args.get('uid')
    selectMode = request.args.get('selectMode')
    
    if selectMode == "suggestor":
        product = list(db.products.find({'sid':uid}))
        for data in product:
            pid = str(data['_id'])
            data['_id']=pid
            now = datetime.datetime.now()
            data['date'] = (data['date'] - now).days
            if data['date'] < 0:
                db.products.delete({'pid':pid})
                db.party.delete({'pid':pid})
                products.remove(data)
                continue
            list_founded = list(db.party.find({'pid':pid}))
            curNum = len(list_founded)
            data['curNum']=curNum
            sname = db.users.find_one({'uid':data['sid']})['uname']
            data['sname'] = sname

        return jsonify({'result':'success','list':product})
    
    elif selectMode == "joined":
        print("내가 참여한 공구 목록!")
        ret = []
        joinproduct = list(db.party.find({'uid':uid}))
        for data in joinproduct:
            print(data)
            pid = str(data['pid'])
            list_founded = list(db.party.find({'pid':pid}))
            curNum = len(list_founded)
            print(curNum)
            product = db.products.find_one({'_id':ObjectId(pid)})
            if product['sid'] == uid:
                continue
            print(product)
            print(type(product))
            now = datetime.datetime.now()
            product['date'] = (product['date'] - now).days
            product['_id']=pid
            product['curNum'] = curNum
            sid = product['sid']
            sname = db.users.find_one({'uid':sid})['uname']
            product['sname'] = sname
            ret.append(product)
        
        return jsonify({'result':'success', 'list':ret})
    
    elif selectMode == 'completed':
        joined = list(db.history.find({'uid':uid}))
        for data in joined:
            data.pop('_id', None)
        return jsonify({'result':'success', 'list':joined})
    else:
        return jsonify({'result':'failure'})


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
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
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
    access_token = request.cookies.get('usertoken')
    print('token : ', access_token)
    try:
        decoded_token = jwt.decode(access_token, SECRET_KEY, algorithms=['HS256'])
        print('decoded: ', decoded_token)
        uid = decoded_token['uid']
        print('uid', uid)
        userdata = db.users.find_one({'uid':uid})
        return render_template('myPage.html', name=userdata['uname'], id = userdata['uid'], phoneNum=userdata['phoneNum'])
    except jwt.ExpiredSignatureError:
        return redirect(url_for('toLogin', message='로그인이 만료되었습니다!'))

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
    app.run('0.0.0.0', port=5001, debug=True)