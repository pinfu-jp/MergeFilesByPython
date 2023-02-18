import sys
from cx_Freeze import setup, Executable


# ビルドに含めるパッケージとモジュールを指定
packages = ['module']
includes = []
excludes = []

# 実行ファイルの設定
exe = Executable(
    script='main.py',  # 実行ファイルとなるスクリプト
    targetName='ParseLogs.exe',  # 出力ファイル名
    base=None  # コンソールアプリケーションとしてビルド
)

# セットアップ
setup(
    name='ParseLogs',
    version='0.1',
    description='Parse some log files',
    options={
        'build_exe': {
            'packages': packages,
            'includes': includes,
            'excludes': excludes,
            'include_files': [],
            'optimize': 0,
            'include_msvcr': True,
        }
    },
    executables=[exe]
)

