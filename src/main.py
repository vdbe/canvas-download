#!/usr/bin/env python3
import json
import logging
import time
import sqlite3

from lib.canvasobjects.instance import Instance
from lib import canvasobjects

def main(**kwargs: dict) -> None:
    canvas_endpoint = kwargs['canvas']['endpoint']
    canvas_bearer_tokens = kwargs['canvas']['bearer_tokens']


    start = time.time()

    # Scrape Canvas
    instance = Instance(canvas_endpoint, canvas_bearer_tokens)
    instance.start_gather()

    # Statistics
    total_time = time.time() - start
    amount_of_courses = len(instance.courses.keys())
    amount_of_modules = 0
    amount_of_items = 0

    items_in_courses = 0
    items_in_modules = 0


    # Creat DB
    conn = sqlite3.connect(kwargs['db']['path'])
    cur = conn.cursor()
    with open(kwargs['db']['build_script_path'], "r", encoding="utf-8") as script:
        cur.executescript(script.read())

    # TODO: Store in stuple instead of list to avoid conversion
    courses_params = list()
    modules_params = list()
    items_params = list()

    # Fill DB and collect stats
    for course in instance.courses.values():
        items_in_courses += len(course.items)
        amount_of_modules += len(course.modules.keys())
        courses_params.append((course.id, course.name))

        for item in course.items:
            if isinstance(item, canvasobjects.item.File):
                items_params.append((
                    item.id, course.id, None, item.filename, item.display_name, item.content_type,
                     item.url, item.updated_at, item.modified_at
                ))

        for module in course.modules.values():
            modules_params.append((module.id, module.name))
            for item in module.items.values():
                if isinstance(item, canvasobjects.item.File):
                    items_params.append((
                        item.id, module.course_id, module.id, item.filename, item.display_name, item.content_type,
                        item.url, item.updated_at, item.modified_at
                    ))
            items_in_modules += len(module.items.keys())

    cur.executemany("INSERT OR IGNORE INTO Course (course_id, course_name) VALUES (?, ?)", tuple(courses_params))
    cur.executemany("INSERT OR IGNORE INTO Module (module_id, module_name) VALUES (?, ?)", tuple(modules_params))

    # TODO: Update data if it changes
    cur.executemany(
        "INSERT OR IGNORE INTO File (file_id, course_id, module_id, filename, display_name, content_type, url, updated_at, modified_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        tuple(items_params)
    )
    # Make sure changes are written
    conn.commit()

    # Print stats
    amount_of_items = items_in_courses + items_in_modules

    logging.info(f"time: {total_time}")
    logging.info(f"courses: {amount_of_courses}")
    logging.info(f"modules: {amount_of_modules}")
    logging.info(f"items: {amount_of_items}")

    logging.debug(f"items in modules: {items_in_modules}")
    logging.debug(f"items in courses: {items_in_courses}")



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    with open('config.json') as fp:
        cfg = json.load(fp)

    main(**cfg)
