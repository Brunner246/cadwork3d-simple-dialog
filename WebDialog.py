"""Composition root

Run inside cadwork 3d:
    from WebDialog import run_plugin
    dialog = run_plugin()

Run standalone (no cadwork installed):
    uv run python WebDialog.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent
_ADAPTERS = _PROJECT_ROOT / "adapters"
_DOMAIN = _PROJECT_ROOT / "domain"
_ASSETS = _PROJECT_ROOT / "assets"
_VENV_SITE_PACKAGES = _PROJECT_ROOT / ".venv" / "Lib" / "site-packages"

print(f"_Project_ROOT: {_PROJECT_ROOT}")
print(f"_VENV_SITE_PACKAGES: {_VENV_SITE_PACKAGES}")


def _prepend_sys_path(path: Path) -> None:
    s = str(path)
    if path.is_dir() and s not in sys.path:
        sys.path.insert(0, s)


def _bootstrap_paths() -> None:
    _prepend_sys_path(_PROJECT_ROOT)
    _prepend_sys_path(_DOMAIN)
    _prepend_sys_path(_ADAPTERS)
    _prepend_sys_path(_ASSETS)
    _prepend_sys_path(_VENV_SITE_PACKAGES)

_bootstrap_paths()

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.sip import voidptr

from adapters.driving.web_bridge import WebBridge
from adapters.driving.web_dialog import WebDockWidget
from domain.cadwork_port import CadworkPort
from domain.cadwork_service import CadworkService


def _select_cadwork_port() -> CadworkPort:
    """Pick the production adapter when cadwork is available, else the fake."""
    try:
        import utility_controller  # noqa: F401 -- presence probe only
    except ImportError:
        from adapters.driven.fake_cadwork_adapter import FakeCadworkAdapter

        return FakeCadworkAdapter()
    from adapters.driven.cwapi3d_adapter import Cwapi3dAdapter

    return Cwapi3dAdapter()


def _build_dock(port: CadworkPort, parent: QWidget | None = None) -> WebDockWidget:
    service = CadworkService(port)
    bridge = WebBridge(service)
    return WebDockWidget(bridge, parent)


def _find_main_window(widget: QWidget | None) -> QMainWindow | None:
    while widget is not None:
        if isinstance(widget, QMainWindow):
            return widget
        widget = widget.parentWidget()
    return None


def run_plugin(parent: QWidget | None = None) -> WebDockWidget:
    """Dock into the host QMainWindow if one is reachable, else show floating."""
    dock = _build_dock(_select_cadwork_port(), parent)
    host = _find_main_window(parent)
    if host is not None:
        host.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
    dock.show()
    return dock


def _run_standalone() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    host = QMainWindow()
    host.setWindowTitle("Cadwork WebView (standalone)")
    host.resize(960, 600)
    host.setCentralWidget(QWidget(host))
    dock = _build_dock(_select_cadwork_port(), host)
    host.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
    host.show()
    return app.exec()


if __name__ == "__main__":
    try:
        print("Running inside cadwork 3d, attempting to import utility_controller...")
        import utility_controller as uc

        # if you want to use the REACT UI, remove the comment below
        # os.environ["CADWORK_UI"] = str('http://127.0.0.1:5173/')

        parent = QWidget.find(voidptr(uc.get_3d_hwnd()))
        run_plugin(parent)
    except ImportError:
        sys.exit(_run_standalone())
