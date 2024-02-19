import json
from flask import Flask
from markupsafe import escape
from ping3 import ping

app = Flask(__name__)


@app.route('/checkip/<name>')
def checkip(name):
    res = []
    rangeCount = 30
    for i in range(rangeCount):
        ms = ping(escape(name), unit='ms', timeout=1)
        res.append(ms)
    isblock = False
    if res.count(None) / rangeCount > 0.9:
        isblock = True
    resp = {
        "isblock": isblock,
        "source": str(res.count(None)) + "/" + str(rangeCount)
    }

    return json.dumps(resp)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
# gunicorn app:app -c gunicorn.conf.py
