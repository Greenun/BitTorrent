from .tools import get_hash
from ..db import controller, models


def main():
    pass


def save_hash(controller, filename):
    sample, info_hash = get_hash(filename)
    info_objects = [models.TorrentInfo(
        name=filename,
        info_hash=info,
    ) for info in info_hash]

    controller.insert(info_objects)
    return