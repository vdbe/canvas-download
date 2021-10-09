#!/usr/bin/env python3

class Canvas:
    def __init__(self, canvas_config: dict):
        self.endpoint = canvas_config['endpoint']
        self.bearer_tokens = canvas_config['bearer_tokens']
