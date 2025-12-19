import sys
import uuid
from datetime import datetime, date
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTableWidget, QVBoxLayout, QHBoxLayout,
    QTableWidgetItem, QPushButton, QMessageBox
)
from PyQt5.QtCore import pyqtSignal, Qt


def calculate_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


class TableModel:
    def __init__(self):
        self._data = [
            {
                "uuid": str(uuid.uuid4()),
                "name": "Alice",
                "dob": date(1990, 5, 1),
                "updated": datetime.now()
            },
            {
                "uuid": str(uuid.uuid4()),
                "name": "Bob",
                "dob": date(1985, 11, 20),
                "updated": datetime.now()
            }
        ]

    def row_count(self):
        return len(self._data)

    def col_count(self):
        return 5  # uuid, name, dob, age, updated

    def data(self, row, col):
        row_data = self._data[row]
        if col == 0:
            return row_data["uuid"]
        elif col == 1:
            return row_data["name"]
        elif col == 2:
            return row_data["dob"].strftime("%Y-%m-%d")
        elif col == 3:
            return calculate_age(row_data["dob"])
        elif col == 4:
            return row_data["updated"].strftime("%Y-%m-%d %H:%M:%S")

    def set_data(self, row, col, value):
        if col not in (1, 2):  # only name and dob editable
            return
        if col == 1:
            self._data[row]["name"] = value
        elif col == 2:
            try:
                dob = datetime.strptime(value, "%Y-%m-%d").date()
                self._data[row]["dob"] = dob
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD.")
        self._data[row]["updated"] = datetime.now()

    def add_row(self):
        self._data.append({
            "uuid": str(uuid.uuid4()),
            "name": "New Name",
            "dob": date(2000, 1, 1),
            "updated": datetime.now()
        })

    def remove_row(self, row):
        if 0 <= row < self.row_count():
            del self._data[row]

    def get_all_data(self):
        return [
            {
                "uuid": row["uuid"],
                "name": row["name"],
                "dob": row["dob"].strftime("%Y-%m-%d"),
                "age": calculate_age(row["dob"]),
                "updated": row["updated"].strftime("%Y-%m-%d %H:%M:%S")
            }
            for row in self._data
        ]


class TableView(QWidget):
    cell_edited = pyqtSignal(int, int, object)
    add_row_clicked = pyqtSignal()
    remove_row_clicked = pyqtSignal()
    print_data_clicked = pyqtSignal()
    sort_by_name_clicked = pyqtSignal()
    sort_by_age_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.table = QTableWidget()
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setSelectionMode(self.table.SingleSelection)

        btn_add = QPushButton("Add Row")
        btn_remove = QPushButton("Remove Selected Row")
        btn_print = QPushButton("Print Model Data")
        btn_sort_name = QPushButton("Sort by Name")
        btn_sort_age = QPushButton("Sort by Age")

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        btn_layout.addWidget(btn_print)
        btn_layout.addWidget(btn_sort_name)
        btn_layout.addWidget(btn_sort_age)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.table.itemChanged.connect(self._on_item_changed)

        btn_add.clicked.connect(lambda: self.add_row_clicked.emit())
        btn_remove.clicked.connect(lambda: self.remove_row_clicked.emit())
        btn_print.clicked.connect(lambda: self.print_data_clicked.emit())
        btn_sort_name.clicked.connect(lambda: self.sort_by_name_clicked.emit())
        btn_sort_age.clicked.connect(lambda: self.sort_by_age_clicked.emit())

        self._updating = False

    def set_row_count(self, count):
        self.table.setRowCount(count)

    def set_col_count(self, count):
        self.table.setColumnCount(count)

    def set_horizontal_headers(self, headers):
        self.table.setHorizontalHeaderLabels(headers)

    def set_item(self, row, col, text, editable=True):
        self._updating = True
        item = QTableWidgetItem(str(text))
        flags = item.flags()
        item.setFlags(flags | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        if editable:
            item.setFlags(flags | Qt.ItemIsEditable)
        else:
            item.setFlags(flags & ~Qt.ItemIsEditable)
        self.table.setItem(row, col, item)
        self._updating = False

    def _on_item_changed(self, item):
        if self._updating:
            return
        row = item.row()
        col = item.column()
        new_value = item.text()
        self.cell_edited.emit(row, col, new_value)

    def get_selected_row(self):
        selected = self.table.selectionModel().selectedRows()
        if selected:
            return selected[0].row()
        return None


class TablePresenter:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.view.cell_edited.connect(self.update_model)
        self.view.add_row_clicked.connect(self.add_row)
        self.view.remove_row_clicked.connect(self.remove_row)
        self.view.print_data_clicked.connect(self.print_model_data)
        self.view.sort_by_name_clicked.connect(self.sort_by_name)
        self.view.sort_by_age_clicked.connect(self.sort_by_age)

        self.load_data()

    def load_data(self):
        self.view.set_row_count(self.model.row_count())
        self.view.set_col_count(self.model.col_count())
        headers = ["UUID", "Name", "DOB", "Age", "Last Updated"]
        self.view.set_horizontal_headers(headers)

        for row in range(self.model.row_count()):
            for col in range(self.model.col_count()):
                editable = col in (1, 2)  # Only name and dob editable
                val = self.model.data(row, col)
                self.view.set_item(row, col, val, editable)

    def update_model(self, row, col, value):
        try:
            self.model.set_data(row, col, value)
        except ValueError as e:
            QMessageBox.warning(self.view, "Invalid input", str(e))
            self.load_data()
            return
        self.load_data()

    def add_row(self):
        self.model.add_row()
        self.load_data()

    def remove_row(self):
        row = self.view.get_selected_row()
        if row is None:
            QMessageBox.information(self.view, "Remove Row", "Please select a row to remove.")
            return
        self.model.remove_row(row)
        self.load_data()

    def print_model_data(self):
        data = self.model.get_all_data()
        print("Current model data:")
        for row in data:
            print(row)

    def sort_by_name(self):
        self.model._data.sort(key=lambda x: x["name"].lower())
        self.load_data()

    def sort_by_age(self):
        self.model._data.sort(key=lambda x: calculate_age(x["dob"]))
        self.load_data()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    model = TableModel()
    view = TableView()
    presenter = TablePresenter(model, view)
    view.setWindowTitle("MVP Table - DOB & Age Example with Sorting")
    view.resize(800, 400)
    view.show()
    sys.exit(app.exec_())
