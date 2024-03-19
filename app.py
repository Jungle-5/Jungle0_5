from pymongo import MongoClient
import requests
import re
from bs4 import BeautifulSoup
from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.jungle0


@app.route('/')
def home():
    return 'This is Home!'

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000,debug=True)

@app.route('/prod', methods=['POST'])
def show_prod():
    url_receive = request.form['url_give']
    date_receive = request['data_give']

    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36', "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3"}
    response = requests.get(url_receive, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    pname = soup.select_one(".prod-buy-header__title").text.strip()
    img = soup.select_one(".prod-image__detail").get('src')
    sale_price = soup.select_one(".prod-sale-price")
    coupon_price = soup.select_one(".prod-coupon-price")
    if sale_price:
        sale_price = sale_price.select_one(".total-price").text.strip()
    else:
        sale_price=""
    if coupon_price:
        coupon_price = coupon_price.select_one(".total-price").text.strip()
    else:
        coupon_price=""

@app.route('/api/check/Duplicate', methods=['POST'])
def check():
    id_give = request.form['inputId']
    user = db.users.find({'uid':id_give})
    if user:
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'failure'})
