#!/usr/bin/env python3
from .canvas import Canvas
from .db import DB
from .download import Download

class Config:
    def __init__(self, **config: dict):
        self.canvas = Canvas(config['canvas'])
        self.db = DB(config['db'])
        self.download = Download(config['download'])
