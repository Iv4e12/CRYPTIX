
import sys

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QFrame,
    QStackedWidget
)
from PySide6.QtGui import QShortcut, QKeySequence

from ui.hashing import HashingLab
from ui.encryption import EncryptionLab
from ui.password_lab import PasswordLab
from ui.cipher_lab import CipherLab
from ui.key_vault import KeyVault
from ui.history import HistoryLab
from ui.about import AboutWindow

class Cryptix(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CRYPTIX | Cryptography Workstation")
        self.resize(1150, 750)
        self.setMinimumSize(900, 600)

        self.setStyleSheet("""
            QMainWindow {
                background: #0b0b12;
            }

            QWidget {
                color: #e5e5ed;
                font-family: Inter, Arial;
                font-size: 13px;
            }

            QFrame#Sidebar {
                background: #10101a;
                border-right: 1px solid #242435;
            }

            QLabel#Brand {
                color: #c4a7ff;
                font-size: 25px;
                font-weight: bold;
                letter-spacing: 2px;
            }

            QLabel#Subtitle {
                color: #77778e;
                font-size: 10px;
                letter-spacing: 2px;
            }

            QPushButton {
                background: transparent;
                color: #9292a8;
                border: none;
                border-radius: 8px;
                padding: 12px;
                text-align: left;
            }

            QPushButton:hover {
                background: #1c1b2b;
                color: #e5e5ed;
            }

            QPushButton:checked {
                background: #29203e;
                color: #c4a7ff;
                font-weight: bold;
                border-left: 3px solid #a78bfa;
            }

            QFrame#Card {
                background: #141421;
                border: 1px solid #29293d;
                border-radius: 12px;
            }

            QLabel#CardTitle {
                color: #85859a;
                font-size: 11px;
                font-weight: bold;
            }

            QLabel#CardValue {
                color: #c4a7ff;
                font-size: 19px;
                font-weight: bold;
            }

            QLabel#Heading {
                font-size: 27px;
                font-weight: bold;
            }

            QLabel#Description {
                color: #85859a;
            }
        """)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(18, 28, 18, 20)
        sidebar_layout.setSpacing(8)

        brand = QLabel("CRYPTIX")
        brand.setObjectName("Brand")

        subtitle = QLabel("CRYPTOGRAPHY LAB")
        subtitle.setObjectName("Subtitle")

        sidebar_layout.addWidget(brand)
        sidebar_layout.addWidget(subtitle)
        sidebar_layout.addSpacing(35)

        self.stack = QStackedWidget()
        self.buttons = {}

        pages = [
            "Dashboard",
            "Encryption",
            "Hashing",
            "Password Lab",
            "Cipher Lab",
            "Key Vault",
            "History"
        ]

        self.stack.addWidget(self.dashboard())

        for name in pages[1:]:
            if name == "Hashing":
                self.stack.addWidget(HashingLab())
            elif name == "Encryption":
                self.stack.addWidget(EncryptionLab())
            elif name == "Password Lab":
                self.stack.addWidget(PasswordLab())
            elif name == "Cipher Lab":
                self.stack.addWidget(CipherLab())
            elif name == "Key Vault":
                self.stack.addWidget(KeyVault())
            elif name == "History":
                self.stack.addWidget(HistoryLab())

        for name in pages:
            button = QPushButton(name)
            button.setCheckable(True)
            button.clicked.connect(
                lambda checked=False, p=name: self.navigate(p)
            )

            sidebar_layout.addWidget(button)
            self.buttons[name] = button

        sidebar_layout.addStretch()

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)

        self.navigate("Dashboard")

        self.about_window = AboutWindow()

        self.about_shortcut = QShortcut(
            QKeySequence("Ctrl+H"), self
        )
        self.about_shortcut.activated.connect(
            self.show_about
        )

    def show_about(self):
        self.about_window.show()
        self.about_window.raise_()
        self.about_window.activateWindow()

    def dashboard(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(35, 30, 35, 30)
        layout.setSpacing(20)

        heading = QLabel("Dashboard")
        heading.setObjectName("Heading")

        description = QLabel(
            "Your cryptography workstation."
        )
        description.setObjectName("Description")

        layout.addWidget(heading)
        layout.addWidget(description)
        layout.addSpacing(15)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        cards = [
            ("ENCRYPTION", "AES-256-GCM"),
            ("HASH ENGINE", "SHA-256 / SHA-512"),
            ("PASSWORD LAB", "READY")
        ]

        for title, value in cards:
            card = QFrame()
            card.setObjectName("Card")

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(20, 20, 20, 20)

            title_label = QLabel(title)
            title_label.setObjectName("CardTitle")

            value_label = QLabel(value)
            value_label.setObjectName("CardValue")

            card_layout.addWidget(title_label)
            card_layout.addWidget(value_label)

            cards_layout.addWidget(card)

        layout.addLayout(cards_layout)
        layout.addSpacing(15)

        quick_title = QLabel("Quick Access")
        quick_title.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )
        layout.addWidget(quick_title)

        modules = [
            "Encryption",
            "Hashing",
            "Password Lab",
            "Cipher Lab"
        ]

        for module in modules:
            row = QHBoxLayout()

            label = QLabel(module)
            label.setStyleSheet("font-size: 14px;")

            open_button = QPushButton("OPEN")
            open_button.setFixedWidth(100)
            open_button.clicked.connect(
                lambda checked=False, p=module: self.navigate(p)
            )

            row.addWidget(label)
            row.addStretch()
            row.addWidget(open_button)

            layout.addLayout(row)

        layout.addStretch()

        return page

    def navigate(self, page):
        pages = [
            "Dashboard",
            "Encryption",
            "Hashing",
            "Password Lab",
            "Cipher Lab",
            "Key Vault",
            "History"
        ]

        index = pages.index(page)
        self.stack.setCurrentIndex(index)

        for name, button in self.buttons.items():
            button.setChecked(name == page)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = Cryptix()
    window.show()

    sys.exit(app.exec())
