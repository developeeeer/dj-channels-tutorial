# Django-Channels で Chat アプリを作成

### チュートリアルに沿って開発を進めますが一部ピックアップ・その他オリジナル部分を記事に残します

- ASGI に触れてみたい。
- 環境変数の扱いについての学習
- ディレクトリ構成の模索
- AWS EC2 でデプロイしてみる

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
