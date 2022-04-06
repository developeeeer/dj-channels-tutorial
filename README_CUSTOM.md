# Chatアプリチュートリアルから一部いじっていきます

## 開発環境のMigrations, DBFileをリセット
migrationsフォルダ、db.sqlite3をリセットして管理者ユーザーを全てリセットする

```python 
# python allreset.pyで以下の処理を実行
# 詳細についてはファイル参照

if __name__ == "__main__":
    delete_sqlite_file()
    delete_migration_folders()
    python_manage_makemigrations()
    python_manage_migrate()
    python_manage_createsuperuser()
    python_manage_runserver()


```