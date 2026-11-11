
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt

from core import history


class HistoryLab(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                color: #e5e5ed;
            }

            QTableWidget {
                background: #141421;
                border: 1px solid #29293d;
                border-radius: 8px;
                gridline-color: #29293d;
                color: #eeeeff;
            }

            QHeaderView::section {
                background: #1c1b2b;
                color: #c4a7ff;
                border: none;
                padding: 10px;
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

        title = QLabel("Activity History")
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        description = QLabel(
            "A record of your recent CRYPTIX operations."
        )
        description.setStyleSheet("color: #85859a;")

        layout.addWidget(title)
        layout.addWidget(description)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            "OPERATION",
            "DESCRIPTION",
            "TIMESTAMP"
        ])

        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.verticalHeader().setVisible(False)

        layout.addWidget(self.table)

        buttons = QHBoxLayout()

        refresh_button = QPushButton("REFRESH")
        refresh_button.clicked.connect(self.refresh)

        clear_button = QPushButton("CLEAR HISTORY")
        clear_button.clicked.connect(self.clear)

        buttons.addWidget(refresh_button)
        buttons.addStretch()
        buttons.addWidget(clear_button)

        layout.addLayout(buttons)

        self.status = QLabel("")
        self.status.setStyleSheet("color: #a78bfa;")
        layout.addWidget(self.status)

        self.refresh()

    def refresh(self):
        records = history.get_records()

        self.table.setRowCount(len(records))

        for row, record in enumerate(records):
            _, operation, description, timestamp = record

            values = [
                operation,
                description,
                timestamp.replace("T", " ")
            ]

            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setFlags(
                    item.flags()
                    & ~Qt.ItemFlag.ItemIsEditable
                )
                self.table.setItem(row, column, item)

        self.status.setText(
            f"{len(records)} recent operations"
        )

    def clear(self):
        answer = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to delete all history?"
        )

        if answer == QMessageBox.StandardButton.Yes:
            history.clear_history()
            self.refresh()
            self.status.setText("History cleared.")

