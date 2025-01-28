from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
# ui/tabs/analysis_tab.py

class AnalysisTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Network Analysis Tab"))
        self.setLayout(layout)
        
