from .tools import get_hash
from ..db import controller, models


def main():
    # function for database update for empty
    pass


def save_hash(db_controller, filename):
    sample, info_hash = get_hash(filename)
    info_objects = [models.TorrentInfo(
        name=filename,
        info_hash=info,
    ) for info in info_hash]

    db_controller.insert(info_objects)
    return True




