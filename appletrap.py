from datetime import datetime, timedelta
from flask import Flask, request, redirect, render_template, url_for
from redis import Redis
import config


redis = Redis()
app = Flask(__name__)


@app.route('/')
@app.route('/hotspot-detect.html')
def default():
    if request.headers.get('User-Agent')[-5:] == 'wispr':
        dt_bytes = redis.get(request.remote_addr)
        if dt_bytes is not None:
            tdiff = datetime.now() - datetime.fromtimestamp(float(dt_bytes))

            if tdiff < timedelta(seconds=config.APPLETRAP_TIMEOUT):
                redis.delete(request.remote_addr)
                return render_template('cna_trap/success.html')

            else:
                redis.set(request.remote_addr, datetime.now().timestamp())
                return render_template('cna_trap/empty.html')

        else:
            redis.set(request.remote_addr, datetime.now().timestamp())
            return render_template('cna_trap/empty.html')
    else:
        return redirect(url_for('trap'))


@app.route('/hotspot-1.html')
def trap():
    return render_template('cna_trap/trap.html')
