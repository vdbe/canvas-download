#!/usr/bin/env python3
from collections.abc import Callable
from typing import Union
from html.parser import HTMLParser
import functools
from pathlib import Path
import urllib
from datetime import datetime
import logging
import asyncio

#from . import CanvasObject, Container
from .canvasobject import CanvasObject
from .container import Container


class Item():
    @staticmethod
    def get_correct_object(parent_type: int, parrent_id: int, raw_item: dict(), object_id: int = None):
        args = [object_id, parent_type, parrent_id]

        item_type = raw_item['type']
        if item_type == 'File':
            item = File(*args)
            task = functools.partial(item.gather, raw_item['url'])

            return item, task

        elif item_type == 'Assignment':
            item = Assignment(*args)
            task = functools.partial(item.gather, raw_item['url'])

            return item, task

        elif item_type == 'Page':
            item = Page(*args)
            task = functools.partial(item.gather, raw_item['url'])

            return item, task

        return False
        #elif item_type == 'SubHeader':
        #    # NOTE: Just text
        #    #print(f"{item_type}: {self.items_url}")
        #    return False
        #elif item_type == 'ExternalUrl':
        #    # NOTE: Links to stuff like Discord
        #    #print(f"{item_type}: {self.items_url}")
        #    return False

        #elif item_type == 'Discussion':
        #    #print(f"{item_type}: {raw_item}")
        #    return False
        #elif item_type == 'ExternalTool':
        #    #print(f"{item_type}: {raw_item}")
        #    return False
        #elif item_type == 'Quiz':
        #    #print(f"{item_type}: {raw_item}")
        #    return False
        #else:
        #        #print(item_type)
        #        return False

    @staticmethod
    def get_correct_objects_from_html(parent_type: int, parent_id: int, html: str):
        parser = MyHTMLParser()
        try:
            parser.feed(html)
        except TypeError:
            # TODO: Find the error here
            pass

        tasks = list()
        items = list()

        for (url, type, object_id) in parser.raw_items:
            if results := Item.get_correct_object(parent_type, parent_id, {"type": type, "url": url}, object_id = object_id):
                item, task = results
                tasks.append(task)

        # TODO: Maybe use a generator instead of just returning everything
        return (items, tasks)


class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.raw_items = list()

    def handle_starttag(self, tag: str, attrs: list):
        if tag != "a":
            return

        id = data_api_returntype = data_api_endpoint = None
        for attr in attrs:
            if attr[0] == 'data-api-endpoint':
                data_api_endpoint = attr[1]
            elif attr[0] == 'data-api-returntype':
                data_api_returntype = attr[1]
                # Nav btns
                if data_api_returntype == "[Module]":
                    return
            elif attr[0] == 'id':
                id = attr[1]

        if data_api_endpoint == None or data_api_returntype == None:
            return

        elif data_api_returntype == 'Assignment':
            id = int(data_api_endpoint.rsplit('/', 1)[-1])
        #elif data_api_returntype == 'Page':
        #    # No way to extract id for a page
        #    pass

        self.raw_items.append((data_api_endpoint, data_api_returntype, id))


