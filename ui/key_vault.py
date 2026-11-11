
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTextEdit, QListWidget,
    QListWidgetItem, QMessageBox, QDialog,
    QFormLayout, QApplication
)
from PySide6.QtCore import Qt

from core import vault, history


class AddEntryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add Vault Entry")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.title_input = QLineEdit()
        self.username_input = QLineEdit()
        self.secret_input = QLineEdit()
        self.secret_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(90)

        form.addRow("Title:", self.title_input)
        form.addRow("Username:", self.username_input)
        form.addRow("Password / Secret:", self.secret_input)
        form.addRow("Notes:", self.notes_input)

        layout.addLayout(form)

        buttons = QHBoxLayout()

        save_button = QPushButton("SAVE ENTRY")
        cancel_button = QPushButton("CANCEL")

        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        buttons.addWidget(save_button)
        buttons.addWidget(cancel_button)

        layout.addLayout(buttons)

    def get_data(self):
        return (
            self.title_input.text(),
            self.username_input.text(),
            self.secret_input.text(),
            self.notes_input.toPlainText()
        )


class KeyVault(QWidget):
    def __init__(self):
        super().__init__()

        self.key = None
        self.entries = []

        self.setStyleSheet("""
            QWidget {
                color: #e5e5ed;
            }

            QLineEdit, QTextEdit, QListWidget {
                background: #141421;
                border: 1px solid #29293d;
                border-radius: 8px;
                padding: 10px;
                color: #eeeeff;
            }

            QPushButton {
                background: #29203e;
                color: #c4a7ff;
                border: 1px solid #49366b;
                border-radius: 7px;
                padding: 10px 16px;
            }

            QPushButton:hover {
                background: #3a2a55;
            }
        """)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(35, 30, 35, 30)
        self.main_layout.setSpacing(15)

        self.show_locked_screen()

    def clear_layout(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)

            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def show_locked_screen(self):
        self.clear_layout()

        title = QLabel("Key Vault")
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        description = QLabel(
            "Your locally encrypted credential storage."
        )
        description.setStyleSheet("color: #85859a;")

        self.main_layout.addWidget(title)
        self.main_layout.addWidget(description)
        self.main_layout.addSpacing(20)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )
        self.password_input.setPlaceholderText(
            "Enter master password..."
        )

        self.main_layout.addWidget(
            QLabel("MASTER PASSWORD")
        )
        self.main_layout.addWidget(self.password_input)

        if vault.vault_exists():
            button = QPushButton("UNLOCK VAULT")
            button.clicked.connect(self.unlock)
            self.main_layout.addWidget(button)
        else:
            button = QPushButton("CREATE VAULT")
            button.clicked.connect(self.create)
            self.main_layout.addWidget(button)

        self.status = QLabel("")
        self.status.setStyleSheet("color: #a78bfa;")
        self.main_layout.addWidget(self.status)

        self.main_layout.addStretch()

    def create(self):
        password = self.password_input.text()

        try:
            self.key = vault.create_vault(password)
            history.add_record(
                "Key Vault",
                "Created vault"
            )
            self.show_unlocked_screen()
        except Exception as error:
            self.status.setText(str(error))

    def unlock(self):
        password = self.password_input.text()

        try:
            self.key = vault.unlock_vault(password)
            history.add_record(
                "Key Vault",
                "Unlocked vault"
            )
            self.show_unlocked_screen()
        except Exception as error:
            self.status.setText(str(error))

    def show_unlocked_screen(self):
        self.clear_layout()

        heading = QHBoxLayout()

        title = QLabel("Key Vault")
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        lock_button = QPushButton("LOCK")
        lock_button.clicked.connect(self.lock)

        heading.addWidget(title)
        heading.addStretch()
        heading.addWidget(lock_button)

        self.main_layout.addLayout(heading)

        description = QLabel(
            "Your encrypted entries."
        )
        description.setStyleSheet("color: #85859a;")
        self.main_layout.addWidget(description)

        self.entry_list = QListWidget()
        self.entry_list.currentRowChanged.connect(
            self.show_entry
        )
        self.main_layout.addWidget(self.entry_list)

        self.details = QLabel(
            "Select an entry to view its details."
        )
        self.details.setWordWrap(True)
        self.details.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.details.setStyleSheet(
            "background: #141421; padding: 15px; "
            "border-radius: 8px; color: #b8b8ca;"
        )
        self.main_layout.addWidget(self.details)

        buttons = QHBoxLayout()

        add_button = QPushButton("ADD ENTRY")
        add_button.clicked.connect(self.add_entry)

        copy_button = QPushButton("COPY SECRET")
        copy_button.clicked.connect(self.copy_secret)

        delete_button = QPushButton("DELETE")
        delete_button.clicked.connect(self.delete_selected)

        buttons.addWidget(add_button)
        buttons.addWidget(copy_button)
        buttons.addWidget(delete_button)

        self.main_layout.addLayout(buttons)

        self.refresh_entries()

    def refresh_entries(self):
        self.entries = vault.get_entries(self.key)

        self.entry_list.clear()

        for entry in self.entries:
            item = QListWidgetItem(entry["title"])
            self.entry_list.addItem(item)

        self.details.setText(
            "Select an entry to view its details."
        )

    def show_entry(self, index):
        if index < 0 or index >= len(self.entries):
            self.details.setText(
                "Select an entry to view its details."
            )
            return

        entry = self.entries[index]

        self.details.setText(
            f"Title: {entry['title']}\n"
            f"Username: {entry['username']}\n"
            f"Password / Secret: {entry['secret']}\n"
            f"Notes: {entry['notes']}"
        )

    def add_entry(self):
        dialog = AddEntryDialog(self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        title, username, secret, notes = dialog.get_data()

        try:
            vault.add_entry(
                self.key, title, username, secret, notes
            )
            history.add_record(
                "Key Vault",
                "Added an entry"
            )
            self.refresh_entries()
        except Exception as error:
            QMessageBox.warning(self, "Error", str(error))

    def copy_secret(self):
        index = self.entry_list.currentRow()

        if index < 0 or index >= len(self.entries):
            return

        QApplication.clipboard().setText(
            self.entries[index]["secret"]
        )

        QMessageBox.information(
            self, "Copied", "Secret copied to clipboard."
        )

    def delete_selected(self):
        index = self.entry_list.currentRow()

        if index < 0 or index >= len(self.entries):
            return

        entry = self.entries[index]

        answer = QMessageBox.question(
            self,
            "Delete Entry",
            f"Delete '{entry['title']}'?"
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        vault.delete_entry(entry["id"])

        history.add_record(
            "Key Vault",
            "Deleted an entry"
        )

        self.refresh_entries()

    def lock(self):
        self.key = None
        self.entries = []
        self.show_locked_screen()
