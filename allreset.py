import os
import shutil

SUPERUSER_EMAIL = "test@test.com"
SUPERUSER_PASS = "defaultPassword"
SQLITE_FILE_NAME = "db.sqlite3"
APPLICATION_LIST = [
    "accounts"
]


def delete_sqlite_file():
    """データベースファイルを削除"""
    if os.path.isfile(SQLITE_FILE_NAME):
        os.remove(SQLITE_FILE_NAME)
        print(f"{SQLITE_FILE_NAME}を削除しました")


def delete_migration_folders():
    """マイグレーションフォルダの削除"""
    migration_folder_name = "migrations"
    for application in APPLICATION_LIST:
        migrations = os.path.join(application, migration_folder_name)
        if os.path.isdir(migrations):
            shutil.rmtree(migrations)
            print(f"{migrations}を削除しました")


def python_manage_makemigrations():
    """python manage.py makemigrations を実行"""
    for application in APPLICATION_LIST:
        command = f"python manage.py makemigrations {application}"
        os.system(command)
        print(command)


def python_manage_migrate():
    """python manage.py migrateを実行"""
    os.system("python manage.py migrate")


def python_manage_createsuperuser():
    """スーパーユーザーの作成"""
    print("=========")
    print(f"Email: {SUPERUSER_EMAIL}")
    print(f"PassWord: {SUPERUSER_PASS}")
    print("=========")
    os.system("python manage.py createsuperuser")


def python_manage_runserver():
    """python manage.py rusnerverを実行"""
    os.system("python manage.py runserver")


if __name__ == "__main__":
    delete_sqlite_file()
    delete_migration_folders()
    python_manage_makemigrations()
    python_manage_migrate()
    python_manage_createsuperuser()
    python_manage_runserver()
