#!/usr/bin/env python3

class Download:
    def __init__(self, download_config: dict):
        self.parallel_downloads = download_config['parallel_downloads']
        self.download_locked = download_config['download_locked']
        self.path = download_config['path']
