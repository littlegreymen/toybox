import sys
import uuid
import json
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QTextEdit, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt


DB_FILE = "lego_db.json"


class LegoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LEGO Men Manager")
        self.db = self.load_db()
        self.previous_db = json.loads(json.dumps(self.db))  # Deep copy
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()
        control_layout = QVBoxLayout()

        # Color selector
        self.color_box = QComboBox()
        self.color_box.addItems(["red", "blue", "green", "yellow", "black"])
        control_layout.addWidget(QLabel("Color"))
        control_layout.addWidget(self.color_box)

        # Name input
        self.name_input = QLineEdit()
        control_layout.addWidget(QLabel("Name"))
        control_layout.addWidget(self.name_input)

        # Helmet checkbox
        self.helmet_check = QCheckBox("Wears Helmet")
        control_layout.addWidget(self.helmet_check)

        # Weapon input
        self.weapon_input = QLineEdit()
        control_layout.addWidget(QLabel("Weapon"))
        control_layout.addWidget(self.weapon_input)

        # Rank input
        self.rank_input = QLineEdit()
        control_layout.addWidget(QLabel("Rank"))
        control_layout.addWidget(self.rank_input)

        # Armor input
        self.armor_input = QLineEdit()
        control_layout.addWidget(QLabel("Armor"))
        control_layout.addWidget(self.armor_input)

        # Jetpack checkbox
        self.jetpack_check = QCheckBox("Has Jetpack")
        control_layout.addWidget(self.jetpack_check)

        # UUID input
        self.uuid_input = QLineEdit()
        control_layout.addWidget(QLabel("UUID (for update/delete)"))
        control_layout.addWidget(self.uuid_input)

        # Buttons
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

        # JSON display
        self.json_view = QTextEdit()
        self.json_view.setReadOnly(True)

        layout.addLayout(control_layout, 1)
        layout.addWidget(self.json_view, 2)
        self.setLayout(layout)

        # Validate button states on form input
        for widget in [
            self.name_input, self.weapon_input, self.rank_input,
            self.armor_input, self.uuid_input
        ]:
            widget.textChanged.connect(self.validate_form)

        self.helmet_check.stateChanged.connect(self.validate_form)
        self.jetpack_check.stateChanged.connect(self.validate_form)

        self.validate_form()
        self.refresh_view()

    def load_db(self):
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    QMessageBox.critical(self, "Error", "Failed to parse JSON file.")
                    return {}
        return {}

    def save_db(self):
        with open(DB_FILE, 'w') as f:
            json.dump(self.db, f, indent=4)

    def refresh_view(self):
        formatted = self.format_json_diff()
        self.json_view.setHtml(formatted)
        self.previous_db = json.loads(json.dumps(self.db))  # deep copy

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

    def add_entry(self):
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
            QMessageBox.warning(self, "Missing UUID", "Please enter a UUID to update.")
            return

        if entry_id in self.db.get(color, {}):
            existing = self.db[color][entry_id]
            new_data = self.get_entry_data()

            for key, value in new_data.items():
                if isinstance(value, bool):
                    existing[key] = value
                elif isinstance(value, str) and value.strip() != "":
                    existing[key] = value  # only update if non-empty string

            self.save_db()
            self.refresh_view()
            QMessageBox.information(self, "Updated", f"LEGO Man {entry_id} updated.")
        else:
            QMessageBox.warning(self, "Update Failed", f"No entry with UUID {entry_id} in {color} section.")

    def delete_entry(self):
        color = self.color_box.currentText()
        entry_id = self.uuid_input.text().strip()

        if not entry_id:
            QMessageBox.warning(self, "Missing UUID", "Please enter a UUID to delete.")
            return

        if entry_id in self.db.get(color, {}):
            del self.db[color][entry_id]
            self.save_db()
            self.refresh_view()
            QMessageBox.information(self, "Deleted", f"LEGO Man {entry_id} deleted.")
        else:
            QMessageBox.warning(self, "Delete Failed", f"No entry with UUID {entry_id} in {color} section.")

    def clear_form(self):
        self.name_input.clear()
        self.weapon_input.clear()
        self.rank_input.clear()
        self.armor_input.clear()
        self.helmet_check.setChecked(False)
        self.jetpack_check.setChecked(False)
        self.uuid_input.clear()

    def format_json_diff(self):
        def html_escape(text):
            return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        output = ["<pre>"]
        for color, entries in self.db.items():
            output.append(f'"<span style="color:#888">{color}</span>": {{')
            for uuid_key, fields in entries.items():
                output.append(f'  "<span style="color:orange">{uuid_key}</span>": {{')

                old_fields = self.previous_db.get(color, {}).get(uuid_key, {})

                for k, v in fields.items():
                    old_exists = k in old_fields
                    old_v = old_fields.get(k, None)

                    if isinstance(v, bool):
                        v_str = "true" if v else "false"
                    else:
                        v_str = str(v)

                    v_html = html_escape(v_str)

                    if not old_exists:
                        color_code = "green"
                    elif old_v != v:
                        color_code = "red"
                    else:
                        color_code = "green"

                    output.append(
                        f'    "<span style="color:#888">{k}</span>": '
                        f'<span style="color:{color_code}">"{v_html}"</span>,'
                    )

                output.append("  },")
            output.append("},")
        output.append("</pre>")
        return "\n".join(output)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LegoApp()
    window.resize(1000, 600)
    window.show()
    sys.exit(app.exec())
