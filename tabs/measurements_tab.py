from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

# ui/tabs/measurements_tab.py

class MeasurementsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Measurements Tab"))
        self.setLayout(layout)