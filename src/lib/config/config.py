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
    def create(cls, config_file: str, endpoint = None, token = None, download_locked = None, parallel_downloads = None):
        import asyncio
        import aiohttp
        import json
        import logging
        from pathlib import Path
        from ..canvasobjects.instance import Instance

        async def check_creds(ptr: dict, endpoint: str, token: str):
            creds_valid = False

            async with aiohttp.ClientSession(headers={f"Authorization": f"Bearer {token}"}) as session:
                params = {
                    'per_page': '0'
                }
                async with session.get(f"{endpoint}/api/v1/courses", params=params) as resp:
                    status = resp.status
                    if status == 404:
                        logging.info("Invalid host")
                        creds_valid = False
                    if status == 401:
                        logging.info("Invalid access token")
                        return False
                    elif status == 200:
                        logging.info("Credentials correct")
                        creds_valid = True
                    else:
                        logging.info("Something went wrong please try again")
                        creds_valid = False
                ptr['success'] = creds_valid

        cfg = {}

        if endpoint == None:
            print("What is the canvas host, an example is `https://canvas.instructure.com`")
            print("canvas host: ", end="")
            endpoint = input().strip()


        if token == None:
            print("")
            print("What is your API access token?")
            print("If you don't have one already just follow these instructions: https://community.canvaslms.com/t5/Admin-Guide/How-do-I-manage-API-access-tokens-as-an-admin/ta-p/89")
            print("canvas token: ", end="")
            token = input().strip()

        logging.info("")
        logging.info("Checking info...")

        d = {
            "success": False
        }
        loop = asyncio.get_event_loop()
        loop.run_until_complete(check_creds(d, endpoint, token))
        logging.info("")

        if d["success"] == False:
            logging.info("exit")
            return False

        cfg["canvas"] = {}
        cfg["canvas"]["endpoint"] = endpoint
        cfg["canvas"]["bearer_token"] = token


        if download_locked == None:
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

        if download_locked == None:
            print("")
            print("How many parallel downloads [1 or bigger](default 10): ", end="")
            answer = input().strip()

            if answer.isdigit():
                d = int(answer)
                if d >= 1:
                    parallel_downloads = d
                else:
                    print("Must be > 1")
                    return False
            elif len(answer) != 0:
                print("You need to provide an number in digit form")
                return False
            else:
                parallel_downloads = 10

        cfg["download"]["parallel_downloads"] = parallel_downloads

        cfg["download"]["path"] = "./downloads"

        cfg["db"] = {}
        cfg["db"]["directory"] = "data/db"

        # TODO: check if exists or use random name
        cfg["db"]["name"] = "db.json"


        # Create dir
        Path(config_file).parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, "w") as f:
            logging.info("writting config file")
            json.dump(cfg, f, indent=True)
        print("")

        return Config(**cfg)
