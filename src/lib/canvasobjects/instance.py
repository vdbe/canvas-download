#!/usr/bin/env python3
import asyncio
import aiohttp
from typing import Union
import logging
import time

from lib.canvasobjects.course import Course

class Instance:
    def __init__(self, url: str, bearer_tokens: list[str]) -> None:
        self.url = url
        self.bearer_tokens = bearer_tokens
        self.courses = dict()

        #self.requests = 0


    def start_gather(self) -> None:
        self.session_amount = len(self.bearer_tokens)
        self.session_index = 0
        self.session = list()

        asyncio.run(self.gather())

        #logging.info(f"requests: {self.requests}")

    async def gather(self) -> None:
        # Setup
        self.sessions = [aiohttp.ClientSession(headers={"Authorization": f"Bearer {token}"}) for token in self.bearer_tokens]
        self.session = self.sessions[self.session_index]

        # Get everything
        await self.gather_courses()

        # NOTE: Maybe replace with functool.partial
        # to avoid adding every parameter here
        get_json = lambda endpoint, full=False, params=None: self.get_json(endpoint, full=full, params=params)
        for task in asyncio.as_completed([course.gather(get_json) for course in self.courses.values()]):
            await task

        # Shutdown
        for task in asyncio.as_completed([session.close() for session in self.sessions]):
            await task

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
        if full == False:
            endpoint = f"{self.url}/api/v1/{endpoint}"

        async with self.session.get(endpoint, params=params) as resp:
            #self.requests += 1

            #bucket = float(resp.headers['X-Rate-Limit-Remaining'])
            #if bucket < 400:
            #    self.session_index = (self.session_index + 1) % self.session_amount
            #    self.session = self.sessions[self.session_index]
            #    time.sleep(0.1)

            index = self.session_index = (self.session_index + 1) % self.session_amount
            self.session = self.sessions[index]

            if resp.status == 200:
                return await resp.json()
            #elif resp.status == 403:
            #    logging.error(f"403: sessions {self.session_index} -> API-bucket {bucket}")
            #    return None
