#!/usr/bin/env python3
import asyncio
from collections.abc import Callable
from typing import Union
import functools

from lib.canvasobjects.item import File, Page, Assignment

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
            for item in json:
                item_type = item['type']
                item_id = item['id']
                if item_type == 'File':
                    file_item = File()
                    self.items[item_id] = file_item

                    task = functools.partial(file_item.get, item['url'], get_json)
                    tasks.append(task)
                elif item_type == 'SubHeader':
                    # Note: Just text
                    #print(f"{item_type}: {self.items_url}")
                    pass
                elif item_type == 'Assignment':
                    assignment_item = Assignment()
                    self.items[item_id] = assignment_item

                    task = functools.partial(assignment_item.get, item['url'], get_json)
                    tasks.append(task)
                    pass
                elif item_type == 'Page':
                    page_item = Page()
                    self.items[item_id] = page_item

                    task = functools.partial(page_item.get, item['url'], get_json)
                    tasks.append(task)
                elif item_type == 'ExternalUrl':
                    # Note: Links to stuff like Discord
                    #print(f"{item_type}: {self.items_url}")
                    pass
                else:
                        print(item_type)
            return tasks
