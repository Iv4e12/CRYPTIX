
import hashlib
import hmac

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QComboBox, QFileDialog,
    QFrame, QMessageBox, QApplication
)

from core import history


class HashingLab(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                color: #e5e5ed;
            }
            QTextEdit, QComboBox {
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

        title = QLabel("Hashing Laboratory")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold;"
        )
        layout.addWidget(title)

        description = QLabel(
            "Generate cryptographic hashes from text or files."
        )
        description.setStyleSheet("color: #85859a;")
        layout.addWidget(description)

        self.algorithm = QComboBox()
        self.algorithm.addItems([
            "SHA-256",
            "SHA-512",
            "SHA3-256",
            "SHA3-512"
        ])
        layout.addWidget(QLabel("HASH ALGORITHM"))
        layout.addWidget(self.algorithm)

        layout.addWidget(QLabel("INPUT TEXT"))

        self.input = QTextEdit()
        self.input.setPlaceholderText(
            "Enter text to calculate its hash..."
        )
        self.input.setMinimumHeight(130)
        layout.addWidget(self.input)

        buttons = QHBoxLayout()

        generate = QPushButton("GENERATE HASH")
        generate.clicked.connect(self.generate_hash)

        file_button = QPushButton("HASH FILE")
        file_button.clicked.connect(self.hash_file)

        buttons.addWidget(generate)
        buttons.addWidget(file_button)

        layout.addLayout(buttons)

        layout.addWidget(QLabel("RESULT"))

        self.result = QTextEdit()
        self.result.setReadOnly(True)
        self.result.setPlaceholderText("Your hash will appear here...")
        self.result.setMaximumHeight(110)
        layout.addWidget(self.result)

        result_buttons = QHBoxLayout()

        copy = QPushButton("COPY HASH")
        copy.clicked.connect(self.copy_hash)

        clear = QPushButton("CLEAR")
        clear.clicked.connect(self.clear)

        result_buttons.addWidget(copy)
        result_buttons.addWidget(clear)

        layout.addLayout(result_buttons)

        layout.addWidget(QLabel("HASH COMPARISON"))

        self.compare_input = QTextEdit()
        self.compare_input.setPlaceholderText(
            "Paste another hash here to compare..."
        )
        self.compare_input.setMaximumHeight(80)
        layout.addWidget(self.compare_input)

        compare = QPushButton("COMPARE HASHES")
        compare.clicked.connect(self.compare_hashes)
        layout.addWidget(compare)

        self.status = QLabel("")
        self.status.setStyleSheet("color: #a78bfa;")
        layout.addWidget(self.status)

        layout.addStretch()

    def get_hasher(self):
        algorithms = {
            "SHA-256": hashlib.sha256,
            "SHA-512": hashlib.sha512,
            "SHA3-256": hashlib.sha3_256,
            "SHA3-512": hashlib.sha3_512
        }
        return algorithms[self.algorithm.currentText()]

    def generate_hash(self):
        data = self.input.toPlainText().encode("utf-8")
        result = self.get_hasher()(data).hexdigest()

        self.result.setPlainText(result)
        self.status.setText("Hash generated successfully.")

        history.add_record(
            "Hashing",
            f"Generated {self.algorithm.currentText()} text hash"
        )

    def hash_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select file"
        )

        if not path:
            return

        try:
            hasher = self.get_hasher()()

            with open(path, "rb") as file:
                for chunk in iter(
                    lambda: file.read(1024 * 1024), b""
                ):
                    hasher.update(chunk)

            self.result.setPlainText(hasher.hexdigest())
            self.status.setText("File hashed successfully.")

            history.add_record(
                "Hashing",
                f"Generated {self.algorithm.currentText()} file hash"
            )

        except OSError as error:
            QMessageBox.critical(
                self, "File Error", str(error)
            )

    def copy_hash(self):
        value = self.result.toPlainText().strip()

        if value:
            QApplication.clipboard().setText(value)
            self.status.setText("Hash copied.")

    def clear(self):
        self.input.clear()
        self.result.clear()
        self.compare_input.clear()
        self.status.clear()

    def compare_hashes(self):
        first = self.result.toPlainText().strip().lower()
        second = self.compare_input.toPlainText().strip().lower()

        if not first or not second:
            self.status.setText("Enter both hashes first.")
            return

        if hmac.compare_digest(first, second):
            self.status.setText("MATCH: Hashes are identical.")
        else:
            self.status.setText("NO MATCH: Hashes differ.")
