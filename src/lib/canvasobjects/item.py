#!/usr/bin/env python3
from collections.abc import Callable
from typing import Union
from html.parser import HTMLParser
import functools

class File():
    def __init__(self) -> None:
        pass

    async def get(self, url: str, get_json: Callable[[str], Union[list[dict], None]]) -> None:
        json = await get_json(url, full = True)

        if json:
            self.id = json['id']
            self.filename = json['filename']
            self.display_name = json['display_name']
            self.content_type = json['content-type']
            self.url = json['url']
            self.updated_at = json['updated_at']
            # TODO: Look at difference between updated_at and modified_at
            self.modified_at = json['modified_at']

            #print(self.filename)

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
            get_items_from_html(body, get_json)

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
            get_items_from_html(description, get_json)

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.raw_items = list()

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return

        data_api_endpoint = None
        data_return_type = None
        for attr in attrs:
            if attr[0] == 'data-api-endpoint':
                data_api_endpoint = attr[1]
            elif attr[0] == 'data-api-returntype':
                data_return_type = attr[1]
            else:
                #print(attr[0])
                pass

        if data_api_endpoint == None or data_return_type == None:
            #print(attrs)
            return

        self.raw_items.append((data_api_endpoint, data_return_type))

def get_item_from_raw(raw_item, get_json: Callable[[str], Union[list[dict], None]]) -> Union[tuple, None]:
            task = None
            item = None
            item_type = raw_item['type']
            if item_type == 'File':
                item = File()

                task = functools.partial(item.get, raw_item['url'], get_json)
            elif item_type == 'SubHeader':
                # NOTE: Just text
                #print(f"{item_type}: {self.items_url}")
                return
            elif item_type == 'Assignment':
                item = Assignment()

                task = functools.partial(item.get, raw_item['url'], get_json)
            elif item_type == 'Page':
                item = Page()

                task = functools.partial(item.get, raw_item['url'], get_json)
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

            return (item, task)

def get_items_from_html(html: str, get_json: Callable[[str], Union[list[dict], None]]) -> (list, list):
    parser = MyHTMLParser()
    parser.feed(html)

    tasks = list()
    items = list()

    for (url, type) in parser.raw_items:
        if type != "File":
            # TODO: Extract usefull data out of these
            continue
        if results := get_item_from_raw({"type": type, "url": url}, get_json):
            item, task = results
            tasks.append(task)

    # TODO: Maybe use a generator instead of just returning everything
    return (items, tasks)
