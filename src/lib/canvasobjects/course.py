#!/usr/bin/env python3
import asyncio
from collections.abc import Callable
from typing import Union

from lib.canvasobjects.module import Module

class Course:
    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name
        self.modules = dict()

    async def gather(self, get_json: Callable[[str], Union[list[dict], None]]) -> None:
        await self.gather_modules(get_json)

        for task in asyncio.as_completed([module.gather(get_json) for module in self.modules.values()]):
            await task

    async def gather_modules(self, get_json: Callable[[str], Union[list[dict], None]]) -> None:
        json = await get_json(f"courses/{self.id}/modules")

        if json:
            for module in json:
                module_id = module['id']
                self.modules[module_id] = Module(module['id'], module['name'], module['items_url'], course_id=self.id)
