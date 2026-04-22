"""ViewModel — the glue between the service layer and the View.

Holds all UI-facing state (`elements`, `is_loading`) and exposes it via
read-only properties plus Qt signals that the View binds to. The View
never touches the service directly, and this class never touches a Qt
widget — which is exactly what makes it unit-testable without a window.
"""

from PyQt6.QtCore import QObject, pyqtSignal

from models.cad_element import CadElement
from models.element_service import ElementService


class CadViewModel(QObject):
    elementsChanged = pyqtSignal(list)
    loadingChanged = pyqtSignal(bool)
    errorOccurred = pyqtSignal(str)

    def __init__(self, service: ElementService):
        super().__init__()
        self._service = service
        self._elements: list[CadElement] = []
        self._is_loading: bool = False

    @property
    def elements(self) -> list[CadElement]:
        return list(self._elements)

    @property
    def is_loading(self) -> bool:
        return self._is_loading

    def load_elements(self) -> None:
        self._set_loading(True)
        try:
            self._elements = self._service.get_active_elements()
        except Exception as exc:
            self.errorOccurred.emit(str(exc))
            return
        finally:
            self._set_loading(False)
        self.elementsChanged.emit(self._elements)

    def activate_elements(self, element_ids: list[int]) -> None:
        try:
            self._service.set_active_elements(element_ids)
        except Exception as exc:
            self.errorOccurred.emit(str(exc))

    def _set_loading(self, value: bool) -> None:
        if self._is_loading == value:
            return
        self._is_loading = value
        self.loadingChanged.emit(value)
