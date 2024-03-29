# MergeFilesByPython

* モジュール別に出力されたログファイル群を、１本のxlsxファイルにマージします
* １本にまとめることで、どのモジュールで問題が起きていたのか時系列で原因調査できるようになります
* 抽出対象日以外に、対象日前の数日分のログをそれぞれマージ可能です

出力イメージ

![xlsxサンプル](./doc/xlsx_result.png)


<br>

## 機能概要

### 1. タイムスタンプ文字列が入った様々なログファイルをマージ可能

* 年月日、時刻文字列のフォーマットは様々あります
* 代表的なケースを想定しつつ、様々なフォーマットに対応しています


#### 1-1.ファイル名にタイムスタンプがない場合

* 様々な年月日、時刻文字列に対応

```(log)
2023-02-10 14:51:12 フォーマット：YYYY-MM-DD hh:mm:dd を解析可能 
2023/02/11 14:51:12 フォーマット：YYYY/MM/DD hh:mm:dd を解析可能 
2023.02.12 14:51:12 フォーマット：YYYY.MM.DD hh:mm:dd を解析可能 
23-02-13 14:51:12 フォーマット：西暦下２桁YY-MM-DD hh:mm:dd を解析可能 
23/02/14 14:51:12 フォーマット：西暦下２桁YY/MM/DD hh:mm:dd を解析可能 
23.02.15 14:51:12 フォーマット：西暦下２桁YY.MM.DD hh:mm:dd を解析可能 
2023-02-10 14:51:12.100 フォーマット：YYYY-MM-DD hh:mm:dd.000 ミリ秒 を解析可能 
2023-02-10 14:51:12-100 フォーマット：YYYY-MM-DD hh:mm:dd-000 ハイフンのミリ秒 を解析可能 
2023-02-10 14:51:12-1 フォーマット：YYYY-MM-DD hh:mm:dd-0   上1,2桁のミリ秒 を解析可能 
2023-2-1 1:5:1 フォーマット：YYYY-M-D h:m:d １桁日時 を解析可能 
```

* レコードに日付がないケースは、ファイルの更新日付とタイムスタンプを合成

```
// ファイル名にタイムスタンプはなく、レコードには時刻しかないケース
14:51:12.100 フォーマット：YYYY-M-D h:m:d １桁日時 を解析可能
// この場合、ファイルのプロパティから更新日付を取得してタイムスタンプとします
```

#### ファイル名に日付タイムスタンプが付いている場合

  * xxxxx_20230222.log などの８桁西暦年月日に対応

```(log)
14:51:12 フォーマット：hh:mm:dd を解析可能 
1:5:1 フォーマット：h:m:d １桁時刻 を解析可能 
```

  * xxxxx_230222.log などの６桁西暦年月日に対応

```(log)
14:51:12 フォーマット：hh:mm:dd を解析可能 
1:5:1 フォーマット：h:m:d １桁時刻 を解析可能 
```

> ファイル名に日付がある場合、ログ内のタイムスタンプは時刻のみでることを前提に解析します

  * xxxxx_202302.log などの6桁西暦年月に対応
  
```(log)
// レコードには日と、時刻が出力されているので、ファイル名の年月とタイムスタンプを生成する
22 14:51:12 フォーマット：hh:mm:dd を解析可能 
22 1:5:1 フォーマット：h:m:d １桁時刻 を解析可能 
```

<br>

### 2. 大量のログファイルをマージ可能

* 設定ファイルで指定したフォルダ下のすべての .log, .txt ファイルをマージ対象とします
  * サブフォルダ下にあるファイルもマージ対象です
