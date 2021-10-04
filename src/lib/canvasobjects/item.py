#!/usr/bin/env python3
from collections.abc import Callable
from typing import Union
from html.parser import HTMLParser
import functools

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

        title = None

        data_api_endpoint = None
        data_return_type = None
        for attr in attrs:
            if attr[0] == 'data-api-endpoint':
                data_api_endpoint = attr[1]
            elif attr[0] == 'data-api-returntype':
                data_return_type = attr[1]
            elif attr[0] == 'title':
                title = attr[1]
            else:
                #print(attr[0])
                pass

        if data_api_endpoint == None or data_return_type == None:
            #print(attrs)
            return

        if title and data_return_type == 'File':
            #print(title)
            pass

        self.raw_items.append((data_api_endpoint, data_return_type))

class File(CanvasObject):
    TYPE = 5

    def __init__(self, object_id, parent_type, parent_id):
        super().__init__(object_id, parent_type, parent_id)

    async def gather(self, url: str, get_json, db: dict) -> None:
        json = await get_json(url, full = True)

        if json:
            file_id = self.id = json['id']
            self.filename = json['filename']
            self.display_name = json['display_name']
            self.content_type = json['content-type']
            self.url = json['url']
            self.updated_at = json['updated_at']
            # TODO: Look at difference between updated_at and modified_at
            self.modified_at = json['modified_at']

            db[self.TYPE][file_id] = self

class Page(Container):
    TYPE = 6

    def __init__(self, object_id, parent_type, parent_id):
        super().__init__(object_id, parent_type, parent_id)

    async def gather(self, url: str, get_json: Callable[[str], Union[list[dict], None]], db: dict) -> None:
        json = await get_json(url, full = True)

        if json:
            object_id = self.object_id = json['page_id']
            self.object_name = json['title']

            # TODO: check is this indeed not needed
            #self.updated_at = json['updated_at']

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

            # TODO: extract items from description
            description = json['description']
            Item.get_correct_objects_from_html(self.TYPE, self.object_id, description)
