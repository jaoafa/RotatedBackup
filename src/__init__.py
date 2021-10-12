import datetime
import gzip
import json
import math
import os

import requests


def get_login_count(filepath: str) -> int:
    """
    `logged in with entity id` の数を調べることにより、ログファイルのログイン数を取得します。

    :param filepath: ログファイルのパス
    :return: ログイン数
    """
    if filepath.endswith(".gz"):
        with gzip.open(filepath, mode='rt', encoding='utf-8') as f:
            data = f.read()
    else:
        with open(filepath, "r", encoding="utf-8") as f:
            data = f.read()
    return data.count("logged in with entity id")


def get_today_login_count(logfiles_path: str) -> int:
    """
    今日のログイン数を取得します。

    :param logfiles_path: ログファイルディレクトリのパス
    :return: ログイン数
    """
    files = os.listdir(logfiles_path)
    files = [f for f in files if os.path.isfile(os.path.join(logfiles_path, f))]
    files = [f for f in files if f.startswith(datetime.date.today().strftime("%Y-%m-%d"))]

    login_count = 0
    for f in files:
        login_count += get_login_count(os.path.join(logfiles_path, f))
    login_count += get_login_count(os.path.join(logfiles_path, "latest.log"))

    return login_count


def delete_old_files(path: str):
    """
    古いファイルを削除します。
    """
    files = os.listdir(path)
    files = [f for f in files if os.path.isfile(os.path.join(path, f))]
    files = [f for f in files if f.endswith(".tar.gz")]
    files = [f for f in files if len(f) == 23]

    if len(files) < 24:
        return
    files.sort()

    for file in files:
        if len(files) < 24:
            return
        os.unlink(os.path.join(path, file))


def send_to_discord(token,
                    channelId,
                    message,
                    embed=None,
                    files=None):
    """
    Discordにメッセージを送信します。
    """
    if files is None:
        files = {}
    headers = {
        "Authorization": "Bot {token}".format(token=token),
        "User-Agent": "Bot"
    }
    params = {
        "payload_json": json.dumps({
            "content": message,
            "embed": embed
        })
    }
    response = requests.post(
        "https://discord.com/api/channels/{channelId}/messages".format(channelId=channelId), headers=headers,
        data=params, files=files)
    print(response.status_code)
    print(response.json())


def convert_size(size_bytes):
    """
    bytesを人間が読みやすいサイズ表記に変えます
    """
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])
