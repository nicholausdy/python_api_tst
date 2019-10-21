from http.server import BaseHTTPRequestHandler, HTTPServer
import mysql.connector
import requests
import json
import http.client
from datetime import date
import random
from urllib.parse import urlparse, parse_qs

PORT_NUMBER = 8080
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database="test"
)


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


class myHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global d
        try:
            cursor = mydb.cursor()
            cursor.execute("SELECT * FROM orders")
            res = cursor.fetchall()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            result = []
            for row in res:
                data = {
                    'id': row[0],
                    'name': row[1],
                    'origin': row[2],
                    'destination': row[3],
                    'goods': row[4],
                    'weight': row[5],
                    'cost': row[6],
                    'courier': row[7],
                    'status': row[8]
                }
                result.append(data)
            data = json.dumps(result)
            self.wfile.write(bytes(data.encode('utf-8')))
            return
        except Exception as e:
            return e

    def do_POST(self):
        try:
            parsed_url = urlparse(self.path).query
            query = parse_qs(parsed_url)
            data = json.dumps(query)
            cursor = mydb.cursor()
            _courier = data.split('"courier": ["')[1].split('"]')[0]
            _weight = data.split('"weight": ["')[1].split('"]')[0]
            _cost = get_cost(str(data.split('"origin": ["')[1].split('"]')[0]), str(data.split('"destination": ["')[1].split('"]')[0]), str(_weight),
                             _courier)
            _origin = get_place('city', data.split('"origin": ["')[1].split('"]')[0])
            _destination = get_place('city', data.split('"destination": ["')[1].split('"]')[0])
            if _cost != "not found" and _origin != "not found" and _destination != "not found":
                _id = random_id()
                _name = data.split('"name": ["')[1].split('"]')[0]
                _goods = data.split('"goods": ["')[1].split('"]')[0]
                _status = "packing"
                _date = date.today().strftime("%d/%m %Y")
                _updatedDate = date.today().strftime("%d/%m/%Y")

                sql = """INSERT INTO orders(id, name, origin, destination, goods, weight, cost, courier, status,
                date, updatedDate) VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                data = (_id, _name, _origin, _destination, _goods, str(_weight), _cost, _courier, _status, _date,
                        _updatedDate)
                cursor.execute(sql, data)
                mydb.commit()
                res = {
                    'message': 'Success Add Data',
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
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(json.dumps(res).encode('utf-8')))
            return
        except Exception as e:
            return e

    def do_PUT(self):
        try:
            parsed_url = urlparse(self.path).query
            query = parse_qs(parsed_url)
            data = json.dumps(query)
            cursor = mydb.cursor()
            _courier = data.split('"courier": ["')[1].split('"]')[0]
            _weight = data.split('"weight": ["')[1].split('"]')[0]
            _cost = get_cost(str(data.split('"origin": ["')[1].split('"]')[0]), str(data.split('"destination": ["')[1].split('"]')[0]), str(_weight),
                             _courier)
            _origin = get_place('city', data.split('"origin": ["')[1].split('"]')[0])
            _destination = get_place('city', data.split('"destination": ["')[1].split('"]')[0])
            if _cost != "not found" and _origin != "not found" and _destination != "not found":
                _id = data.split('"id": ["')[1].split('"]')[0]
                _name = data.split('"name": ["')[1].split('"]')[0]
                _goods = data.split('"goods": ["')[1].split('"]')[0]
                _status = "packing"
                _date = date.today().strftime("%d/%m %Y")
                _updatedDate = date.today().strftime("%d/%m/%Y")

                sql = """UPDATE orders SET name=%s, origin=%s, destination=%s, goods=%s, 
                                            weight=%s, cost=%s, courier=%s, updatedDate=%s WHERE id=%s"""
                data = (_name, _origin, _destination, _goods, str(_weight), _cost, _courier, _updatedDate, _id)
                cursor.execute(sql, data)
                mydb.commit()
                res = {
                    'message': 'Success Update Data',
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
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(json.dumps(res).encode('utf-8')))
            return
        except Exception as e:
            return e


    def do_DELETE(self):
        # self.send_response(200)
        # self.send_header('Content-type', 'application/json')
        # self.end_headers()
        # self.wfile.write(bytes("HAI".encode('utf-8')))
        try:
            parsed_url = urlparse(self.path).query
            query = parse_qs(parsed_url)
            data = json.dumps(query)
            cursor = mydb.cursor()
            _id = data.split('"id": ["')[1].split('"]')[0]
            sql = "DELETE FROM orders WHERE id="+_id
            cursor.execute(sql)
            mydb.commit()
            res = {
                'status': 200,
                'message': "Berhasil Menghapus Data dengan ID "+ _id
            }
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(json.dumps(res).encode('utf-8')))
            return
        except Exception as e:
            return e


port = 4040
with HTTPServer(("",port), myHandler) as httpd:
    print("serving at port ",port)
    httpd.serve_forever()
    mydb.close()
