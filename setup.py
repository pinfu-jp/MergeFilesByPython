import sys
import os
from cx_Freeze import setup, Executable


# ビルドに含めるパッケージとモジュールを指定
packages = ['module']
includes = []
excludes = []

# 実行ファイルの設定
exe = Executable(
    script='main.py',  # 実行ファイルとなるスクリプト
    targetName='MergeLogs.exe',  # 出力ファイル名
    base=None  # コンソールアプリケーションとしてビルド
)

# セットアップ実行で exe作成
setup(
    name='MergeLogs',
    version='0.1',
    description='Parse logs And Merge to csv file',
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
    executables=[exe],
    copyright=(
        "Copyright (c) 2023 "
        "Pinfu-jp. "
        "All rights reserved."
    ),)


# 作成されたexe等の出力先を開く
if sys.platform == 'win32':
    out_dir = os.path.join(".", "build", "exe.win-amd64-3.11")
    os.system('explorer "{}"'.format(os.path.abspath(out_dir)))