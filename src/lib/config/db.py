#!/usr/bin/env python3

class DB:
    def __init__(self, download_config: dict):
        self.directory = download_config['directory']
        self.name = download_config['name']
