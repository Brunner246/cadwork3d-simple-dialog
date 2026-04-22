"""Real cwapi3d adapter. Runs inside cadwork 3d.

This is the only file in the project that imports cwapi3d controllers.
The imports are deferred to the method bodies so this module can be
imported (and its class instantiated) in environments where cadwork is
not installed — e.g. CI, a dev laptop, pytest.
"""

from models.cad_element import CadElement


class CadworkElementService:
    def get_active_elements(self) -> list[CadElement]:
        import cadwork
        import element_controller as ec
        import attribute_controller as ac
        import geometry_controller as gc

        # The IDs of whatever the user currently has selected / active in cadwork.
        element_ids = ec.get_active_identifiable_element_ids()

        elements: list[CadElement] = []
        for element_id in element_ids:
            name = ac.get_name(element_id) or "Unnamed"
            element_type = ec.get_element_type_description(element_id) or "Unknown"
            vertex_count = len(gc.get_element_vertices(element_id))

            elements.append(CadElement(element_id, name, element_type, vertex_count))

        return elements

    def set_active_elements(self, element_ids: list[int]) -> None:
        import visualization_controller as vc

        vc.set_active(element_ids)
