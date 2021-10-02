#!/usr/bin/env python3
import json

from lib.canvasobjects.instance import Instance

def main(**kwargs: dict) -> None:
    canvas_endpoint = kwargs['canvas']['endpoint']
    canvas_bearer_token = kwargs['canvas']['bearer_token']

    instance = Instance(canvas_endpoint, canvas_bearer_token)
    instance.start_gather()

if __name__ == "__main__":
    with open('config.json') as fp:
        cfg = json.load(fp)

    main(**cfg)
