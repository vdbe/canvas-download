#!/usr/bin/env python3
import asyncio
from collections.abc import Callable
from typing import Union
import functools

#from . import Container, Module
from .container import Container
from .module import Module
from .item import Item

class Course(Container):
    TYPE = 3

    def __init__(self, object_id: int, parent_type: int, parent_id: int, object_name: str):
        super().__init__(object_id, parent_type, parent_id)
        self.object_name = object_name

    async def gather(self, get_json: Callable[[str], Union[list[dict], None]], db: dict) -> None:
        tasks = await self.gather_modules(get_json, db)

        tasks = [task(get_json, db) for task in tasks]
        await asyncio.gather(*tasks, self.gather_items_from_syllabus_body(get_json, db))

    async def gather_items_from_syllabus_body(self, get_json: Callable[[str], Union[list[dict], None]], db):
        params = { "include[]": "syllabus_body"}
        json = await get_json(f"courses/{self.object_id}", params=params)

        if json:
            html = json['syllabus_body']
            self.items, tasks = Item.get_correct_objects_from_html(self.TYPE, self.object_id, html)

            for task in asyncio.as_completed([task(get_json, db) for task in tasks]):
                await task

    async def gather_modules(self, get_json: Callable[[str], Union[list[dict], None]], db: dict):
        json = await get_json(f"courses/{self.object_id}/modules")

        if json:
            tasks = list()
            for raw_module in json:
                module_id = raw_module['id']
                module = Module(module_id, self.TYPE, self.object_id, raw_module['name'])

                db[Module.TYPE][module_id] = module
                tasks.append(functools.partial(module.gather))

            return tasks
        return []
