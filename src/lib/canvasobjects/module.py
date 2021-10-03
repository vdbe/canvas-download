#!/usr/bin/env python3
import asyncio
from collections.abc import Callable
from typing import Union
import functools

from lib.canvasobjects.item import File, Page, Assignment, get_item_from_raw

class Module:
    def __init__(self, id, name, items_url, course_id=None) -> None:
        self.id = id
        self.name = name
        self.items_url = items_url

        self.course_id = course_id

        self.items = dict()

        # Some other interesting values
        #self.items_count = items_count

    async def gather(self, get_json: Callable[[str], Union[list[dict], None]]) -> None:
        tasks = await self.gather_items(get_json)

        if tasks:
            for task in asyncio.as_completed([task() for task in tasks]):
                await task

    async def gather_items(self, get_json: Callable[[str], Union[list[dict], None]]):
        #print(self.items_url)
        json = await get_json(self.items_url, full=True)

        if json:
            tasks = []
            for raw_item in json:
                if results := get_item_from_raw(raw_item, get_json):
                    item, task = results
                    tasks.append(task)
                    self.items[raw_item['id']] = item
            return tasks
