import pymysql
from flaskext.mysql import MySQL
from flask import request, Flask, jsonify
import requests
import json
import http.client
from datetime import date
import random

app = Flask(__name__)
mysql = MySQL()
app.config['DEBUG'] = True

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'test'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
mysql.init_app(app)


def random_id():
    res = ""
    for i in range(15):
        res = res+str(random.randrange(0, 9))
    return res


def get_place(cat, id):
    try:
        _data = {
            'id': id
        }
        _headers = {
            'key': "8673346f00df697bd0b951de5f847598",
            'content-type': "application/x-www-form-urlencoded"
        }
        url = "	https://api.rajaongkir.com/starter/" + cat
        res = requests.get(url, params=_data, headers=_headers)
        if cat == "city" or cat == "province":
            if cat == "city":
                return res.json()['rajaongkir']['results']['city_name']
            else:
                return res.json()['rajaongkir']['results']['province']
        else:
            return res.json()['rajaongkir']
    except Exception as e:
        res = "not found"
        return res


def get_cost(origin, destination, weight, courier):
    try:
        conn = http.client.HTTPSConnection("api.rajaongkir.com")

        payload = "origin=" + origin + "&destination=" + destination + "&weight=" + weight + "&courier=" + courier

        headers = {
            'key': "8673346f00df697bd0b951de5f847598",
            'content-type': "application/x-www-form-urlencoded"
        }

        conn.request("POST", "/starter/cost", payload, headers)

        res = conn.getresponse()
        data = res.read()

        return json.loads(data)['rajaongkir']['results'][0]['costs'][0]['cost'][0]['value']
    except Exception as e:
        res = "not found"
        return res


@app.route('/api/order', methods=['GET', 'POST'])
def index():
    global cursor, conn
    if request.method == 'GET':
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute("SELECT * FROM orders")
            res = cursor.fetchall()
        except Exception as e:
            return e
        finally:
            cursor.close()
            conn.close()
    elif request.method == 'POST':
        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            _weight = request.args.get('weight')
            _courier = request.args.get('courier')
            _cost = get_cost(str(request.args.get('origin')), str(request.args.get('destination')), str(_weight),
                             _courier)
            _origin = get_place('city', request.args.get('origin'))
            _destination = get_place('city', request.args.get('destination'))
            if _cost != "not found" and _origin != "not found" and _destination != "not found":
                _id = random_id()
                _name = request.args.get('name')
                _goods = request.args.get('goods')
                _status = "packing"
                _date = date.today().strftime("%d/%m %Y")
                _updatedDate = date.today().strftime("%d/%m/%Y")

                sql = """INSERT INTO orders(id, name, origin, destination, goods, weight, cost, courier, status, date, updatedDate) 
                         VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                data = (_id, _name, _origin, _destination, _goods, str(_weight), _cost, _courier, _status, _date,
                        _updatedDate)
                cursor.execute(sql, data)
                conn.commit()
                res = {
                    'message': 'Success',
                    'data': {
                        'id': _id,
                        'name': _name,
                        'origin': _origin,
                        'destination': _destination,
                        'goods': _goods,
                        'cost': _cost,
                        'courier': _courier,
                        'status': _status,
                        'date': _date,
                    }
                }
            else:
                notfound = []
                if _origin == "not found":
                    notfound.append("Origin")
                if _destination == "not found":
                    notfound.append("Destination")
                if _cost == "not found" and _origin != "not found" and _destination != "not found":
                    notfound.append("Courier")
                res = {
                    'message': 'Data Tidak Ditemukan, Periksa Kembali Parameter',
                    'null': notfound
                }
        except Exception as e:
            return e
        finally:
            cursor.close()
            conn.close()
    else:
        res = [{
            'status': 201,
            'message': 'Failed',
        }]
    return jsonify({'result': res})


@app.route('/api/order', methods=['PUT'])
def update():
    global cursor, conn
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        _weight = request.args.get('weight')
        _courier = request.args.get('courier')
        _cost = get_cost(str(request.args.get('origin')), str(request.args.get('destination')), str(_weight),
                         _courier)
        _origin = get_place('city', request.args.get('origin'))
        _destination = get_place('city', request.args.get('destination'))
        if _cost != "not found" and _origin != "not found" and _destination != "not found":
            _id = request.args.get('id')
            _name = request.args.get('name')
            _goods = request.args.get('goods')
            _updatedDate = date.today().strftime("%d/%m/%Y")

            sql = """UPDATE orders SET name=%s, origin=%s, destination=%s, goods=%s, 
                            weight=%s, cost=%s, courier=%s, updatedDate=%s WHERE id=%s"""
            data = (_name, _origin, _destination, _goods, str(_weight), _cost, _courier, _updatedDate, _id)
            cursor.execute(sql, data)
            conn.commit()
            res = {
                'message': 'Success',
                'data': {
                    'id': _id,
                    'name': _name,
                    'origin': _origin,
                    'destination': _destination,
                    'goods': _goods,
                    'cost': _cost,
                    'courier': _courier,
                    'updatedDate': _updatedDate,
                }
            }
        else:
            notfound = []
            if _origin == "not found":
                notfound.append("Origin")
            if _destination == "not found":
                notfound.append("Destination")
            if _cost == "not found" and _origin != "not found" and _destination != "not found":
                notfound.append("Courier")
            res = {
                'message': 'Data Tidak Ditemukan, Periksa Kembali Parameter',
                'null': notfound
            }
    except Exception as e:
        return e
    finally:
        cursor.close()
        conn.close()
    return jsonify({'result': res})


@app.route('/api/order', methods=['DELETE'])
def delete():
    global cursor, conn
    try:
        sql = "DELETE FROM orders WHERE id=%s"
        data = (request.args.get('id'))
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()
        res = [{
            'status': 200,
            'message': "Success Delete"
        }]
        return jsonify(res)
    except Exception as e:
        return e
    finally:
        cursor.close()
        conn.close()


@app.route('/api/cost', methods=['POST'])
def get():
    try:
        conn = http.client.HTTPSConnection("api.rajaongkir.com")


        payload = "origin=" + request.args.get('origin') + \
                  "&destination=" + request.args.get('destination') + \
                  "&weight=" + request.args.get('weight') + \
                  "&courier=" + request.args.get('courier')

        headers = {
            'key': "8673346f00df697bd0b951de5f847598",
            'content-type': "application/x-www-form-urlencoded"
        }

        conn.request("POST", "/starter/cost", payload, headers)

        res = conn.getresponse()
        data = res.read()
        return json.loads(data)['rajaongkir']
    except Exception as e:
        res = {
            'message': "Data tidak ditemukan, periksa kembali parameter",
            'status': 404
        }
        return jsonify(res)


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp


@app.errorhandler(405)
def not_found(error=None):
    message = {
        'status': 405,
        'message': 'Method ' + request.method + ' is not allowed',
    }
    resp = jsonify(message)
    resp.status_code = 405

    return resp


if __name__ == "__main__":
    app.run(threaded=True, host='0.0.0.0', port=4040)
