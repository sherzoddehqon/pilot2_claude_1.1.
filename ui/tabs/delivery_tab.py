from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

# ui/tabs/delivery_tab.py

class DeliveryTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Water Delivery Tab"))
        self.setLayout(layout)