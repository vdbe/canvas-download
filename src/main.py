#!/usr/bin/env python3
import json
import logging

from lib.canvasobjects.instance import Instance

def main(**kwargs: dict) -> None:
    canvas_endpoint = kwargs['canvas']['endpoint']
    canvas_bearer_token = kwargs['canvas']['bearer_token']

    instance = Instance(canvas_endpoint, canvas_bearer_token)
    instance.start_gather()

    if logging.root.level <= logging.INFO:
        amount_of_courses = len(instance.courses.keys())
        amount_of_modules = 0
        amount_of_items = 0

        items_in_courses = 0
        items_in_modules = 0

        for course in instance.courses.values():
            items_in_courses += len(course.items)
            amount_of_modules += len(course.modules.keys())

            for module in course.modules.values():
                items_in_modules += len(module.items.keys())

        amount_of_items = items_in_courses + items_in_modules

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
