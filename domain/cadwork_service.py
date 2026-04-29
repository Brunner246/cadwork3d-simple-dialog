from domain.building_element import BuildingElement
from domain.cadwork_port import CadworkPort


class CadworkService:
    def __init__(self, port: CadworkPort) -> None:
        self._port = port

    def get_active_elements(self) -> list[BuildingElement]:
        try:
            return list(self._port.get_active_elements())
        except Exception as exc:
            print(f"[service] get_active_elements failed: {exc}")
            return []

    def activate_and_zoom(self, element_id: int) -> None:
        try:
            self._port.activate_and_zoom(element_id)
        except Exception as exc:
            print(f"[service] activate_and_zoom({element_id}) failed: {exc}")
