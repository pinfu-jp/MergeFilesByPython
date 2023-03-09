import sys
import os
import shutil
import zipfile

from cx_Freeze import setup, Executable

APP_NAME = "MergeLogs"

# ビルドに含めるパッケージとモジュールを指定
packages = ['module']
includes = []
excludes = []

# 実行ファイルの設定
exe = Executable(
    script='main.py',  # 実行ファイルとなるスクリプト
    targetName=(APP_NAME + '.exe'),  # 出力ファイル名
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

# 設定ファイルをコピーしてくる
json_name = APP_NAME + ".json"
src_path = os.path.join(".", json_name)
dest_path = os.path.join(".", "build", "exe.win-amd64-3.11", json_name)
if os.path.exists(dest_path):
    os.remove(dest_path)
shutil.copy(src_path, dest_path)

dest_path = os.path.join(".", "build", "exe.win-amd64-3.11")

# 作成されたexe等の出力先を開く
if sys.platform == 'win32':
    os.system('explorer "{}"'.format(os.path.abspath(dest_path)))

# # ZIP化 
# zip_path = os.path.join(".", "package", APP_NAME + ".zip")
# if os.path.exists(zip_path):
#     os.remove(zip_path)
# with zipfile.ZipFile(zip_path, mode='w', compression=zipfile.ZIP_DEFLATED) as zipf:
#     zipf.write(dest_path)
