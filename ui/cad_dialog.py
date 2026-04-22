"""View — a QDialog that binds to CadViewModel.

The dialog has no business logic: it loads the layout from `cad_dialog.ui`,
forwards user actions to ViewModel commands, and reacts to ViewModel signals
by updating widgets. Swap the ViewModel for a different one and this class
does not need to change.
"""

from pathlib import Path

from PyQt6 import uic
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from models.cad_element import CadElement
from ui.cad_view_model import CadViewModel


_UI_FILE = Path(__file__).resolve().parent / "cad_dialog.ui"


class CadDialog(QDialog):
    # Widgets are injected by uic.loadUi; these annotations give the IDE
    # and type checker the types of those attributes without a codegen step.
    titleLabel: QLabel
    tableWidget: QTableWidget
    refreshButton: QPushButton

    def __init__(self, view_model: CadViewModel, parent: QWidget | None = None):
        super().__init__(parent)
        uic.loadUi(_UI_FILE, self)

        self._view_model = view_model
        self._elements: list[CadElement] = []

        self.tableWidget.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.tableWidget.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.refreshButton.clicked.connect(self._view_model.load_elements)
        self._view_model.elementsChanged.connect(self._render_table)
        self._view_model.loadingChanged.connect(self._on_loading_changed)
        self._view_model.errorOccurred.connect(self._show_error)
        self.tableWidget.itemSelectionChanged.connect(self._on_selection_changed)

        self._view_model.load_elements()

    def _render_table(self, elements: list[CadElement]) -> None:
        self._elements = list(elements)
        # block spurious activation to cadwork
        self.tableWidget.blockSignals(True)
        try:
            self.tableWidget.setRowCount(len(elements))
            for row, element in enumerate(elements):
                self.tableWidget.setItem(row, 0, QTableWidgetItem(element.name))
                self.tableWidget.setItem(row, 1, QTableWidgetItem(element.element_type))
                self.tableWidget.setItem(row, 2, QTableWidgetItem(str(element.vertex_count)))
        finally:
            self.tableWidget.blockSignals(False)

    def _on_selection_changed(self) -> None:
        selected_rows = sorted(
            {index.row() for index in self.tableWidget.selectedIndexes()}
        )
        element_ids = [self._elements[row].element_id for row in selected_rows]
        self._view_model.activate_elements(element_ids)

    def _on_loading_changed(self, is_loading: bool) -> None:
        self.refreshButton.setDisabled(is_loading)

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Operation failed", message)
