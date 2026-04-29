"""Tests for the application service.

These tests run with no Qt and no cwapi3d
"""

from adapters.driven.fake_cadwork_adapter import FakeCadworkAdapter
from domain.building_element import BuildingElement
from domain.cadwork_service import CadworkService


class _RecordingPort:
    def __init__(self) -> None:
        self.activate_calls: list[int] = []

    def get_active_elements(self) -> list[BuildingElement]:
        return [BuildingElement(id=1, name="one")]

    def activate_and_zoom(self, element_id: int) -> None:
        self.activate_calls.append(element_id)


class _BoomPort:
    def get_active_elements(self) -> list[BuildingElement]:
        raise RuntimeError("ids-boom")

    def activate_and_zoom(self, element_id: int) -> None:
        raise RuntimeError("zoom-boom")


def test_get_active_elements_returns_fake_data():
    service = CadworkService(FakeCadworkAdapter())

    assert service.get_active_elements() == [
        BuildingElement(id=42, name="Beam-A"),
        BuildingElement(id=101, name="Column-B"),
        BuildingElement(id=256, name="Plate-C"),
    ]


def test_activate_and_zoom_dispatches_to_port():
    port = _RecordingPort()
    service = CadworkService(port)

    service.activate_and_zoom(42)

    assert port.activate_calls == [42]


def test_service_swallows_port_exceptions():
    service = CadworkService(_BoomPort())

    assert service.get_active_elements() == []
    service.activate_and_zoom(7)  # must not raise
