from flask import Flask, jsonify, request
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb

app = Flask(__name__)


def dbconnect():
    '''config = {
        'user': 'admin',
        'password': 'CP2A7.m+cc?3k!$',
        'host': 'database-1.c2iykoijq5qp.us-east-2.rds.amazonaws.com',
        'database': 'mydatabase',
        'raise_on_warnings': True
        }'''

    db = pymysql.connect(host="database-1.c2iykoijq5qp.us-east-2.rds.amazonaws.com", user="admin", password="CP2A7.m+cc?3k!$", database="mydatabase")
    cursor = db.cursor()
    return cursor

@app.route('/', methods=['GET', 'POST'])
def getHourlyData():
    return "Hello World!"

@app.route('/get-hourly-data/', methods=['GET'])
def get_hourly_data():
    cursor = dbconnect()
    cursor.execute("SELECT * FROM energy limit 2")
    result = cursor.fetchall()
    return jsonify(result)

    
@app.route('/get-yearly-data/')
def get_yearly_data():
    cursor = dbconnect()
    cursor.execute("SELECT SUM(Market_Demand) as demand, YEAR(Date) FROM energy GROUP BY YEAR(Date)")
    result = cursor.fetchall()
    return jsonify(result)
    
@app.route('/get-monthly-data/')
def get_monthly_data():
	return 'This is monthly data'  
    
    
@pytest.fixture
def client(app):
    return app.test_client()

def test_get_hourly_data(client):
    response = client.get('/get-hourly-data/')
    assert response.status_code == 200
    # Add additional assertions for response data if needed

def test_get_yearly_data(client):
    response = client.get('/get-yearly-data/')
    assert response.status_code == 200
    # Add additional assertions for response data if needed

def test_get_monthly_data(client):
    response = client.get('/get-monthly-data/')
    assert response.status_code == 200
    # Add additional assertions for response data if needed



if __name__ == '__main__':
    app.run()