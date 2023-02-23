# MergeFilesByPython

このプログラムは、指定されたフォルダ内の全てのログファイルからタイムスタンプとログ文字列を抽出し、csvファイルに出力します



## ビルド方法

* cx_Freeze を使ってビルドします
  
* 以下のコマンドを実行することでexeが作成されます
```
python .\setup.py build
```

<br>

## 実行方法

### マウスクリックで実行

* .\build\exe.win-amd64-3.11\ParseLogs.exe をダブルクリック
* JSONファイル選択画面で ParseLogs.json を選択

### コマンドラインで実行

```
.\build\exe.win-amd64-3.11\ParseLogs.exe .\ParseLogs.json
```

<br>

## エラー発生時の調査方法

* ParseLogs.log にログが出力されるので、err などが残っていないかを確認してください