import json
import time
from flask import Flask, request
from markupsafe import escape
from tcping import Ping
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)





def action(ping):
    try:
        ping.ping(1)
    except Exception as err:
        print(err)

@app.route('/checktcp/<name>')
def checktcp(name):

    rangeCount = 100
    start = time.time()
    ips = escape(name).split(":")
    timeout = 2
    ping = Ping(ips[0], ips[1], timeout)
    all_task = []
    max_workers=32
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for second in range(rangeCount):
            all_task.append(pool.submit(action, ping))

    count = ping.__dict__["_successed"]
    isblock = True
    if count / rangeCount >= 0.1:
        isblock = False
    resp = {
        "isblock": isblock,
        "count": str(count) + "/" + str(rangeCount),
        "conn_times": ping.__dict__["_conn_times"],
        "use_conn_time": sum(ping.__dict__["_conn_times"]) / 1000,
        "source": count / rangeCount,
        "all_time": time.time() - start
    }

    return json.dumps(resp)




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
# gunicorn app:app -c gunicorn.conf.py
