from typing import Protocol

from domain.building_element import BuildingElement


class CadworkPort(Protocol):
    def get_active_elements(self) -> list[BuildingElement]: ...

    def activate_and_zoom(self, element_id: int) -> None: ...
