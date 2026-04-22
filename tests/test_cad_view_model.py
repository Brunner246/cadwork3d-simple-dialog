"""Tests for CadViewModel.

These tests demonstrate the payoff of the MVVM split: the ViewModel is
exercised and asserted with no Qt widgets and no cadwork 3d — only a
fake service that implements the ElementService Protocol.
"""

from models.cad_element import CadElement
from ui.cad_view_model import CadViewModel
from services.fake_element_service import FakeElementService


class _BrokenService:
    def get_active_elements(self) -> list[CadElement]:
        raise RuntimeError("boom")

    def set_active_elements(self, element_ids: list[int]) -> None:
        raise RuntimeError(f"activate-boom ({len(element_ids)})")


def test_load_elements_populates_state(qtbot):
    vm = CadViewModel(FakeElementService())

    vm.load_elements()

    assert vm.elements == FakeElementService().get_active_elements()
    assert vm.is_loading is False


def test_load_elements_emits_elements_changed(qtbot):
    vm = CadViewModel(FakeElementService())

    with qtbot.waitSignal(vm.elementsChanged, timeout=1000) as blocker:
        vm.load_elements()

    emitted_elements = blocker.args[0]
    assert len(emitted_elements) == 3
    assert emitted_elements[0].name == "Wall-01"


def test_service_error_emits_error_signal_and_clears_loading(qtbot):
    vm = CadViewModel(_BrokenService())

    with qtbot.waitSignal(vm.errorOccurred, timeout=1000) as blocker:
        vm.load_elements()

    assert blocker.args[0] == "boom"
    assert vm.is_loading is False
    assert vm.elements == []


def test_activate_elements_pushes_ids_to_service():
    service = FakeElementService()
    vm = CadViewModel(service)

    vm.activate_elements([101, 103])

    assert service.activated_ids == [101, 103]


def test_activate_elements_error_emits_error_signal(qtbot):
    vm = CadViewModel(_BrokenService())

    with qtbot.waitSignal(vm.errorOccurred, timeout=1000) as blocker:
        vm.activate_elements([1, 2])

    assert blocker.args[0] == "activate-boom (2)"
