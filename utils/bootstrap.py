from BitTorrent.utils.tools import get_hash
from BitTorrent.db import controller, models
import os
import pathlib
import argparse

parser = argparse.ArgumentParser(description="Description")
parser.add_argument('--dirname', default="torrent_files", help="directory name")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--all', action="store_true", help="all files in directory")
group.add_argument('--filename', type=str, default="ubuntu-18.04.3-live-server-amd64.iso.torrent")


def main(args):
    # function for empty database update
    user = os.getenv("DB_USER", "postgres")
    pw = os.getenv("DB_PASSWORD", "0584qwqw")
    db_name = os.getenv("DB_NAME", "dht_database")
    host = os.getenv("DB_HOST", "localhost")
    db_controller = controller.DHTDatabase(user=user, password=pw, db_name=db_name, host=host)

    root_dir = pathlib.Path.cwd().parent
    file_dir = root_dir.joinpath(args.dirname)

    if args.all:
        for file in file_dir.glob("*.torrent"):
            save_hash(db_controller, file)
    else:
        filename = args.filename
        save_hash(db_controller, filename)


def save_hash(db_controller, filename):
    sample, info_hash = get_hash(filename)
    info_objects = [models.TorrentInfo(
        name=filename.name,
        info_hash=info,
    ) for info in info_hash]

    # for test 20 info hashes
    info_objects = info_objects[:20]

    db_controller.insert(info_objects)
    return True


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
