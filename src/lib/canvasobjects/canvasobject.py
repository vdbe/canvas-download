#!/usr/bin/env python3

class CanvasObject:
    # CanvasObject: 0, Container: 1, Instance: 2, Course: 3, Module: 4, File: 5, Page: 6, Assignment: 7
    TYPE = 0

    # TODO: replace with enum
    parent_type: int
    parent_id: int
    object_id: int
    object_name: str

    def __init__(self, object_id: int, parent_type: int, parent_id: int) -> None:
        self.object_id = object_id
        self.parent_type = parent_type
        self.parent_id = parent_id
