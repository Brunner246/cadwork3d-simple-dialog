"""The contract the ViewModel depends on.

This is the seam between the UI/ViewModel and whatever backend produces
elements. Any object that exposes these two methods structurally
satisfies the Protocol — no inheritance required. Concrete
implementations live in the `services/` layer.
"""

from typing import Protocol

from models.cad_element import CadElement


class ElementService(Protocol):
    def get_active_elements(self) -> list[CadElement]:
        ...

    def set_active_elements(self, element_ids: list[int]) -> None:
        ...
