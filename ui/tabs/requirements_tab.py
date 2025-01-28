from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

# ui/tabs/requirements_tab.py

class RequirementsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Water Requirements Tab"))
        self.setLayout(layout)