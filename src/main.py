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
from datetime import datetime

def main(**kwargs: dict) -> None:
    canvas_endpoint = kwargs['canvas']['endpoint']
    canvas_bearer_tokens = kwargs['canvas']['bearer_tokens']
    db_dir = kwargs['db']['directory']
    db_name = kwargs['db']['name']

    # Scrape Canvas
    logging.info(f"start gather...")
    instance = Instance(canvas_endpoint, canvas_bearer_tokens)
    start_time = time.time()
    instance.start_gather()
    logging.info(f"gather time: {time.time() - start_time}")

    db = instance.db

    logging.info(f"requests: {instance.requests}")
    logging.info(f"courses: {len(db[Course.TYPE])}")
    logging.info(f"modules: {len(db[Module.TYPE])}")
    logging.info(f"pages: {len(db[Page.TYPE])}")
    logging.info(f"assigments: {len(db[Assignment.TYPE])}")
    logging.info(f"files: {len(db[File.TYPE])}")
    logging.info(f"loading db...")

    # Make sure db folder exists
    Path(db_dir).mkdir(parents=True, exist_ok=True)
    old_db = dict()
    db_file = Path(db_dir, db_name)
    if db_file.is_file():
        with open(str(db_file), 'rb') as handle:
            old_db = pickle.load(handle)
    else:
        old_db = db

    path_start = kwargs['download']['path']
    total_byte_size = 0
    downloads = list()
    safe = not kwargs['download']['download_locked']

    logging.info(f"comparing timstamps...")
    files = db[File.TYPE]
    old_files = old_db[File.TYPE]
    for file in files.values():

        old_file = old_files[file.object_id]
        if old_file.last_download > file.modified_at:
            file.last_download = old_file.last_download
            continue

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

            path_stack.append(container.object_name)

        path = Path(path_start, *path_stack[::-1])
        downloads.append(functools.partial(file.download, path))


    if len(downloads):
        logging.info(f"files to downloads: {len(downloads)}")
        logging.info(f"total download size: {sizeof_fmt(total_byte_size)}")

        parallel_downloads = kwargs['download']['parallel_downloads']
        logging.info(f"parallel downloads: {parallel_downloads}")

        logging.info(f"starting downloads...")
        start_time = time.time()
        for _ in ThreadPool(parallel_downloads).imap_unordered(lambda f: f(), downloads):
            pass

        logging.info(f"download time: {time.time() - start_time}")
    else:
        logging.info(f"all files up-to-date")

    logging.info(f"commiting db...")
    with open(db_file, 'wb') as handle:
        pickle.dump(db, handle, protocol=pickle.HIGHEST_PROTOCOL)

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
