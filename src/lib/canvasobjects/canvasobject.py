#!/usr/bin/env python3
import json

class CanvasObject:
    # CanvasObject: 0, Container: 1, Instance: 2, Course: 3, Module: 4, File: 5, Page: 6, Assignment: 7
    TYPE = 0

    # TODO: replace with enum
    parent_type: int
    parent_id: int
    object_id: int
    object_name: str

    def __init__(self, object_id: int, parent_type: int, parent_id: int, object_name = None) -> None:
        self.object_id = object_id
        self.parent_type = parent_type
        self.parent_id = parent_id
        self.object_name = object_id

    def to_json(self):
        json = {"parent_type": self.parent_type, "parent_id": self.parent_id, "object_id": self.object_id, "object_name": self.object_name }
        return json

    @classmethod
    def from_json_dict(cls, json_dict):
        return cls(json_dict['object_id'], json_dict['parent_type'], json_dict['parent_id'], json_dict['object_name'])
