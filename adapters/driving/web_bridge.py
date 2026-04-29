"""Driving adapter -- QObject exposed to JavaScript via QWebChannel.

Each `pyqtSlot` translates a JavaScript call into a `CadworkService`
method. Slots with `result="QVariant"` are awaitable from JS:

    const elements = await cadwork.getActiveElements();

Plain slots are fire-and-forget:

    cadwork.activateAndZoom(42);
"""

from PyQt6.QtCore import QObject, pyqtSlot

from domain.cadwork_service import CadworkService


class WebBridge(QObject):
    def __init__(self, service: CadworkService, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._service = service

    @pyqtSlot(result="QVariant")
    def getActiveElements(self) -> list[dict]:
        return [
            {"id": el.id, "name": el.name}
            for el in self._service.get_active_elements()
        ]

    # qint64 => cadwork element IDs are 64-bit.
    @pyqtSlot("qint64")
    def activateAndZoom(self, element_id: int) -> None:
        self._service.activate_and_zoom(element_id)
