import chardet

from module.logger import write_log, LogLevel, DEBUG_LOG_PATH


def encode_to_utf8(some_string):
    """文字列をUTF8にエンコード"""

    try:
        if isinstance(some_string, bytes):
            detected_encoding = chardet.detect(some_string)['encoding']
            decoded_string = some_string.decode(detected_encoding)
            return decoded_string.encode('utf-8')

        return some_string

    except Exception as e:
        # エンコードできない場合は元の文字列のままとする
        write_log("__encode_to_utf8 exception :" + str(e) + " string:" + some_string, LogLevel.E)
        return some_string