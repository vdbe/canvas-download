#!/usr/bin/env python3
import asyncio
from collections.abc import Callable
from typing import Union

from lib.canvasobjects.item import Item

class Module:
    def __init__(self, id, name, items_url) -> None:
        self.id = id
        self.name = name
        self.items_url = items_url

        self.items = list()

        # Some other interesting values
        #self.items_count = items_count

    async def gather(self, get_json: Callable[[str], Union[list[dict], None]]) -> None:
        await self.gather_items(get_json)

        for task in asyncio.as_completed([item.gather(get_json) for item in self.items]):
            await task

    async def gather_items(self, get_json: Callable[[str], Union[list[dict], None]]) -> None:
        #print(self.items_url)
        json = await get_json(self.items_url, full=True)

        if json:
            for item in json:
                # TODO: add logic for each item type
                self.items.append(Item(item))
                #self.items.append(Item(item['id'], item['title'], item['type']))
