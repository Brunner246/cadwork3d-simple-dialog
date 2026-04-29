from domain.building_element import BuildingElement


class FakeCadworkAdapter:
    def get_active_elements(self) -> list[BuildingElement]:
        elements = [
            BuildingElement(id=42, name="Beam-A"),
            BuildingElement(id=101, name="Column-B"),
            BuildingElement(id=256, name="Plate-C"),
        ]
        print(f"[fake cadwork] get_active_elements() -> {elements}")
        return elements

    def activate_and_zoom(self, element_id: int) -> None:
        print(f"[fake cadwork] activate_and_zoom({element_id})")
