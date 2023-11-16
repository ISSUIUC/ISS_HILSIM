import socketio

sio = socketio.Client(logger=True, engineio_logger=True)

@sio.event
def connect():
    print('connection established')

@sio.event
def my_message(data):
    print('message received with ', data)
    sio.emit('my response', {'response': 'my response'})


@sio.event
def disconnect():
    print('disconnected from server')

@sio.event
def connect_error(data):
    print("The connection failed!")
    print(data)

sio.connect('http://localhost/', socketio_path="/api/dscomm/ws/socket.io")
sio.wait()