from PySide6.QtWidgets import QMainWindow, QTabWidget
from .tabs.network_tab import NetworkTab
from .tabs.analysis_tab import AnalysisTab
from .tabs.capacity_tab import CapacityTab
from .tabs.delivery_tab import DeliveryTab
from .tabs.requirements_tab import RequirementsTab
from .tabs.planning_tab import PlanningTab
from .tabs.measurements_tab import MeasurementsTab
from .tabs.reporting_tab import ReportingTab

#ui/main_window.py

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Claude Qushtepa Pilot Irrigation System")
        self.setMinimumSize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Add all tabs
        self.tabs.addTab(NetworkTab(), "Network Upload")
        self.tabs.addTab(AnalysisTab(), "Network Analysis")
        self.tabs.addTab(CapacityTab(), "Capacity Management")
        self.tabs.addTab(DeliveryTab(), "Water Delivery")
        self.tabs.addTab(RequirementsTab(), "Water Requirements")
        self.tabs.addTab(PlanningTab(), "Irrigation Planning")
        self.tabs.addTab(MeasurementsTab(), "Measurements")
        self.tabs.addTab(ReportingTab(), "Reports")