from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Container Lab</title></head>
    <body>
    <h1>Flask Container Lab</h1>
    <p>Name: Divyanshu Gaur</p>
    <p>SAP: 500121752</p>
    <p>Batch: Batch 1</p>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
