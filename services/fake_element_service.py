"""Deterministic stand-in for standalone runs and unit tests.

Satisfies `ElementService` structurally (no inheritance needed).
`activated_ids` records the last list passed to `set_active_elements`,
which lets tests assert that the View/ViewModel pushed the right IDs
downstream.
"""

from models.cad_element import CadElement


class FakeElementService:
    def __init__(self) -> None:
        self.activated_ids: list[int] = []

    def get_active_elements(self) -> list[CadElement]:
        return [
            CadElement(101, "Wall-01", "Beam", 8),
            CadElement(102, "Floor-Panel-A", "Panel", 12),
            CadElement(103, "Column-North", "Beam", 8),
        ]

    def set_active_elements(self, element_ids: list[int]) -> None:
        self.activated_ids = list(element_ids)