* マルチスレッドで平行解析するので処理時間は短縮されています
* テスト例
  * 1,000行 x 10ファイル の解析に 5秒
  * 3,000行 x 100ファイル の解析に 147秒
  * 評価環境：Windows11 Pro / Intel(R) Core(TM) i7-1165G7 @ 2.80GHz / 16GB


  > パフォーマンス、品質評価は [テストコード](https://github.com/pinfu-jp/MergeFilesByPython/blob/main/Test_MergeLogs.py) で可能

<br>

### 3. マージ結果は XLSX ファイル形式

* Excelでさらに解析できるようにしています
  * 中間データであるCSVファイルも出力しています

```(CSV)
タイムスタンプ,ファイル名,キーワード,ログ内容
2023-02-23 09:11:12.001,test6_230222.log,,[info] 画面表示開始
2023-02-23 09:11:12.123,test6_230222.log,err,[err] 例外が発生
```
#### フォーマット

|列番号|項目|例|
|-|-|-|
|1|タイムスタンプ<br>YYYY-MM-DD hh:mm:dd.000 形式|2023-02-23 09:11:12.001|
|2|抽出元のログファイル<br>指定のルートフォルダからの相対パスで指定|test6_230222.log<br>sub_folder\test3.log|
|3|抽出キーワード<br>設定ファイルで指定したキーワードに該当する場合のみ出力される|err/exception/エラー/warn/警告|
|4|ログ本文<br>タイムスタンプ文字列を除外した文字列<br>※ 最大文字数は設定ファイルに従う|[info] 画面表示開始|

<br>

### 4.設定ファイルでカスタマイズ可能

* マージ対象や、出力先フォルダ、ファイル名称を指定できます
* 設定はJSON形式ファイルで一括指定します

```(json)
{
    "解析対象ログフォルダ": ".\\log",
    "解析結果出力先フォルダ": ".\\csv",
    "出力ファイル名":"merged_log",
    "解析対象日": 20230222,
    "遡る日数": 5,
    "抽出キーワード（正規表現）":"err|except|エラー|warn|警告",
    "1行当たりの最大出力文字数":256,
    "タイムスタンプ抽出最大文字数":24
}
```
#### JSONフォーマット

* <u>文字コード UTF-8 で入力します（Shift-JIS不可）</u>

|項目名|説明|未指定時の自動設定値|
|-|-|-|
|解析対象ログフォルダ|ログファイルを入れているフォルダパス<br>サブフォルダも解析対象となります<br>相対パスで指定する場合、実行プログラムからの相対パスを指定する必要があります|.\\log|
|解析結果出力先フォルダ|マージ結果を出力するフォルダパス<br>日単位でCSVファイル化するのでフォルダ指定となります<br>フォルダが無い場合は自動作成します|.\\csv|
|出力ファイル名|CSVファイルの名称を指定|"merged_log"|
|解析対象日|解析する日付<br>西暦年月日８桁数値で指定|システム時刻の日付|
|遡る日数|解析対象日以前で集める日数<br>トラブルの原因で遡る必要がある場合があるので設定があります|5|
|抽出キーワード（正規表現）|重要なキーワードを含むログを強調したい場合に指定<br>正規表現で指定してください|"err\|except\|エラー\|warn\|警告"|
|1行当たりの最大出力文字数|マージ後のログ文字列の長さを制限<br>概要として確認したい場合に文字数を減らせます|256|
|タイムスタンプ抽出最大文字数|タイムスタンプ文字列は各行の先頭にあることを前提にしています<br>先頭文字から何文字までを抽出対象とするか指定が必要です<br>タイムスタンプ文字列が後方にある場合は、文字数を長めに指定してください<br>指定文字数が長いほど解析時間が長くなることに注意してください|32|

> 項目名は変更不可


<br>


## 開発環境

* VScode, sandbox を推奨
* 参照ライブラリ
  * 以下をインストールしてください
  ```
  Package                   Version
  ------------------------- ---------
  altgraph                  0.17.3
  comtypes                  1.1.14
  cx-Freeze                 6.14.1
  cx-Logging                3.1.0
  et-xmlfile                1.1.0
  future                    0.18.3
  lief                      0.12.3
  openpyxl                  3.1.1
  pefile                    2022.5.30
  pip                       23.0
  pyinstaller-hooks-contrib 2022.15
  pywin32                   305
  pywin32-ctypes            0.2.0
  pywinauto                 0.6.8
  setuptools                65.5.0
  six                       1.16.0
  wheel                     0.38.4
  ```

<br>

## デバッグ方法

* ユニットテストでデバッグします

* Test_MergeLogs.py を実行します

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