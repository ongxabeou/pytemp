from abc import abstractmethod

from socketIO_client import SocketIO, LoggingNamespace


class ROOM:
    EVENT = 'event'


class SmpClient:
    def __init__(self):
        self.name = 'smp'
        self.port = 0
        self.host = ''
        self.rooms = []
        self.io = None
        self.secret_key = None
        self.logger = None

    def set_logger(self, logger):
        self.logger = logger

    def set_config(self, host, port, secret_key):
        self.host = host
        self.port = port
        self.secret_key = secret_key

    def connect(self):
        if self.io is None:
            socket_io = SocketIO(host=self.host, port=self.port, namespace=LoggingNamespace, path='/chat')
            socket_io.on('connect', self.on_connect, path='/chat')
            socket_io.on('disconnect', self.on_disconnect, path='/chat')
            socket_io.on('reconnect', self.on_reconnect, path='/chat')
            socket_io.on('status', self.on_status, path='/chat')
            socket_io.on('message', self.on_message, path='/chat')
            socket_io.connect(path='/chat')
            self.io = socket_io

    def disconnect(self):
        self.io.disconnect()
        temp = self.io
        self.io = None
        del temp

    def on_connect(self):
        print(self.name, 'connected')

    def on_status(self, data):
        print(self.name, 'on_status:', data)

    @abstractmethod
    def on_message(self, data):
        print(self.name, 'on_message:', data)

    def on_disconnect(self):
        print(self.name, 'disconnected')

    def on_reconnect(self):
        for room in self.rooms:
            self._emit('joined', {'key': self.secret_key, 'name': self.name, 'room': room})
        print(self.name, 'reconnected')

    def _emit(self, event, data):
        self.io.emit(event, data, path='/chat')

    def joined_room(self, room):
        self.rooms.append(room)
        self._emit('joined', {'key': self.secret_key, 'name': self.name, 'room': room})

    def left_room(self, room):
        self.rooms.remove(room)
        self._emit('left', {'name': self.name, 'room': room})

    def send_event(self, data):
        self.send(room='event', data=data, msg_type='text')

    def send_cmd(self, data):
        self.send(room='cmd', data=data, msg_type='json')

    def send(self, room, data, msg_type='text'):
        if room not in self.rooms:
            self.joined_room(room)
        msg = {'key': self.secret_key, 'name': self.name, 'room': room, 'data': data}
        print('sent message:', msg)
        self._emit(msg_type, msg)

    def wait_one(self):
        self.io.wait(seconds=1)

    def wait(self, seconds=None):
        if seconds is None:
            self.io.wait()
        else:
            self.io.wait(seconds=seconds)


# ------------------Test------------------------
if __name__ == '__main__':
    client = SmpClient()
    client.set_config(secret_key='uiliauiunviwubwieuvn', host='localhost', port=5000)
    client.connect()
    client.joined_room('event')
    client.send_event({'subject': 'xin chao ban', 'body': 'chúc bạn may mắn lần sau'})
    client.wait_one()
