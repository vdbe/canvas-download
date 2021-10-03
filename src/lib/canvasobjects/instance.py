#!/usr/bin/env python3
import asyncio
import aiohttp
from typing import Union

from lib.canvasobjects.course import Course

class Instance:
    def __init__(self, url: str, bearer_token: str) -> None:
        self.url = url
        self.bearer_token = bearer_token
        self.courses = dict()

    def start_gather(self) -> None:
        headers = {
            "Authorization": f"Bearer {self.bearer_token}"
        }

        asyncio.run(self.gather(headers))

    async def gather(self, headers: dict) -> None:
        # Setup
        self.session = aiohttp.ClientSession(headers=headers)

        # Get everything
        await self.gather_courses()

        # NOTE: Mayber replace with functool.partial
        # to avoid adding every parameter here
        get_json = lambda endpoint, full=False, params=None: self.get_json(endpoint, full=full, params=params)
        for task in asyncio.as_completed([course.gather(get_json) for course in self.courses.values()]):
            await task

        # Shutdown
        await self.session.close()

    async def gather_courses(self) -> None:
        params = {
            'per_page': '500'
        }
        json = await self.get_json("/courses", params=params)

        if json:
            for course in json:
                course_id = course['id']
                self.courses[course_id] = Course(course_id, course['name'])

    async def get_json(self, endpoint: str, *_, full: bool = False, params: bool = None) -> Union[list[dict], None]:
        if full:
            url = endpoint
        else:
            url = f"{self.url}/api/v1/{endpoint}"

        async with self.session.get(url, params=params) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                #print(f"Status code: {resp.status} -> {url}")
                return None
