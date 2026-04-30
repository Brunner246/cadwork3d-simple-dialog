"""Driving adapter -- QDockWidget hosting the QWebEngineView and bridge.
"""

import os
from pathlib import Path

from PyQt6.QtCore import QFile, QIODevice, Qt, QUrl
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWebEngineCore import QWebEngineScript
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QDockWidget, QWidget

from adapters.driving.web_bridge import WebBridge

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_REACT_INDEX = _PROJECT_ROOT / "web" / "dist" / "index.html"
_INDEX = _PROJECT_ROOT / "assets" / "index.html"


def _resolve_ui_url() -> QUrl:
    """Pick which UI to load.

    `CADWORK_UI` selects the source:
        - http(s):// URL  -> loaded directly (e.g. `http://127.0.0.1:5173/`,
                             the Vite dev server with HMR)
        - unset / anything else -> web/dist/index.html, the React bundle
                             produced by `npm run build`
    """
    ui = os.environ.get("CADWORK_UI", "").strip()
    if ui.startswith(("http://", "https://")):
        return QUrl(ui)
    # if not _REACT_INDEX.is_file(): ...
    #     raise FileNotFoundError(
    #         f"{_REACT_INDEX} is missing -- run "
    #         f"`npm install && npm run build` inside the web/ directory, "
    #         f"or set CADWORK_UI to the dev server URL "
    #         f"(e.g. http://127.0.0.1:5173/)."
    #     )
    # return QUrl.fromLocalFile(_REACT_INDEX)
    if not _INDEX.is_file():
        raise FileNotFoundError(
            f"{_INDEX} is missing -- run `npm install` inside the project root."
        )
    return QUrl.fromLocalFile(str(_INDEX))


class WebDockWidget(QDockWidget):
    def __init__(self, bridge: WebBridge, parent: QWidget | None = None) -> None:
        super().__init__("Cadwork WebView", parent)
        self.setObjectName("CadworkWebDockWidget")
        self.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )

        bridge.setParent(self)
        self._view = QWebEngineView(self)
        self._channel = QWebChannel(self)
        self._channel.registerObject("cadwork", bridge)
        self._view.page().setWebChannel(self._channel)
        self._inject_qwebchannel_js()

        self.setWidget(self._view)
        self.resize(720, 480)

        self._view.load(_resolve_ui_url())

    def _inject_qwebchannel_js(self) -> None:
        qfile = QFile(":/qtwebchannel/qwebchannel.js")
        if not qfile.open(QIODevice.OpenModeFlag.ReadOnly):
            raise RuntimeError("qwebchannel.js resource not found")
        try:
            source = bytes(qfile.readAll()).decode("utf-8")
        finally:
            qfile.close()

        script = QWebEngineScript()
        script.setName("qwebchannel")
        script.setSourceCode(source)
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
        script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        script.setRunsOnSubFrames(False)
        self._view.page().scripts().insert(script)
