
import math
import secrets
import string

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QSlider, QCheckBox,
    QFrame, QApplication
)
from PySide6.QtCore import Qt

from core import history


class PasswordLab(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                color: #e5e5ed;
            }

            QLineEdit {
                background: #141421;
                border: 1px solid #29293d;
                border-radius: 8px;
                padding: 12px;
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

            QCheckBox {
                spacing: 10px;
            }

            QSlider::groove:horizontal {
                background: #29293d;
                height: 6px;
                border-radius: 3px;
            }

            QSlider::handle:horizontal {
                background: #a78bfa;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 30, 35, 30)
        layout.setSpacing(16)

        title = QLabel("Password Laboratory")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold;"
        )
        layout.addWidget(title)

        description = QLabel(
            "Generate secure passwords and analyze their strength."
        )
        description.setStyleSheet("color: #85859a;")
        layout.addWidget(description)

        layout.addSpacing(10)

        layout.addWidget(QLabel("PASSWORD LENGTH"))

        length_row = QHBoxLayout()

        self.length_slider = QSlider(Qt.Orientation.Horizontal)
        self.length_slider.setMinimum(8)
        self.length_slider.setMaximum(64)
        self.length_slider.setValue(20)
        self.length_slider.valueChanged.connect(
            self.update_length
        )

        self.length_label = QLabel("20")
        self.length_label.setStyleSheet(
            "color: #c4a7ff; font-weight: bold;"
        )

        length_row.addWidget(self.length_slider)
        length_row.addWidget(self.length_label)

        layout.addLayout(length_row)

        layout.addWidget(QLabel("CHARACTER SETS"))

        self.uppercase = QCheckBox("Uppercase letters (A-Z)")
        self.lowercase = QCheckBox("Lowercase letters (a-z)")
        self.numbers = QCheckBox("Numbers (0-9)")
        self.symbols = QCheckBox("Symbols (!@#$...)")

        self.uppercase.setChecked(True)
        self.lowercase.setChecked(True)
        self.numbers.setChecked(True)
        self.symbols.setChecked(True)

        layout.addWidget(self.uppercase)
        layout.addWidget(self.lowercase)
        layout.addWidget(self.numbers)
        layout.addWidget(self.symbols)

        layout.addSpacing(10)

        generate = QPushButton("GENERATE PASSWORD")
        generate.clicked.connect(self.generate_password)
        layout.addWidget(generate)

        layout.addWidget(QLabel("GENERATED PASSWORD"))

        self.password = QLineEdit()
        self.password.setReadOnly(True)
        self.password.setPlaceholderText(
            "Your generated password will appear here..."
        )
        layout.addWidget(self.password)

        copy = QPushButton("COPY PASSWORD")
        copy.clicked.connect(self.copy_password)
        layout.addWidget(copy)

        layout.addSpacing(15)

        layout.addWidget(QLabel("PASSWORD ANALYSIS"))

        self.strength = QLabel("Strength: Not analyzed")
        self.strength.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #c4a7ff;"
        )
        layout.addWidget(self.strength)

        self.entropy = QLabel("Estimated entropy: --")
        self.entropy.setStyleSheet("color: #85859a;")
        layout.addWidget(self.entropy)

        self.status = QLabel("")
        self.status.setStyleSheet("color: #a78bfa;")
        layout.addWidget(self.status)

        layout.addStretch()

    def update_length(self, value):
        self.length_label.setText(str(value))

    def generate_password(self):
        groups = []

        if self.uppercase.isChecked():
            groups.append(string.ascii_uppercase)

        if self.lowercase.isChecked():
            groups.append(string.ascii_lowercase)

        if self.numbers.isChecked():
            groups.append(string.digits)

        if self.symbols.isChecked():
            groups.append("!@#$%^&*()-_=+[]{};:,.?")

        if not groups:
            self.status.setText(
                "Select at least one character set."
            )
            return

        characters = "".join(groups)
        length = self.length_slider.value()

        password = [
            secrets.choice(group)
            for group in groups
        ]

        password.extend(
            secrets.choice(characters)
            for _ in range(length - len(password))
        )

        secrets.SystemRandom().shuffle(password)

        result = "".join(password)

        self.password.setText(result)
        self.analyze_password(result)

        self.status.setText("Password generated successfully.")

        history.add_record(
            "Password Lab",
            "Generated a password"
        )

    def analyze_password(self, password):
        pool = 0

        if any(c in string.ascii_lowercase for c in password):
            pool += 26

        if any(c in string.ascii_uppercase for c in password):
            pool += 26

        if any(c in string.digits for c in password):
            pool += 10

        if any(c in "!@#$%^&*()-_=+[]{};:,.?" for c in password):
            pool += len("!@#$%^&*()-_=+[]{};:,.?")

        entropy = len(password) * math.log2(pool)

        self.entropy.setText(
            f"Estimated entropy: {entropy:.1f} bits"
        )

        if entropy < 40:
            level = "Weak"
        elif entropy < 60:
            level = "Moderate"
        elif entropy < 80:
            level = "Strong"
        else:
            level = "Very Strong"

        self.strength.setText(f"Strength: {level}")

    def copy_password(self):
        value = self.password.text()

        if value:
            QApplication.clipboard().setText(value)
            self.status.setText("Password copied.")
