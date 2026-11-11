
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QComboBox, QSpinBox,
    QLineEdit, QApplication
)

from core import history


class CipherLab(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                color: #e5e5ed;
            }

            QTextEdit, QLineEdit, QComboBox, QSpinBox {
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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 30, 35, 30)
        layout.setSpacing(15)

        title = QLabel("Cipher Laboratory")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold;"
        )
        layout.addWidget(title)

        description = QLabel(
            "Encrypt and decrypt text using classical ciphers."
        )
        description.setStyleSheet("color: #85859a;")
        layout.addWidget(description)

        layout.addSpacing(10)

        layout.addWidget(QLabel("SELECT CIPHER"))

        self.cipher = QComboBox()
        self.cipher.addItems([
            "Caesar",
            "Atbash",
            "Vigenère"
        ])
        self.cipher.currentTextChanged.connect(
            self.update_options
        )
        layout.addWidget(self.cipher)

        self.options_layout = QVBoxLayout()
        layout.addLayout(self.options_layout)

        self.shift_label = QLabel("SHIFT VALUE")
        self.shift = QSpinBox()
        self.shift.setRange(1, 25)
        self.shift.setValue(3)

        self.keyword_label = QLabel("KEYWORD")
        self.keyword = QLineEdit()
        self.keyword.setPlaceholderText(
            "Enter a keyword..."
        )

        self.options_layout.addWidget(self.shift_label)
        self.options_layout.addWidget(self.shift)
        self.options_layout.addWidget(self.keyword_label)
        self.options_layout.addWidget(self.keyword)

        layout.addWidget(QLabel("INPUT TEXT"))

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText(
            "Enter text to encrypt or decrypt..."
        )
        self.input_text.setMinimumHeight(130)
        layout.addWidget(self.input_text)

        button_row = QHBoxLayout()

        encrypt_button = QPushButton("ENCRYPT")
        encrypt_button.clicked.connect(
            lambda: self.process(True)
        )

        decrypt_button = QPushButton("DECRYPT")
        decrypt_button.clicked.connect(
            lambda: self.process(False)
        )

        button_row.addWidget(encrypt_button)
        button_row.addWidget(decrypt_button)

        layout.addLayout(button_row)

        layout.addWidget(QLabel("OUTPUT"))

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(130)
        layout.addWidget(self.output_text)

        bottom_row = QHBoxLayout()

        copy_button = QPushButton("COPY OUTPUT")
        copy_button.clicked.connect(self.copy_output)

        clear_button = QPushButton("CLEAR")
        clear_button.clicked.connect(self.clear)

        bottom_row.addWidget(copy_button)
        bottom_row.addWidget(clear_button)

        layout.addLayout(bottom_row)

        self.status = QLabel("")
        self.status.setStyleSheet("color: #a78bfa;")
        layout.addWidget(self.status)

        layout.addStretch()

        self.update_options()

    def update_options(self):
        cipher = self.cipher.currentText()

        self.shift_label.setVisible(cipher == "Caesar")
        self.shift.setVisible(cipher == "Caesar")

        self.keyword_label.setVisible(cipher == "Vigenère")
        self.keyword.setVisible(cipher == "Vigenère")

    def caesar(self, text, shift):
        result = ""

        for char in text:
            if char.isascii() and char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                result += chr(
                    (ord(char) - base + shift) % 26 + base
                )
            else:
                result += char

        return result

    def atbash(self, text):
        result = ""

        for char in text:
            if char.isascii() and char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                result += chr(
                    base + 25 - (ord(char) - base)
                )
            else:
                result += char

        return result

    def vigenere(self, text, key, decrypt=False):
        result = ""
        key = key.upper()
        key_index = 0

        for char in text:
            if char.isascii() and char.isalpha():
                base = ord('A') if char.isupper() else ord('a')

                shift = ord(key[key_index % len(key)]) - ord('A')

                if decrypt:
                    shift = -shift

                result += chr(
                    (ord(char) - base + shift) % 26 + base
                )

                key_index += 1
            else:
                result += char

        return result

    def process(self, encrypting):
        text = self.input_text.toPlainText()

        if not text:
            self.status.setText("Enter some text first.")
            return

        cipher = self.cipher.currentText()

        if cipher == "Caesar":
            shift = self.shift.value()

            if not encrypting:
                shift = -shift

            result = self.caesar(text, shift)

        elif cipher == "Atbash":
            result = self.atbash(text)

        else:
            key = self.keyword.text().strip()

            if not key or not key.isascii() or not key.isalpha():
                self.status.setText(
                    "Enter a keyword containing only A-Z letters."
                )
                return

            result = self.vigenere(
                text, key, decrypt=not encrypting
            )

        self.output_text.setPlainText(result)

        action = "encrypted" if encrypting else "decrypted"
        self.status.setText(
            f"Text {action} successfully."
        )

        history.add_record(
            "Cipher Lab",
            f"{cipher}: text {action}"
        )

    def copy_output(self):
        value = self.output_text.toPlainText()

        if value:
            QApplication.clipboard().setText(value)
            self.status.setText("Output copied.")

    def clear(self):
        self.input_text.clear()
        self.output_text.clear()
        self.status.setText("")
