from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ObjectImage:
    start_address: int
    code: bytes
    symbols: dict[str, int]


def link_objects(objects: list[ObjectImage], image_size: int = 0x10000) -> bytes:
    image = bytearray(image_size)
    for obj in objects:
        end = obj.start_address + len(obj.code)
        if end > image_size:
            raise ValueError("Object exceeds image size")
        for offset, value in enumerate(obj.code):
            address = obj.start_address + offset
            image[address] = value
    return bytes(image)
