#!/usr/bin/env python3
import asyncio
import aiohttp
from typing import Union, Tuple
import logging
import time
import functools

#from . import Container, Course
from .container import Container
from .course import Course

class Instance(Container):
    TYPE = 2

    def __init__(self, url: str, bearer_token: str) -> None:
        super().__init__(0, self.TYPE, 0)
        #self.bearer_tokens = bearer_tokens
        self.bearer_token = bearer_token
        self.url = url
        self.parent_id = 0

        db = self.db = dict()

        # TODO: Dont hardcode
        for i in range(3, 7+1):
            db[i] = dict()

        self.requests = 0
        self.dup_requests = 0


    def start_gather(self) -> None:
        #self.session_amount = len(self.bearer_tokens)
        #self.session_index = 0
        #self.sessions = list()

        asyncio.run(self.gather())

    async def gather(self) -> None:
        # Setup
        #self.sessions = [aiohttp.ClientSession(headers={"Authorization": f"Bearer {token}"}) for token in self.bearer_tokens]
        #self.session = self.sessions[self.session_index]
        self.session = aiohttp.ClientSession(headers={f"Authorization": f"Bearer {self.bearer_token}"})

        # Get everything
        tasks = await self.gather_courses()

        if tasks:
            # NOTE: Maybe replace with functool.partial
            # to avoid adding every parameter here
            get_json = lambda endpoint, full=False, params=None: self.get_json(endpoint, full=full, params=params)
            tasks = [task(get_json, self.db) for task in tasks]
            await asyncio.gather(*tasks)

        # Shutdown
        #for task in asyncio.as_completed([session.close() for session in self.sessions]):
        #    await task
        await self.session.close()

    async def gather_courses(self) -> list:
        params = {
            'per_page': '500'
        }
        _, json = await self.get_json("/courses", params=params)

        if json:
            tasks = list()

            for raw_course in json:
                course_id = raw_course['id']
                course = Course(course_id, self.TYPE, self.parent_id, raw_course['name'])
                self.db[Course.TYPE][course_id] = course
                tasks.append(functools.partial(course.gather))

            return tasks


    async def get_json(self, endpoint: str, *_, full: bool = False, params: bool = None, repeat=True) -> Tuple[int ,Union[list[dict], bool]]:
        if full == False:
            endpoint = f"{self.url}/api/v1/{endpoint}"

        async with self.session.get(endpoint, params=params) as resp:
            self.requests += 1

            #bucket = float(resp.headers['X-Rate-Limit-Remaining'])
            #if bucket < 400:
            #    self.session_index = (self.session_index + 1) % self.session_amount
            #    self.session = self.sessions[self.session_index]
            #    time.sleep(0.1)

            #index = self.session_index = (self.session_index + 1) % self.session_amount
            #self.session = self.sessions[index]

            status = resp.status
            if status == 200:
                return resp.status, await resp.json()
            elif status == 403 and repeat:
                for i in range(20):
                    self.dup_requests += 1
                    if i < 5:
                        pass
                    elif i < 10:
                        await asyncio.sleep(.01 * i)
                    else:
                        logging.debug(f"repeated request {i} times: {endpoint}")
                        time.sleep(0.1 * i)

                    new_status, res = await self.get_json(endpoint, params=params, full=True, repeat=False)
                    if new_status != 403:
                        return new_status, res

                logging.error(f"403: sessions {self.session_index} {endpoint}")
            else:
                return status, False
