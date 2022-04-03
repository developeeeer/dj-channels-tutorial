import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # ルームグループへの参加
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        # 接続を許可
        self.accept()

    def disconnect(self, close_code):
        # ルームグループから削除
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # WebSocketよりメッセージを受信
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # ルームグループへメッセージを送信
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # ルームグループよりメッセージを受信
    def chat_message(self, event):
        message = event['message']

        # WebSocketへメッセージを送信
        self.send(text_data=json.dumps({
            'message': message
        }))