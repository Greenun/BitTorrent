from .tools import get_hash
from ..db import controller, models
import os
import pathlib
import argparse

parser = argparse.ArgumentParser(description="Description")
parser.add_argument('--dirname', default="torrent_files", required=True, help="directory name")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--all', help="all files in directory")
group.add_argument('--filename', type=str, default="ubuntu-18.04.3-live-server-amd64.iso.torrent")


def main(args):
    # function for database update for empty
    user = os.getenv("DB_USER", "postgres")
    pw = os.getenv("DB_PASSWORD", "0584qwqw")
    db_name = os.getenv("DB_NAME", "dht_database")
    host = os.getenv("DB_HOST", "localhost")
    db_controller = controller.DHTDatabase(user=user, password=pw, db_name=db_name, host=host)

    dirpath = pathlib.Path('.')

    if args.all:
        pass
    else:
        filename = args.filename
        save_hash(db_controller, )


def save_hash(db_controller, filename):
    sample, info_hash = get_hash(filename)
    info_objects = [models.TorrentInfo(
        name=filename,
        info_hash=info,
    ) for info in info_hash]

    db_controller.insert(info_objects)
    return True


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)