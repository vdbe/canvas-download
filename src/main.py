#!/usr/bin/env python3
import json
import logging
import time
from multiprocessing.pool import ThreadPool
from pathlib import Path
import functools
from json import JSONEncoder

from lib.canvasobjects.module import Module
from lib.canvasobjects.instance import Instance
from lib.canvasobjects.item import File, Page, Assignment
from lib.canvasobjects.course import Course
from lib.config import Config

def main(config: Config) -> None:
    # Scrape Canvas
    logging.info(f"start gathering...")
    instance = Instance(config.canvas.endpoint, config.canvas.bearer_token)
    start_time = time.time()
    instance.start_gather()
    logging.info(f"gather time: {time.time() - start_time:.2f}s")

    db = instance.db

    logging.info(f"uniq requests: {instance.requests - instance.dup_requests}")
    logging.info(f"dup requests: {instance.dup_requests}")
    logging.info(f"courses: {len(db[Course.TYPE])}")
    logging.info(f"modules: {len(db[Module.TYPE])}")
    logging.info(f"pages: {len(db[Page.TYPE])}")
    logging.info(f"assigments: {len(db[Assignment.TYPE])}")
    logging.info(f"files: {len(db[File.TYPE])}")
    logging.info(f"loading db...")

    # Make sure db folder exists
    Path(config.db.directory).mkdir(parents=True, exist_ok=True)
    old_db = dict()
    db_file = Path(config.db.directory, config.db.name)
    if db_file.is_file():
        with open(db_file, "r") as f:
            json_db = json.loads(f.read())

        object_class_dict = {
            Instance.TYPE: Instance.from_json_dict,
            Course.TYPE: Course.from_json_dict,
            Module.TYPE: Module.from_json_dict,
            File.TYPE: File.from_json_dict,
            Page.TYPE: Page.from_json_dict,
            Assignment.TYPE: Assignment.from_json_dict,
        }

        for object_type in map(int, json_db.keys()):
            old_db[object_type] = dict()
            for canvas_object in json_db[str(object_type)]:
                o = object_class_dict[object_type](canvas_object)
                old_db[object_type][o.object_id] = o
    else:
        old_db = db


    path_start = config.download.path
    total_byte_size = 0
    downloads = list()
    safe = not config.download.download_locked

    logging.info(f"comparing timestamps...")
    files = db[File.TYPE]
    old_files = old_db[File.TYPE]
    for file in files.values():
        try:
            old_file = old_files[file.object_id]
        except KeyError:
            old_file = file

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

            path_stack.append(container.object_name.replace('/', '-'))

        path = Path(path_start, *path_stack[::-1])
        downloads.append(functools.partial(file.download, path))


    if len(downloads):
        logging.info(f"files to downloads: {len(downloads)}")
        logging.info(f"total download size: {sizeof_fmt(total_byte_size)}")

        parallel_downloads = config.download.parallel_downloads
        logging.info(f"parallel downloads: {parallel_downloads}")

        logging.info(f"starting downloads...")
        start_time = time.time()
        for _ in ThreadPool(parallel_downloads).imap_unordered(lambda f: f(), downloads):
            pass

        logging.info(f"download time: {time.time() - start_time:.2f}s")
    else:
        logging.info(f"all files up-to-date")

    logging.info(f"commiting db...")

    def _default(self, obj):
        return getattr(obj.__class__, "to_json", _default.default)(obj)

    # SRC: https://stackoverflow.com/a/38764817
    _default.default = JSONEncoder().default
    JSONEncoder.default = _default

    # Update the old db with the new values
    # this way no data is lost when removed upstream
    d = dict()
    for key in old_db.keys():
        old_db[key].update(db[key])
        d[key] = list(old_db[key].values())
    del db
    del old_db

    with open(db_file, "w") as f:
        json.dump(d, f)

    logging.info(f"exiting...")


# SRC: https://stackoverflow.com/questions/1094841/get-human-readable-version-of-file-size
def sizeof_fmt(num: int, suffix: str = "B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    import sys

    if len(sys.argv) > 1:
        conf = sys.argv[1]
        if conf == '=h' or conf == "--help":
            print(f"f{sys.argv[0]} [config file]")
            exit(0)
    else:
        conf = 'data/config/config.json'

    if Path(conf).is_file():
        with open(conf) as fp:
            cfg = json.load(fp)
            config = Config(**cfg)
            del cfg
    else:
        config = Config.create(conf)
        if config == False:
            exit(1)

    main(config)
