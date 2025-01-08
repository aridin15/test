from flask import Flask

app = Flask(__name__)

@app.route('/api/flask')
def hello_world():
    return 'Hello, World from Flasky!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)