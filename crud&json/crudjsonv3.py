import sys
import uuid
import json
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QTextEdit, QMessageBox,
    QCheckBox, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

DB_FILE = "lego_db.json"

class LegoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LEGO Men Manager")
        self.db = self.load_db()
        self.previous_db = json.loads(json.dumps(self.db))
        self.dark_mode = False
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # Top bar with search and theme toggle
        top_bar = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by name...")
        self.search_bar.textChanged.connect(self.refresh_view)
        top_bar.addWidget(QLabel("Search:"))
        top_bar.addWidget(self.search_bar)

        self.theme_toggle = QPushButton("Toggle Dark Mode")
        self.theme_toggle.clicked.connect(self.toggle_theme)
        top_bar.addWidget(self.theme_toggle)
        main_layout.addLayout(top_bar)

        # Main input and JSON layout
        mid_layout = QHBoxLayout()
        control_layout = QVBoxLayout()

        self.color_box = QComboBox()
        self.color_box.addItems(["red", "blue", "green", "yellow", "black"])
        control_layout.addWidget(QLabel("Color"))
        control_layout.addWidget(self.color_box)

        self.name_input = QLineEdit()
        control_layout.addWidget(QLabel("Name"))
        control_layout.addWidget(self.name_input)

        self.helmet_check = QCheckBox("Wears Helmet")
        control_layout.addWidget(self.helmet_check)

        self.weapon_input = QLineEdit()
        control_layout.addWidget(QLabel("Weapon"))
        control_layout.addWidget(self.weapon_input)

        self.rank_input = QLineEdit()
        control_layout.addWidget(QLabel("Rank"))
        control_layout.addWidget(self.rank_input)

        self.armor_input = QLineEdit()
        control_layout.addWidget(QLabel("Armor"))
        control_layout.addWidget(self.armor_input)

        self.jetpack_check = QCheckBox("Has Jetpack")
        control_layout.addWidget(self.jetpack_check)

        self.uuid_input = QLineEdit()
        control_layout.addWidget(QLabel("UUID (for update/delete)"))
        control_layout.addWidget(self.uuid_input)

        self.add_button = QPushButton("Create LEGO Man")
        self.add_button.clicked.connect(self.add_entry)
        control_layout.addWidget(self.add_button)

        self.update_button = QPushButton("Update")
        self.update_button.clicked.connect(self.update_entry)
        control_layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_entry)
        control_layout.addWidget(self.delete_button)

        control_layout.addStretch()
        mid_layout.addLayout(control_layout, 1)

        self.json_view = QTextEdit()
        self.json_view.setReadOnly(True)
        mid_layout.addWidget(self.json_view, 2)

        main_layout.addLayout(mid_layout)

        # Status label
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_label.setTextFormat(Qt.RichText)
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)
        for w in [self.name_input, self.weapon_input, self.rank_input, self.armor_input, self.uuid_input]:
            w.textChanged.connect(self.validate_form)
        self.helmet_check.stateChanged.connect(self.validate_form)
        self.jetpack_check.stateChanged.connect(self.validate_form)
        self.color_box.currentIndexChanged.connect(self.update_counts)

        self.validate_form()
        self.refresh_view()

    def load_db(self):
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def save_db(self):
        with open(DB_FILE, 'w') as f:
            json.dump(self.db, f, indent=4)

    def refresh_view(self):
        query = self.search_bar.text().strip().lower()
        filtered = {
            color: {
                uid: data for uid, data in entries.items()
                if query in data.get("name", "").lower()
            } for color, entries in self.db.items()
        } if query else self.db

        formatted = self.format_json_diff(filtered)
        self.json_view.setHtml(formatted)
        self.previous_db = json.loads(json.dumps(self.db))
        self.update_counts()

    def validate_form(self):
        uuid_present = bool(self.uuid_input.text().strip())
        other_filled = any([
            self.name_input.text().strip(),
            self.weapon_input.text().strip(),
            self.rank_input.text().strip(),
            self.armor_input.text().strip(),
            self.helmet_check.isChecked(),
            self.jetpack_check.isChecked()
        ])
        self.add_button.setEnabled(not uuid_present and other_filled)
        self.update_button.setEnabled(uuid_present)
        self.delete_button.setEnabled(uuid_present)

    def get_entry_data(self):
        return {
            "name": self.name_input.text(),
            "helmet": self.helmet_check.isChecked(),
            "weapon": self.weapon_input.text(),
            "rank": self.rank_input.text(),
            "armor": self.armor_input.text(),
            "has_jetpack": self.jetpack_check.isChecked()
        }

    def name_exists(self, name):
        for entries in self.db.values():
            for data in entries.values():
                if data.get("name", "").lower() == name.lower():
                    return True
        return False

    def add_entry(self):
        name = self.name_input.text().strip()
        if self.name_exists(name):
            QMessageBox.warning(self, "Duplicate Name", f"A LEGO man named '{name}' already exists.")
            return

        color = self.color_box.currentText()
        entry_id = str(uuid.uuid4())
        entry = self.get_entry_data()

        self.db.setdefault(color, {})[entry_id] = entry
        self.save_db()
        self.refresh_view()
        QMessageBox.information(self, "Added", f"LEGO Man created with UUID:\n{entry_id}")
        self.clear_form()

    def update_entry(self):
        color = self.color_box.currentText()
        entry_id = self.uuid_input.text().strip()
        if not entry_id:
            return

        if entry_id in self.db.get(color, {}):
            entry = self.db[color][entry_id]
            new_data = self.get_entry_data()
            for key, value in new_data.items():
                if isinstance(value, bool):
                    entry[key] = value
                elif value.strip():
                    entry[key] = value
            self.save_db()
            self.refresh_view()
            QMessageBox.information(self, "Updated", f"LEGO Man {entry_id} updated.")

    def delete_entry(self):
        color = self.color_box.currentText()
        entry_id = self.uuid_input.text().strip()
        if entry_id in self.db.get(color, {}):
            del self.db[color][entry_id]
            self.save_db()
            self.refresh_view()
            QMessageBox.information(self, "Deleted", f"LEGO Man {entry_id} deleted.")

    def clear_form(self):
        self.name_input.clear()
        self.weapon_input.clear()
        self.rank_input.clear()
        self.armor_input.clear()
        self.helmet_check.setChecked(False)
        self.jetpack_check.setChecked(False)
        self.uuid_input.clear()

    def format_json_diff(self, display_data):
        def escape(s):
            return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        html = ["<pre>"]
        for color, entries in display_data.items():
            html.append(f'"<span style=\"color:#888\">{color}</span>": {{')
            for uid, data in entries.items():
                html.append(f'  "<span style=\"color:orange\">{uid}</span>": {{')
                for k, v in data.items():
                    old = self.previous_db.get(color, {}).get(uid, {}).get(k, None)
                    changed = old != v
                    color_code = "red" if changed else "green"
                    val = "true" if v is True else "false" if v is False else escape(v)
                    html.append(f'    "<span style=\"color:#888\">{k}</span>": <span style=\"color:{color_code}\">"{val}"</span>,')
                html.append("  },")
            html.append("},")
        html.append("</pre>")
        return "\n".join(html)

    def update_counts(self):
        counts = {color: len(self.db.get(color, {})) for color in ["red", "blue", "green", "yellow", "black"]}
        parts = [f'<span style="color:{c}">{c}: {n}</span>' for c, n in counts.items()]
        self.status_label.setText(" | ".join(parts))

    def toggle_theme(self):
        palette = QPalette()
        if not self.dark_mode:
            palette.setColor(QPalette.Window, QColor("#121212"))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor("#2e2e2e"))
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor("#444"))
            palette.setColor(QPalette.ButtonText, Qt.white)
            self.setPalette(palette)
        else:
            self.setPalette(QApplication.palette())
        self.dark_mode = not self.dark_mode

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LegoApp()
    window.resize(1000, 600)
    window.show()
    sys.exit(app.exec())
