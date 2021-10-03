#!/usr/bin/env python3
import asyncio
from collections.abc import Callable
from typing import Union

from lib.canvasobjects.module import Module
from lib.canvasobjects.item import get_items_from_html

class Course:
    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name
        self.modules = dict()
        self.items = dict()

    async def gather(self, get_json: Callable[[str], Union[list[dict], None]]) -> None:
        await self.gather_modules(get_json)

        tasks = [module.gather(get_json) for module in self.modules.values()]
        tasks.append(self.gather_items_from_syllabus_body(get_json))
        for task in asyncio.as_completed(tasks):
            await task

    async def gather_items_from_syllabus_body(self, get_json: Callable[[str], Union[list[dict], None]]):
        params = { "include[]": "syllabus_body"}
        json = await get_json(f"courses/{self.id}", params=params)

        if json:
            html = json['syllabus_body']
            self.items, tasks = get_items_from_html(html, get_json)

            for task in asyncio.as_completed([task() for task in tasks]):
                await task


        pass
    async def gather_modules(self, get_json: Callable[[str], Union[list[dict], None]]) -> None:
        json = await get_json(f"courses/{self.id}/modules")

        if json:
            for module in json:
                module_id = module['id']
                self.modules[module_id] = Module(module['id'], module['name'], module['items_url'], course_id=self.id)
