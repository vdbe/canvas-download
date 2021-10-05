#!/usr/bin/env python3
from collections.abc import Callable
from typing import Union
from html.parser import HTMLParser
import functools
from pathlib import Path
import urllib
from datetime import datetime
import logging

#from . import CanvasObject, Container
from .canvasobject import CanvasObject
from .container import Container

class Item():
    @staticmethod
    def get_correct_object(parent_type: int, parrent_id: int, raw_item: dict()):
        args = [None, parent_type, parrent_id]

        item_type = raw_item['type']
        if item_type == 'File':
            item = File(*args)
            task = functools.partial(item.gather, raw_item['url'])

            return item, task

        elif item_type == 'SubHeader':
            # NOTE: Just text
            #print(f"{item_type}: {self.items_url}")
            return

        elif item_type == 'Assignment':
            item = Assignment(*args)
            task = functools.partial(item.gather, raw_item['url'])

            return item, task

        elif item_type == 'Page':
            item = Page(*args)
            task = functools.partial(item.gather, raw_item['url'])

            return item, task

        elif item_type == 'ExternalUrl':
            # NOTE: Links to stuff like Discord
            #print(f"{item_type}: {self.items_url}")
            return

        elif item_type == 'Discussion':
            print(f"{item_type}: {raw_item}")
            return

        elif item_type == 'ExternalTool':
            print(f"{item_type}: {raw_item}")
            return

        else:
                print(item_type)
                return

    @staticmethod
    def get_correct_objects_from_html(parent_type: int, parent_id: int, html: str) -> (list, list):
        parser = MyHTMLParser()
        parser.feed(html)

        tasks = list()
        items = list()

        for (url, type) in parser.raw_items:
            if type != "File":
                # TODO: Extract usefull data out of these
                continue
            if results := Item.get_correct_object(parent_type, parent_id, {"type": type, "url": url}):
                item, task = results
                tasks.append(task)

        # TODO: Maybe use a generator instead of just returning everything
        return (items, tasks)

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.raw_items = list()

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return

        data_api_endpoint = None
        data_api_returntype = None
        for attr in attrs:
            if attr[0] == 'data-api-endpoint':
                data_api_endpoint = attr[1]
            elif attr[0] == 'data-api-returntype':
                data_api_returntype = attr[1]

        if data_api_endpoint == None or data_api_returntype == None:
            return

        self.raw_items.append((data_api_endpoint, data_api_returntype))

class File(CanvasObject):
    TYPE = 5

    def __init__(self, object_id, parent_type, parent_id):
        super().__init__(object_id, parent_type, parent_id)

    def download(self, path: Path):
        #print(f"download: {path}/{self.display_name}")

        # Check path create if not exists
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        path = path.joinpath(self.display_name)

        try:
            # TODO: use the `reporthook` from urlretrieve for more accurate download progression
            urllib.request.urlretrieve(self.url, filename=path)
            self.last_download = datetime.now().timestamp()
        except urllib.error.HTTPError as e:
            print(path, e)
            logging.e
            logging.error("dowload failed: {self.display_name}, {e}, {self.url}")

        return str(path), self.byte_size



    async def gather(self, url: str, get_json, db: dict) -> None:
        json = await get_json(url, full = True)

        if json:
            object_id = self.object_id = json['id']
            self.filename = json['filename']
            self.display_name = json['display_name']
            self.content_type = json['content-type']
            self.byte_size = json['size']

            self.url = json['url']

            self.updated_at = datetime.strptime(json['updated_at'], "%Y-%m-%dT%H:%M:%S%z").timestamp()
            # TODO: Look at difference between updated_at and modified_at
            self.modified_at = datetime.strptime(json['updated_at'], "%Y-%m-%dT%H:%M:%S%z").timestamp()

            self.last_download = 0

            db[self.TYPE][object_id] = self

            if self.url:
                self.locked = False
            else:
                self.url = f"{url.split('api/v1/')[0]}/files/{object_id}/download?download_frd=1&verifier={json['uuid']}"
                self.locked = True


class Page(Container):
    TYPE = 6

    def __init__(self, object_id, parent_type, parent_id):
        super().__init__(object_id, parent_type, parent_id)

    async def gather(self, url: str, get_json: Callable[[str], Union[list[dict], None]], db: dict) -> None:
        json = await get_json(url, full = True)

        if json:
            object_id = self.object_id = json['page_id']
            self.object_name = json['title']

            db[self.TYPE][object_id] = self

            if json['locked_for_user'] == True:
                return

            body = json['body']
            Item.get_correct_objects_from_html(self.TYPE, self.object_id, body)

class Assignment(Container):
    TYPE = 7

    def __init__(self, object_id, parent_id, name):
        super().__init__(object_id, parent_id, name)

    async def gather(self, url: str, get_json: Callable[[str], Union[list[dict], None]], db) -> None:
        json = await get_json(url, full = True)

        if json:
            object_id = self.object_id = json['id']
            self.object_name = json['name']
            self.updated_at = json['updated_at']

            if json['locked_for_user'] == True:
                return

            db[self.TYPE][object_id] = self

            description = json['description']
            Item.get_correct_objects_from_html(self.TYPE, self.object_id, description)
