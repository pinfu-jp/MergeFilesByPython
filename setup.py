from cx_Freeze import setup, Executable

# ビルドオプションを設定
build_exe_options = {
	"packages": [
		"src",
		# "src/parse_logs_to_csv.py",
		# "src/logger.py",
		# "src/messagebox.py",
		# "src/open_csv.py",
		# "src/select_folder.py"
	], 
	"excludes": [""],
	# "include_files": [
	# ]
}

base = None    # ベースとなるウィンドウマネージャを指定

exe = Executable("src/main.py", base=base, target_name="ParseLogs.exe")

# setup 関数を呼び出して、実行ファイルの情報を設定
setup(
    name="ParseLogs",
    version="1.0",
    description="pinfu",
    options = {"build_exe": build_exe_options},    # ビルドオプションを設定
    executables = [exe]  # 実行ファイルを設定
)
