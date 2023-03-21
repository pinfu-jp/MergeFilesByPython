import psutil

from module.logger import write_log

def get_cpu_core_count():
    """CPUの論理コア数取得"""

    count = psutil.cpu_count(logical=True)  # true:論理コア, false:物理コア
    write_log(f"get_cpu_count() :{count}")
    return count