class File(CanvasObject):
    TYPE = 5

    def __init__(self, object_id: int, parent_type: int, parent_id: int, object_name: str = None):
        super().__init__(object_id, parent_type, parent_id, object_name)
        self.last_download = 0

    @classmethod
    def from_json_dict(cls, json_dict: dict):
        c = cls(json_dict['object_id'], json_dict['parent_type'], json_dict['parent_id'], json_dict['object_name'])
        c.filename = json_dict['filename']
        c.content_type = json_dict['content_type']
        c.byte_size = json_dict['byte_size']
        c.url = json_dict['url']

        c.updated_at = json_dict['updated_at']
        c.modified_at = json_dict['modified_at']
        c.locked = json_dict['locked']
        c.last_download = json_dict['last_download']

        return c

    def to_json(self):
        json = {
            "parent_type": self.parent_type,
            "parent_id": self.parent_id,
            "object_id": self.object_id,
            "object_name": self.object_name,
            "filename": self.filename,
            "content_type": self.content_type,
            "byte_size": self.byte_size,
            "url": self.url,
            "updated_at": self.updated_at,
            "modified_at": self.modified_at,
            "locked": self.locked,
            "last_download": self.last_download,
        }
        return json

    def download(self, path: Path):
        # Check path create if not exists
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        path = path.joinpath(self.object_name.replace('/', '-'))

        try:
            # TODO: use the `reporthook` from urlretrieve for more accurate download progression
            logging.info(f"dowloading: {path}")
            urllib.request.urlretrieve(self.url, filename=path)
            self.last_download = int(datetime.now().timestamp())
            pass
        except urllib.error.HTTPError as e:
            logging.error("dowload failed: {self.object_name}, {e}, {self.url}")

        return str(path), self.byte_size

    async def gather(self, url: str, get_json, db: dict) -> None:
        # Get lowest possible parent_type if it is a duplicate
        if self.object_id != None:
            val = db[self.TYPE].get(self.object_id)
            if val != None and val.parent_type <= self.parent_type:
                return

        _, json = await get_json(url, full = True)

        if json:
            object_id = self.object_id = json['id']

            d = db[self.TYPE]
            val = d.get(object_id)
            if val != None and d[object_id].parent_type <= self.parent_type:
                return

            self.filename = json['filename']
            self.object_name = json['display_name']
            self.content_type = json['content-type']
            self.byte_size = json['size']

            self.url = json['url']

            # NOTE: it seems that modified_at is the last file change and update_at is the last page change?
            # you can check how many times updated_at and modified_at are differen with the following oneliner:
            # ```sh
            # jq '."5" | .[] | .updated_at,.modified_at,null' data/db/db.json | uniq  -c | grep -v null | awk '{print $1}' | sort -n | uniq -c
            # ```
            # If the second is one it means they where not the same for n/2 items where n is the first number of the line,
            # if the second number on a line can be 1 or 2 is its 2 it means that updated_at and modified_at where the same for n amount of items
            # where n is the first number of the line
            self.updated_at = int(datetime.strptime(json['updated_at'], "%Y-%m-%dT%H:%M:%S%z").timestamp())
            self.modified_at = int(datetime.strptime(json['modified_at'], "%Y-%m-%dT%H:%M:%S%z").timestamp())

            self.last_download = 0

            d[object_id] = self

            if self.url:
                self.locked = False
            else:
                self.url = f"{url.split('api/v1/')[0]}/files/{object_id}/download?download_frd=1&verifier={json['uuid']}"
                self.locked = True


class Page(Container):
    TYPE = 6

    def __init__(self, object_id: int, parent_type: int, parent_id: int, object_name: str = None):
        super().__init__(object_id, parent_type, parent_id, object_name=None)

    async def gather(self, url: str, get_json, db: dict) -> None:
        # No need to check if object_id exists object_id is here always None
        _, json = await get_json(url, full = True)

        if json:
            object_id = self.object_id = json['page_id']

            self.object_name = json['title']

            if json['locked_for_user'] == True:
                return

            d = db[self.TYPE]
            val = d.get(object_id)
            # Get lowest possible parent_type if it is a duplicate
            if val == None or val.parent_type > self.parent_type:
                d[object_id] = self

                body = json['body']
                if body != None:
                    if results := Item.get_correct_objects_from_html(self.TYPE, self.object_id, body):
                        _, tasks = results
                        for task in asyncio.as_completed([task(get_json, db) for task in tasks]):
                            await task


class Assignment(Container):
    TYPE = 7

    def __init__(self, object_id: int, parent_type: int, parent_id: int, object_name: str = None):
        super().__init__(object_id, parent_type, parent_id, object_name)

    async def gather(self, url: str, get_json, db: dict) -> None:
        # Get lowest possible parent_type if it is a duplicate
        if self.object_id != None:
            val = db[self.TYPE].get(self.object_id)
            if val != None and val.parent_type <= self.parent_type:
                return

        _, json = await get_json(url, full = True)

        if json:
            object_id = self.object_id = json['id']
            self.object_name = json['name']
            self.updated_at = json['updated_at']

            if json['locked_for_user'] == True:
                return

            d = db[self.TYPE]
            val = d.get(object_id)
            # Get lowest possible parent_type if it is a duplicate
            if val == None or val.parent_type > self.parent_type:
                d[object_id] = self

                description = json['description']
                if results := Item.get_correct_objects_from_html(self.TYPE, self.object_id, description):
                    _, tasks = results
                    for task in asyncio.as_completed([task(get_json, db) for task in tasks]):
                        await task
