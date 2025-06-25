from __future__ import annotations

from dataclasses import dataclass

RawInput = int | float | str


@dataclass
class Dimension:
    width: int
    height: int


@dataclass
class Pos:
    row: int
    col: int

    @classmethod
    def of_tuple(cls, pos_tuple: tuple[int, int]) -> Pos:
        return Pos(row=pos_tuple[0], col=pos_tuple[1])
