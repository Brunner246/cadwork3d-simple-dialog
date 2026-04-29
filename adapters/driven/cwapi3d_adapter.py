from domain.building_element import BuildingElement


class Cwapi3dAdapter:
    def get_active_elements(self) -> list[BuildingElement]:
        import attribute_controller as ac
        import element_controller as ec

        return [
            BuildingElement(id=int(eid), name=ac.get_name(eid))
            for eid in ec.get_active_identifiable_element_ids()
        ]

    def activate_and_zoom(self, element_id: int) -> None:
        import element_controller as ec
        import visualization_controller as vc

        if element_id <= 0:
            print(f"Invalid element id: {element_id}")
            return

        vc.set_inactive(ec.get_active_identifiable_element_ids())
        vc.set_active([element_id])
        vc.zoom_active_elements()
