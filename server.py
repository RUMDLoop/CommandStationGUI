#!/usr/bin/env python

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on available packages.
async_mode = None

if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

    if async_mode is None:
        try:
            from gevent import monkey
            async_mode = 'gevent'
        except ImportError:
            pass

    if async_mode is None:
        async_mode = 'threading'

    print('async_mode is ' + async_mode)

# monkey patching is necessary because this application uses a background
# thread
if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()

import time
from threading import Thread
from flask import Flask, render_template, session, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from pymongo import MongoClient
import datetime
import uuid
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

client = MongoClient()

db = client.rumdloop_db

pods = db.pods
mancodes = db.mancodes


second = 1
minute = 60 * second
hour = 60 * minute
day = 24 * hour

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        time.sleep(10)
        count += 1
        socketio.emit('my response',
                      {'data': 'Server generated event', 'count': count},
                      namespace='/test')

@app.route('/<client>')
def index(client=None):
    if client == 'external':
        return render_template('index.html')
    elif client == 'internal':
        ###TODO return a key/token for auth access
        return jsonify({'success' : True})
    else:
        return jsonify({'success' : False})

"""

Input: {'man_code':'shrey'}
Output:
        SUCCESS: {'status':'ok','pod_id':'','timestamp':''}
        FAIL: {'status':'error','reason':'','timestamp':''}
"""
@app.route('/getPodID',methods=['POST'])
def create_pod():
    man_code = request.form['man_code']
    if man_code == None:
        response = {'status' : 'error','reason' : 'invalid manafacturer code','timestamp' : datetime.datetime.utcnow()}
    else:
        search = mancodes.find_one({'man_code' : man_code})
        if search == None:
            response = {'status' : 'error','reason' : 'manafacturer code does not exist','timestamp' : datetime.datetime.utcnow()}
        else:
            uuid_code = uuid.uuid4()
            uuid_str = str(uuid_code)
            query = pods.find_one({'pod_id' : uuid_str})
            while query != None:
                uuid_code = uuid.uuid4()
                uuid_str = str(uuid_code)
                query = pods.find_one({'pod_id' : uuid_str})
            pod = {'pod_id' : uuid_str, 'model' : 'Prometheus', 'operational' : True, 'createdAt' : datetime.datetime.utcnow(), 'updatedAt' : datetime.datetime.utcnow()}
            post_id = pods.insert_one(pod)
            if post_id != None:
                response = {'status' : 'ok', 'pod_id' : uuid_str,'timestamp' : datetime.datetime.utcnow()}
            else:
                response = {'status' : 'error', 'reason' : 'database upload failed', 'timestamp' : datetime.datetime.utcnow()}
    return jsonify(response)



def get_auth_token(data):
    is_pod = data['is_pod']
    if is_pod:
        pod_id = data['pod_id']
        search = pods.find_one({'pod_id' : pod_id})
        if search != None:
            s = Serializer('secret_key',expires_in = 10 * day)
            return s.dumps({'id' : pod_id})
        else:
            return None
    else:
        client_id = data['client_id']

@staticmethod
def verify_auth_token(token):
    s = Serializer('secret_key')
    try:
        data = s.loads(token)
    except SignatureExpired:
        return 1
    except BadSignature:
        return 2
    return 0

"""
Input: {'is_pod':'pod_id':'','client_id':''}
Output:
        SUCCESS: {'status':'ok','pod_id':'',secret_token:'','timestamp':''}
        FAIL: {'status' : 'error','reason':'','timestamp':''}
"""
@app.route('/auth', methods=['POST'])
def authenticate():
    is_pod = request.form['is_pod']
    if is_pod:
        x_id = request.form['pod_id']
    else:
        x_id = request.form['client_id']
    token = get_auth_token({'is_pod' : is_pod, 'pod_id' : x_id if is_pod else None, 'client_id' : x_id if not is_pod else None})
    if token != None:
        res = {'status':'ok','pod_id' : x_id,'secret_token' : token, 'timestamp' : datetime.datetime.utcnow()}
    else:
        res = {'status':'error','reason' :'id not found', 'timestamp' : datetime.datetime.utcnow()}
    return jsonify(res)



"""

pod->client

"""
@socketio.on('data_send', namespace='/test')
def test_message(message):
    token = message['token']
    res_code = verify_auth_token(token)
    if res_code == 0:
        pod_id = message['pod_id']
        search = pods.find_one({'pod_id' : pod_id})
        if search != None:
            emit('data_receive_' + pod_id, {'data' : message['data']})

"""

client->pod

"""
@socketio.on('cmd_send', namespace='/test')
def test_message(message):
    token = message['token']
    res_code = verify_auth_token(token)
    if res_code == 0:
        pod_id = message['pod_id']
        search = pods.find_one({'pod_id' : pod_id})
        if search != None:
            emit('cmd_receive_' + pod_id, {'data' : message['data']})


### TODO: Figure out what's the difference between this and just a regular emit to a channel
@socketio.on('my broadcast event', namespace='/test')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@socketio.on('stop', namespace='/test')
def stop(message):
    token = message['token']
    cmd = message['data']
    res_code = verify_auth_token(token)
    if res_code == 0 and cmd == 'pod_stop_cmd':
        pod_id = message['pod_id']
        search = pods.find_one({'pod_id' : pod_id})
        if search != None:
            emit('stop_' + pod_id, {'data' : 'pod_stop_cmd'})





@socketio.on('disconnect request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True)
