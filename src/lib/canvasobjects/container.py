#!/usr/bin/env python3
from .canvasobject import CanvasObject
#from . import CanvasObject

class Container(CanvasObject):
    TYPE = 1

    def __init__(self, object_id, parent_type, parent_id, object_name=None):
        super().__init__(object_id, parent_type, parent_id, object_name=None)
