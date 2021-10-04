#!/usr/bin/env python3
import json
import logging
import time
import sqlite3

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

    for file in db[File.TYPE].values():
        print(file.display_name)


    # Print stats
    logging.info(f"time: {total_time}")
    logging.info(f"requests: {instance.requests}")
    logging.info(f"courses: {len(db[Course.TYPE])}")
    logging.info(f"modules: {len(db[Module.TYPE])}")
    logging.info(f"files: {len(db[File.TYPE])}")
    logging.info(f"pages: {len(db[Page.TYPE])}")
    logging.info(f"assigments: {len(db[Assignment.TYPE])}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    with open('config.json') as fp:
        cfg = json.load(fp)

    main(**cfg)
