#!/usr/bin/env python3
from collections.abc import Callable
from typing import Union

class Item:
    def __init__(self, data: dict) -> None:
        self.data = data

        # Other interesting values
        #self.url = url

    async def gather(self, get_json: Callable[[str], Union[list[dict], None]]) -> None:
        return
        print(self.title)
        #await asyncio.sleep(1)
        #await self.gather_items(get_json)

        #for task in asyncio.as_completed([module.gather(get_json) for module in self.module]):
        #    await task
        #

    async def gather_something(self, get_json) -> None:
        pass
        #json = await get_json(self.url, full=True)

        #for item in json:
        #    self.items.append(Item(item['id'], item['title'], item['type'], item['url']))

