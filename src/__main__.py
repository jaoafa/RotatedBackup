# 前回のバックアップがなければバックアップ
# 前回のバックアップから今まで誰もログインしていない場合はバックアップをしない
# -> ログファイルをパースし判定
# -> `logged in with entity id` がログファイルにいくつ出てくるかで判定
# -> そもそもチェック時点で鯖に人がいたらバックアップ
# 最低1日1回はバックアップをとる
import datetime
import json
import os
import tarfile

from mcstatus import MinecraftServer

from src import convert_size, delete_old_files, get_today_login_count, send_to_discord
from src.config import Config


def main():
    """
    Main
    """
    log_dir = "/home/server/minecraft/logs/"
    if config.log_dir_path:
        log_dir = os.path.abspath(config.log_dir_path)

    print("[INFO] log_dir: %s" % log_dir)
    if not os.path.exists(log_dir):
        print("[ERROR] log directory does not exist.")
        exit(1)

    today_login_count = get_today_login_count(log_dir)
    print("[INFO] today login count: %d" % today_login_count)

    data = {}
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

    server = MinecraftServer.lookup("localhost")

    # noinspection PyBroadException
    try:
        query = server.query()
        online = query.players.online
    except Exception:
        print("[ERROR] Minecraft server is not online.")
        online = 0

    if online == 0 and "count" in data and data["count"] == today_login_count:
        return  # 現在のオンラインプレイヤー数が0 && 前回のバックアップ時からログイン数かわってない

    with open("data.json", "w") as f:
        json.dump({
            "count": today_login_count
        }, f)

    if not os.path.exists(config.out_path):
        os.mkdir(config.out_path)

    for world in config.worlds:
        print("[INFO] Backup world: %s" % world)
        world_path = os.path.join(config.mcpath, world)
        backup_world_path = os.path.join(config.out_path, world)
        if not os.path.exists(backup_world_path):
            os.mkdir(backup_world_path)

        with tarfile.open(
                os.path.join(backup_world_path, datetime.datetime.now().strftime("%Y-%m-%d_%H-%M") + ".tar.gz"),
                "w:gz") as t:
            t.add(world_path)

        filesize = os.path.getsize(
            os.path.join(backup_world_path, datetime.datetime.now().strftime("%Y-%m-%d_%H-%M") + ".tar.gz"))

        print("[INFO] Backup successfully")
        send_to_discord(config.discord_token, config.discord_channel,
                        ":white_check_mark:ワールド「%s」のローテートバックアップが完了しました。(サイズ: %s)" % (world, convert_size(filesize)))

        print("[INFO] Delete old backup files")
        delete_old_files(backup_world_path)


if __name__ == "__main__":
    if not os.path.exists("config.json"):
        print("[ERROR] config.json not found")
        exit(1)

    config = Config("config.json")
    main()
