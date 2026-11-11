from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt


class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("About CRYPTIX")
        self.setFixedSize(480, 440)

        self.setStyleSheet("""
            QWidget {
                background: #0b0b12;
                color: #e5e5ed;
                font-family: Inter, Arial;
            }

            QLabel#Title {
                color: #c4a7ff;
                font-size: 28px;
                font-weight: bold;
            }

            QLabel#Section {
                color: #c4a7ff;
                font-size: 13px;
                font-weight: bold;
            }

            QLabel#Text {
                color: #a0a0b5;
                font-size: 12px;
            }

            QPushButton {
                background: #29203e;
                color: #c4a7ff;
                border: 1px solid #49366b;
                border-radius: 7px;
                padding: 9px;
            }

            QPushButton:hover {
                background: #3a2a55;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(12)

        title = QLabel("CRYPTIX")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Cryptography Workstation")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setObjectName("Text")
        layout.addWidget(subtitle)

        layout.addSpacing(12)

        def section(name, content):
            heading = QLabel(name)
            heading.setObjectName("Section")

            text = QLabel(content)
            text.setObjectName("Text")
            text.setWordWrap(True)

            layout.addWidget(heading)
            layout.addWidget(text)

        section(
            "ABOUT",
            "CRYPTIX is a desktop cryptography workstation "
            "with encryption, hashing, password generation "
            "and other cryptographic tools."
        )

        section(
            "BUILT WITH",
            "Python • PySide6 • Cryptography • SQLite • PyQtGraph"
        )

        section(
            "MADE FOR",
            "Hack Club — Hack Cast"
        )

        section(
            "THANK YOU",
            "Thank you for checking out my project!"
        )

        layout.addStretch()

        close_button = QPushButton("CLOSE")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
