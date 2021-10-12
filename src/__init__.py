import datetime
import gzip
import os


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
