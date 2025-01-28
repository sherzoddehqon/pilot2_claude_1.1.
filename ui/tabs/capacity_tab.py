from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

# ui/tabs/capacity_tab.py

class CapacityTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Capacity Management Tab"))
        self.setLayout(layout)
