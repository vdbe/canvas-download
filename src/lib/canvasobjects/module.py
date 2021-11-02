#!/usr/bin/env python3
import asyncio
from collections.abc import Callable
from typing import Union
import functools

#from lib.canvasobjects.item import File, Page, Assignment, get_item_from_raw

#from . import Container, Item
from .container import Container
from .item import Item

class Module(Container):
    TYPE = 4
    def __init__(self, object_id: int, parent_type: int, parent_id: int, object_name: str):
        super().__init__(object_id, parent_type, parent_id)
        self.object_name = object_name

    async def gather(self, get_json: Callable[[str], Union[list[dict], None]], db: dict) -> None:
        tasks = await self.gather_items(get_json, db)

        if tasks:
            for task in asyncio.as_completed([task(get_json, db) for task in tasks]):
                await task

    async def gather_items(self, get_json: Callable[[str], Union[list[dict], None]], db: dict):
        params = {
            'per_page': '500'
        }
        _, json = await get_json(f"courses/{self.parent_id}/modules/{self.object_id}/items", params=params)

        if json:
            tasks = list()
            for raw_item in json:
                if results := Item.get_correct_object(self.TYPE, self.object_id, raw_item):
                    item, task = results
                    tasks.append(task)
            return tasks
