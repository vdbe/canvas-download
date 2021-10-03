#!/usr/bin/env python3
from collections.abc import Callable
from typing import Union

class File():
    def __init__(self) -> None:
        pass

    async def get(self, url: str, get_json: Callable[[str], Union[list[dict], None]]) -> None:
        json = await get_json(url, full = True)

        if json:
            self.id = json['id']
            self.filename = json['filename']
            self.display_name = json['display_name']
            self.conten_type = json['content-type']
            self.url = json['url']
            self.updated_at = json['updated_at']
            # TODO: Look at difference between updated_at and modified_at
            self.modified_at = json['modified_at']

class Page():
    def __init__(self) -> None:
        pass

    async def get(self, url: str, get_json: Callable[[str], Union[list[dict], None]]) -> None:
        json = await get_json(url, full = True)

        if json:
            self.title = json['title']
            self.updated_at = json['updated_at']

            if json['locked_for_user'] == True:
                return

            # TODO: extract items from body
            body = json['body']

class Assignment():
    def __init__(self) -> None:
        pass

    async def get(self, url: str, get_json: Callable[[str], Union[list[dict], None]]) -> None:
        json = await get_json(url, full = True)

        if json:
            self.name = json['name']
            self.updated_at = json['updated_at']

            if json['locked_for_user'] == True:
                return

            # TODO: extract items from description
            description = json['description']
