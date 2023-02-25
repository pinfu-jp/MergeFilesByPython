# MergeFilesByPython

* このプログラムは、モジュール別に出力されたログファイル群を１本のCSVファイルにマージします
* １本にまとめることで、どのモジュールで問題が起きているのか原因調査できるようにします
* 抽出対象日と、対象日から翻って数日のログをそれぞれ出力できます
* 出力はCSV形式ファイルです


<br>

## 機能概要

（準備中）

<br>

## ビルド方法

* Windows向けに exe 化可能です

* cx_Freeze を使ってビルドします
  
* 以下のコマンドを実行することでexeが作成されます
```
python .\setup.py build
```

<br>

## 実行方法

### pythonコマンドで実行

```
python .\main.py .\MergeLogs.json
```


### ビルドした exe を実行

* .\build\exe.win-amd64-3.11\MergeLogs.exe をダブルクリック
* JSONファイル選択画面で MergeLogs.json を選択

#### コマンドラインで exe 実行

```
.\build\exe.win-amd64-3.11\MergeLogs.exe .\MergeLogs.json
```


<br>

## エラー発生時の調査方法

* MergeLogs.log にログが出力されるので、err などが残っていないかを確認してください