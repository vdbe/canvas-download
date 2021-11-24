#!/usr/bin/env python3

class Canvas:
    def __init__(self, canvas_config: dict):
        self.endpoint = canvas_config['endpoint']
        self.bearer_token = canvas_config['bearer_token']
