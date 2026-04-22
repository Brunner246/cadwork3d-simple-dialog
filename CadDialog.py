"""Entry points for the CadDialog example.

Two entry paths are provided because cwapi3d plugins typically run in
two contexts:

- Inside cadwork 3d, which already owns the Qt event loop. The plugin
  just constructs the dialog and calls `show()` — no QApplication, no
  `exec()`. Use `run_plugin()` for this.

- On a laptop with no cadwork installed. Here we create a
  QApplication, wire a FakeElementService, and run `exec()` so the
  dialog stays open.
"""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.sip import voidptr

current_dir = Path(__file__).resolve().parent.absolute()
services_dir = current_dir / "services"
models_dir = current_dir / "models"
ui_dir = current_dir / "ui"

sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(services_dir))
sys.path.insert(0, str(models_dir))
sys.path.insert(0, str(ui_dir))

from ui.cad_dialog import CadDialog
from ui.cad_view_model import CadViewModel
from services.cadwork_element_service import CadworkElementService
from services.fake_element_service import FakeElementService


def run_plugin(parent: QWidget | None = None) -> CadDialog:
    """Construct and show the dialog inside cadwork 3d."""
    service = CadworkElementService()
    view_model = CadViewModel(service)
    dialog = CadDialog(view_model, parent)
    dialog.show()
    return dialog


def _run_standalone() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    service = FakeElementService()
    view_model = CadViewModel(service)
    dialog = CadDialog(view_model)
    dialog.show()
    return app.exec()


if __name__ == "__main__":
    # sys.exit(_run_standalone())

    import utility_controller as uc
    hwnd_cadwork = uc.get_3d_hwnd()
    parent = QWidget.find(voidptr(hwnd_cadwork))
    dialog = run_plugin(parent)

    
