from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/datetime', methods=['GET'])
def get_time():
    now = datetime.now()
    format = now.strftime("%d/%m/%Y %H:%M:%S")
    return jsonify({'datetime':format})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)