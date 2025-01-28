from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

# ui/tabs/planning_tab.py

class PlanningTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Irrigation Planning Tab"))
        self.setLayout(layout)