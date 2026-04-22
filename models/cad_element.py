from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CadElement:
    element_id: int
    name: str
    element_type: str
    vertex_count: int

    def __hash__(self) -> int:
        return hash(self.element_id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CadElement):
            return NotImplemented
        return self.element_id == other.element_id
