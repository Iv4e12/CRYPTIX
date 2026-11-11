
import os
import base64

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QLineEdit, QMessageBox
)

from core import history


class EncryptionLab(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                color: #e5e5ed;
            }

            QTextEdit, QLineEdit {
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

        title = QLabel("AES-256-GCM Encryption")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold;"
        )
        layout.addWidget(title)

        description = QLabel(
            "Encrypt and decrypt text using authenticated encryption."
        )
        description.setStyleSheet("color: #85859a;")
        layout.addWidget(description)

        layout.addWidget(QLabel("PASSWORD"))

        self.password = QLineEdit()
        self.password.setPlaceholderText(
            "Enter an encryption password..."
        )
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password)

        layout.addWidget(QLabel("INPUT TEXT"))

        self.input = QTextEdit()
        self.input.setPlaceholderText(
            "Enter text to encrypt or paste encrypted data..."
        )
        self.input.setMinimumHeight(150)
        layout.addWidget(self.input)

        buttons = QHBoxLayout()

        encrypt = QPushButton("ENCRYPT")
        encrypt.clicked.connect(self.encrypt_text)

        decrypt = QPushButton("DECRYPT")
        decrypt.clicked.connect(self.decrypt_text)

        buttons.addWidget(encrypt)
        buttons.addWidget(decrypt)

        layout.addLayout(buttons)

        layout.addWidget(QLabel("OUTPUT"))

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setPlaceholderText(
            "Encrypted or decrypted text will appear here..."
        )
        self.output.setMinimumHeight(130)
        layout.addWidget(self.output)

        result_buttons = QHBoxLayout()

        copy = QPushButton("COPY OUTPUT")
        copy.clicked.connect(self.copy_output)

        clear = QPushButton("CLEAR")
        clear.clicked.connect(self.clear)

        result_buttons.addWidget(copy)
        result_buttons.addWidget(clear)

        layout.addLayout(result_buttons)

        self.status = QLabel("")
        self.status.setStyleSheet("color: #a78bfa;")
        layout.addWidget(self.status)

        layout.addStretch()

    def derive_key(self, password, salt):
        kdf = Scrypt(
            salt=salt,
            length=32,
            n=2**14,
            r=8,
            p=1
        )

        return kdf.derive(password.encode("utf-8"))

    def encrypt_text(self):
        password = self.password.text()
        plaintext = self.input.toPlainText()

        if not password or not plaintext:
            self.status.setText(
                "Enter both a password and some text."
            )
            return

        try:
            salt = os.urandom(16)
            nonce = os.urandom(12)

            key = self.derive_key(password, salt)

            aes = AESGCM(key)
            ciphertext = aes.encrypt(
                nonce,
                plaintext.encode("utf-8"),
                None
            )

            package = salt + nonce + ciphertext

            encoded = base64.b64encode(
                package
            ).decode("ascii")

            self.output.setPlainText(encoded)
            self.status.setText(
                "Encryption completed successfully."
            )

            history.add_record(
                "Encryption",
                "Encrypted text using AES-256-GCM"
            )

        except Exception as error:
            self.status.setText(
                f"Encryption failed: {error}"
            )

    def decrypt_text(self):
        password = self.password.text()
        encrypted = self.input.toPlainText().strip()

        if not password or not encrypted:
            self.status.setText(
                "Enter a password and encrypted text."
            )
            return

        try:
            package = base64.b64decode(
                encrypted,
                validate=True
            )

            if len(package) < 44:
                raise ValueError("Invalid encrypted data.")

            salt = package[:16]
            nonce = package[16:28]
            ciphertext = package[28:]

            key = self.derive_key(password, salt)

            aes = AESGCM(key)

            plaintext = aes.decrypt(
                nonce,
                ciphertext,
                None
            )

            self.output.setPlainText(
                plaintext.decode("utf-8")
            )

            self.status.setText(
                "Decryption completed successfully."
            )

            history.add_record(
                "Encryption",
                "Decrypted text using AES-256-GCM"
            )

        except Exception:
            self.output.clear()
            self.status.setText(
                "Decryption failed. Check the password and data."
            )

    def copy_output(self):
        value = self.output.toPlainText()

        if value:
            from PySide6.QtWidgets import QApplication
            QApplication.clipboard().setText(value)
            self.status.setText("Output copied.")

    def clear(self):
        self.password.clear()
        self.input.clear()
        self.output.clear()
        self.status.clear()
