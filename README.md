# Django-Channels で Chat アプリを作成

### チュートリアルに沿って開発を進めますが一部ピックアップ・その他オリジナル部分を記事に残します

## pipenv で仮想環境構築<hr>

プロジェクトディレクトリを作成

```terminal
mkdir project
```

pipenv 環境構築

```terminal
1. バージョン指定無し
pipenv install

2. バージョン指定有り
pipenv --python 3.9.9
```

package インストール

```terminal
pipenv shell
pip install Django==3.2.12

# 仮想環境を非アクティブ化にする
exit
```

## django-environ で環境変数管理へ<hr>

django-environ のインストール

```terminal
pip install django-environ
```

.env ファイルを作成

```terminal
touch .env
```

.env ファイルに環境変数の追加

```.env
DEBUG=0
SECRET_KEY="KEY"
ALLOWED_HOSTS="*"
```

settings.py の編集

```settings.py
# インポートの追加
import environ
import os
```

環境変数用のファイルとマシン環境変数の使い分けを記述

```settings.py
env = environ.Env()
READ_ENV_FILE = env.bool('DJANGO_READ_ENV_FILE', default=0)

if READ_ENV_FILE:
    environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
```

環境変数の使用方法

```settings.py
# env(環境変数名)で使用する
SECRET_KEY = env('SECRET_KEY')
```

## Template の管理フォルダをルートに変更<hr>

settings.py の TEMPLATES.DIRS を編集  
application/templates の参照から project/templates を参照するように変更

```settings.py
TEMPLATES = [
    {
        ...
        + 'DIRS': [os.path.join(BASE_DIR, 'templates')],
        ...
    },
]
```

## Channels ライブラリの統合<hr>

channels ライブラリのインストール

```terminal
pip install channels
```

settings.py の編集

```terminal
# INSTALLED_APPSに追加
INSTALLED_APPS = [
    'channels',
    ...
]

# settings.pyの下部に追加
ASGI_APPLICATION = "config.asgi.application"
```

config/asgi.py を以下に書き換えて DjangoASGI アプリケーションを Wrap

```asgi.py
import os

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # Just HTTP for now. (We can add other protocols later.)
})
```

これで ASGI サーバーの構築が完了

```terminal
python manage.py runserver

Starting ASGI/Channels version 3.0.4 development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

## チャットサーバーの実装<hr>

room template を追加

```terminal
touch templates/chat/room.html

# 以下を追加
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>Chat Room</title>
</head>
<body>
    <textarea id="chat-log" cols="100" rows="20"></textarea><br>
    <input id="chat-message-input" type="text" size="100"><br>
    <input id="chat-message-submit" type="button" value="Send">
    {{ room_name|json_script:"room-name" }}
    <script>
        const roomName = JSON.parse(document.getElementById('room-name').textContent);

        const chatSocket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/chat/'
            + roomName
            + '/'
        );

        chatSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            document.querySelector('#chat-log').value += (data.message + '\n');
        };

        chatSocket.onclose = function(e) {
            console.error('Chat socket closed unexpectedly');
        };

        document.querySelector('#chat-message-input').focus();
        document.querySelector('#chat-message-input').onkeyup = function(e) {
            if (e.keyCode === 13) {  // enter, return
                document.querySelector('#chat-message-submit').click();
            }
        };

        document.querySelector('#chat-message-submit').onclick = function(e) {
            const messageInputDom = document.querySelector('#chat-message-input');
            const message = messageInputDom.value;
            chatSocket.send(JSON.stringify({
                'message': message
            }));
            messageInputDom.value = '';
        };
    </script>
</body>
</html>
```

room view を chat/views.py へ追加

```views.py
def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name': room_name
    })
```

room view のルートを chat/urls.py へ追加

```urls.py
urlpatterns = [
    ...
    path('<str:room_name>/', views.room, name='room'),
]
```

Consumer を作成する

Channels が WebSocket 接続を受け入れると、ルートルーティング構成を参照してコンシューマーを検索し、コンシューマーのさまざまな関数を呼び出して接続からのイベントを処理します。

今回は /ws/chat/{ROOM_NAME}/ WebSocket で受信したメッセージを受け取り、同じ WebSocket にエコーバックするパスで WebSocket 接続を受け入れる基本的なコンシューマーを作成します。

Memo

In particular for large sites it will be possible to configure a production-grade HTTP server like nginx to route requests based on path to either (1) a production-grade WSGI server like Gunicorn+Django for ordinary HTTP requests or (2) a production-grade ASGI server like Daphne+Channels for WebSocket requests.

```
# consumers fileの作成
touch chat/consumers.py

# 以下を書き込む
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
```

コンシューマーへのルートを持つチャットアプリのルーティング構成を作成

```
# routing.py fileの作成
touch routing.py

# 以下を書き込む
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
```

chat.routing モジュールでルートルーティング構成を指定するため asgi.py を編集する  
接続の HTTP パスを調べて、特定のコンシューマーにルーティングします。  
※migrate していない場合は migrate しておく

```
python manage.py migrate
```

```asgi.py
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import chat.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})
```

チャネルレイヤを有効化にする  
チャネル層は一種の通信システム。複数のコンシューマーインスタンスが相互に、および Django の他の部分と通信できるようにする。  
方法は Redis チャネルレイヤを使用する or インメモリチャンネルレイヤを使用する方法がある

1. Redis チャネルレイヤを使用
   複数のチャネルレイヤを構成することが可能だが、ほとんどの場合は default チャネルレイヤのみの使用となるそう。(チュートリアル引用)

```
# Redisをバッキングストアとして使用
docker run -p 6379:6379 -d redis:5

# ChannelsがRedisとのインターフェース方法を認識できるように、channels_redisをインストールする
pip install channels_redis

# チャネルレイヤ構成をsettings.pyへ追加
# hostがlocalhostになっているので本番環境には合わせる必要がある
ASGI_APPLICATION = 'mysite.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

2. インメモリチャンネルレイヤを使用
   Channels には、メモリ内の ChannelsLayer もパッケージ化されている。  
   このレイヤは、テストやローカル開発の目的で使用すること。  
   ※本番環境ではクロスプロセスメッセージングが不可能

```
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
```

Redis との通信確認(直接仮想サーバーを立ち上げて実行しても良い)

```terminal
$ python manage.py shell
>>> import channels.layers
>>> channel_layer = channels.layers.get_channel_layer()
>>> from asgiref.sync import async_to_sync
>>> async_to_sync(channel_layer.send)('test_channel', {'type': 'hello'})
>>> async_to_sync(channel_layer.receive)('test_channel')
{'type': 'hello'}
```

以上でチャットサーバー構築の完了  
python manage.py runserver で起動して複数タブで/chat/{room}/を開いて相互通信できているか確認してください。

## チャットサーバーの非同期化<hr>

ChatConsumer を非同期になるように変更

```
# 以下に置き換え
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
```

## 以上で非同期チャットサーバーの構築が完了

## CUSTOM.md で色々カスタマイズしてみる...
