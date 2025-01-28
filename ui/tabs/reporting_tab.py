from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

# ui/tabs/reporting_tab.py

class ReportingTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Reports Tab"))
        self.setLayout(layout)