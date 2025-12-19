import sys
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QVBoxLayout, QTableWidgetItem

# Model: holds data
class TableModel:
    def __init__(self):
        self._data = [
            ["Alice", 30],
            ["Bob", 25],
            ["Charlie", 35]
        ]
    
    def row_count(self):
        return len(self._data)
    
    def col_count(self):
        return len(self._data[0]) if self._data else 0
    
    def data(self, row, col):
        return self._data[row][col]
    
    def set_data(self, row, col, value):
        self._data[row][col] = value

# View: shows data using QTableWidget
class TableView(QWidget):
    def __init__(self):
        super().__init__()
        self.table = QTableWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)
    
    def set_row_count(self, count):
        self.table.setRowCount(count)
    
    def set_col_count(self, count):
        self.table.setColumnCount(count)
    
    def set_item(self, row, col, text):
        item = QTableWidgetItem(str(text))
        self.table.setItem(row, col, item)

# Presenter: connects model and view
class TablePresenter:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.load_data()
    
    def load_data(self):
        self.view.set_row_count(self.model.row_count())
        self.view.set_col_count(self.model.col_count())
        for row in range(self.model.row_count()):
            for col in range(self.model.col_count()):
                value = self.model.data(row, col)
                self.view.set_item(row, col, value)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    model = TableModel()
    view = TableView()
    presenter = TablePresenter(model, view)
    view.show()
    sys.exit(app.exec_())
