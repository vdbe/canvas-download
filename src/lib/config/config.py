#!/usr/bin/env python3
from .canvas import Canvas
from .db import DB
from .download import Download

class Config:
    def __init__(self, **config: dict):
        self.canvas = Canvas(config['canvas'])
        self.db = DB(config['db'])
        self.download = Download(config['download'])

    @classmethod
    def create(cls, config_file: str):
        import asyncio
        import aiohttp
        import json
        from ..canvasobjects.instance import Instance

        async def check_creds(endpoint: str, token: str):
            creds_valid = False

            async with aiohttp.ClientSession(headers={f"Authorization": f"Bearer {token}"}) as session:
                params = {
                    'per_page': '0'
                }
                async with session.get(f"{endpoint}/api/v1/courses", params=params) as resp:
                    status = resp.status
                    if status == 404:
                        print("Invalid host")
                        creds_valid = False
                    if status == 401:
                        print("Invalid access token")
                        return False
                    elif status == 200:
                        print("Credentials correct")
                        creds_valid = True
                    else:
                        print("Something went wrong please try again")
                        creds_valid = False
            if creds_valid == False:
                exit(1)

        cfg = {}

        print("What is the canvas host, an example is `https://canvas.instructure.com`")
        print("canvas host: ", end="")
        endpoint = input().strip()


        print("What is your API access token?")
        print("If you don't have one already just follow these instructions: https://community.canvaslms.com/t5/Admin-Guide/How-do-I-manage-API-access-tokens-as-an-admin/ta-p/89")
        print("canvas token: ", end="")
        token = input().strip()

        print("")
        print("Checking info...")
        print("")

        loop = asyncio.get_event_loop()
        loop.run_until_complete(check_creds(endpoint, token))

        cfg["canvas"] = {}
        cfg["canvas"]["endpoint"] = endpoint
        cfg["canvas"]["bearer_token"] = token

        print("Do you want to download locked files [yes/no](default no): ", end="")
        answer = input().strip()
        download_locked = False
        if answer == 'yes':
            print("`yes` selected")
            download_locked = True
        elif answer == 'no':
            print("`no` selected")
        else:
            print("Unknown optin defaulting to `no`")
        cfg["download"] = {}
        cfg["download"]["download_locked"] = download_locked

        print("")
        print("How many parallel downloads [1 or bigger](default 10): ", end="")
        answer = input().strip()

        if answer.isdigit():
            d = int(answer)
            if d >= 1:
                cfg["download"]["parallel_downloads"] = d
            else:
                print("Must be > 1")
                return False
        elif len(answer) != 0:
            print("You need to provide an number in digit form")
            return False
        else:
                cfg["download"]["parallel_downloads"] = 10

        cfg["download"]["path"] = "./downloads"

        cfg["db"] = {}
        cfg["db"]["directory"] = "data/db"

        # TODO: check if exists or use random name
        cfg["db"]["name"] = "db.json"

        with open(config_file, "w") as f:
            print("writting config")
            json.dump(cfg, f, indent=True)

        return cfg
