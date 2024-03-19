from pymongo import MongoClient
from pymongo import DESCENDING

from flask import Flask, render_template, jsonify, request
from flask.json.provider import JSONProvider
from flask_jwt_extended import JWTManager

import json
import sys
import hashlib, datetime, jwt

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.gonggu

SECRET_KEY = 'SECRETT'

@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_insert']
    pw_receive = request.form['pw_insert']
    name_receive = request.form['name_insert']
    phone_receive = request.form['phone_insert']
    #print('id: '+id_receive+' pw: '+pw_receive+' name: '+name_receive+' phone: '+phone_receive)
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest() #해시 함수 sha256(단방향) 사용해 암호화
    
    db.users.insert_one({'uid': id_receive, 'pw': pw_hash, 'uname': name_receive, 'phoneNum': phone_receive})

    return jsonify({'result': 'success'})

@app.route('/api/login', methods=['POST'])
def api_login():
    id_input = request.form['id_login']
    pw_input = request.form['pw_login']
    pw_hash = hashlib.sha256(pw_input.encode('utf-8')).hexdigest() #해시 함수 sha256(단방향) 사용해 암호화
    #print('id: '+id_input+' pw: '+pw_input)
    result = db.users.find_one({'uid': id_input, 'pw': pw_hash})

    #print(result)

    if result is not None:
        payload = {
            'uid': id_input,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=5)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 틀렸습니다'})


@app.route('/')
def home():
    return render_template('loginPage.html')

if __name__ == '__main__':
    print(sys.executable)
    app.run('0.0.0.0', port=5001, debug=True)