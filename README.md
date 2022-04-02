# Django-Channels で Chat アプリを作成

- ASGI に触れてみたい。
- 環境変数の扱いについての学習
- ディレクトリ構成の模索
- AWS EC2 でデプロイしてみる

## 1. pipenv で仮想環境構築<hr>

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

## 2. django-environ で環境変数管理へ<hr>

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
