from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BuildingElement:
    id: int
    name: str

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, BuildingElement):
            return NotImplemented
        return self.id == other.id

    def __repr__(self):
        return f"BuildingElement(id={self.id}, name='{self.name}')"

    def __str__(self):
        return self.name
