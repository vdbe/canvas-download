#!/usr/bin/env python3
import json
import logging
import time
from multiprocessing.pool import ThreadPool
from pathlib import Path
import functools
import pickle

from lib.canvasobjects.instance import Instance
from lib.canvasobjects.item import File, Page, Assignment
from lib.canvasobjects.course import Course
from lib.canvasobjects.module import Module

def main(**kwargs: dict) -> None:
    canvas_endpoint = kwargs['canvas']['endpoint']
    canvas_bearer_tokens = kwargs['canvas']['bearer_tokens']


    start = time.time()

    # Scrape Canvas
    instance = Instance(canvas_endpoint, canvas_bearer_tokens)
    instance.start_gather()

    # Statistics
    total_time = time.time() - start

    db = instance.db

    path_start = kwargs['download']['path']
    total_byte_size = 0
    downloads = list()
    safe = not kwargs['download']['download_locked']

    for file in db[File.TYPE].values():
        if safe and file.locked:
            continue

        total_byte_size += file.byte_size
        path_stack = list()

        container_type = file.parent_type
        container_id = file.parent_id
        while container_type != Instance.TYPE:
            container = db[container_type][container_id]
            container_type = container.parent_type
            container_id = container.parent_id
            container_name = container.object_name

            path_stack.append(container_name)

        path = Path(path_start, *path_stack[::-1])
        downloads.append(functools.partial(file.download, path))

    # Print stats
    logging.info(f"gather time: {total_time}")
    logging.info(f"requests: {instance.requests}")
    logging.info(f"courses: {len(db[Course.TYPE])}")
    logging.info(f"modules: {len(db[Module.TYPE])}")
    logging.info(f"pages: {len(db[Page.TYPE])}")
    logging.info(f"assigments: {len(db[Assignment.TYPE])}")
    logging.info(f"files: {len(db[File.TYPE])}")
    logging.info(f"total file size: {sizeof_fmt(total_byte_size)}")

    parallel_downloads = kwargs['download']['parallel_downloads']
    logging.info(f"parallel downloads: {parallel_downloads}")

    for _ in ThreadPool(parallel_downloads).imap_unordered(lambda f: f(), downloads):
        pass


# SRC: https://stackoverflow.com/questions/1094841/get-human-readable-version-of-file-size
def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    with open('config.json') as fp:
        cfg = json.load(fp)

    main(**cfg)
