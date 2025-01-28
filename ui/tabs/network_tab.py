from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTextEdit, QFileDialog, QTreeWidget, QTreeWidgetItem,
                             QMessageBox, QHeaderView, QSplitter)
from PySide6.QtCore import Qt
import networkx as nx
import re

# ui/tabs/network_tab.py

class NetworkTab(QWidget):
    def __init__(self):
        super().__init__()
        self.network_data = None
        self.components = {
            'DP': 'Distribution Point',
            'MC': 'Canal',
            'ZT': 'Gate',
            'SW': 'Smart Water',
            'F': 'Field'
        }
        self.G = nx.DiGraph()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        # Top buttons row
        buttons_layout = QHBoxLayout()
        
        # Upload controls
        self.upload_btn = QPushButton("Upload Mermaid File")
        self.upload_btn.clicked.connect(self.upload_file)
        self.file_label = QLabel("No file selected")
        
        # Analysis button
        self.analyze_components_btn = QPushButton("1. Analyze Components")
        self.analyze_components_btn.clicked.connect(self.analyze_components)
        self.analyze_components_btn.setEnabled(False)
        
        # Add buttons to top row
        buttons_layout.addWidget(self.upload_btn)
        buttons_layout.addWidget(self.file_label)
        buttons_layout.addWidget(self.analyze_components_btn)
        buttons_layout.addStretch()
        
        # Add buttons row to main layout
        layout.addLayout(buttons_layout)
        
        # Middle section with content preview and results tree side by side
        middle_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # File content preview
        self.content_preview = QTextEdit()
        self.content_preview.setReadOnly(True)
        self.content_preview.setPlaceholderText("File content will appear here")
        middle_splitter.addWidget(self.content_preview)
        
        # Results tree
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["Component Type", "ID", "Details"])
        self.results_tree.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        middle_splitter.addWidget(self.results_tree)
        
        # Add middle section to vertical splitter
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.addWidget(middle_splitter)
        
        # Bottom section
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        
        # Path analysis button
        self.analyze_paths_btn = QPushButton("2. Analyze Paths")
        self.analyze_paths_btn.clicked.connect(self.analyze_paths)
        self.analyze_paths_btn.setEnabled(False)
        bottom_layout.addWidget(self.analyze_paths_btn)
        
        # Paths display
        self.paths_display = QTextEdit()
        self.paths_display.setReadOnly(True)
        self.paths_display.setPlaceholderText("Paths will appear here")
        bottom_layout.addWidget(self.paths_display)
        
        main_splitter.addWidget(bottom_widget)
        
        # Add the main splitter to the layout
        layout.addWidget(main_splitter)
        
        self.setLayout(layout)

    def upload_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Mermaid File",
            "",
            "Mermaid Files (*.mmd *.txt);;All Files (*)"
        )
        
        if file_name:
            try:
                with open(file_name, 'r') as file:
                    content = file.read()
                    self.network_data = content
                    self.file_label.setText(file_name.split('/')[-1])
                    self.content_preview.setText(content)
                    self.analyze_components_btn.setEnabled(True)
                    self.G.clear()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error reading file: {str(e)}")

    def analyze_components(self):
        if not self.network_data:
            return
        
        # Clear previous results
        self.results_tree.clear()
        self.G.clear()
        
        # Extract all components with their labels using regex
        # Pattern matches: ID["Label"] format
        extracted_components = re.findall(r'(\w+)\["([^\]]+)"\]', self.network_data)
        
        # Organize components by type
        component_groups = {}
        node_labels = {}
        
        for component_id, component_label in extracted_components:
            # Extract component type from ID (e.g., 'DP' from 'DP1')
            component_type = re.match(r'[A-Za-z]+', component_id).group()
            
            # Store in groups if it's a known component type
            if component_type in self.components:
                if component_type not in component_groups:
                    component_groups[component_type] = set()
                component_groups[component_type].add(component_id)
                node_labels[component_id] = component_label
                self.G.add_node(component_id)
        
        # Extract connections
        # Pattern matches: NodeA ---> NodeB or NodeA --> NodeB
        connections = re.findall(r'(\w+)\s*-+>\s*(\w+)', self.network_data)
        
        # Add edges to the graph
        for source, target in connections:
            if source in self.G.nodes() and target in self.G.nodes():
                self.G.add_edge(source, target)
        
        # Create tree items
        for comp_type, comp_set in sorted(component_groups.items()):
            # Create parent item with component type and count
            parent = QTreeWidgetItem(self.results_tree)
            parent.setText(0, self.components[comp_type])
            parent.setText(1, f"Total: {len(comp_set)}")
            parent.setExpanded(True)
            
            # Add child items for each component
            for comp_id in sorted(comp_set):
                child = QTreeWidgetItem(parent)
                child.setText(0, self.components[comp_type])  # Component type name
                child.setText(1, comp_id)  # Component ID
                
                # Add label and connectivity information
                details = node_labels.get(comp_id, "")
                if comp_type == 'F':
                    predecessors = list(self.G.predecessors(comp_id))
                    if predecessors:
                        details += f" (Connected to: {', '.join(predecessors)})"
                
                child.setText(2, details)  # Label and additional details
        
        # Enable path analysis
        self.analyze_paths_btn.setEnabled(True)
        
        # Show component counts
        component_counts = "\n".join(
            f"{self.components[ctype]}: {len(cset)}"
            for ctype, cset in sorted(component_groups.items())
        )
        
        QMessageBox.information(self, "Success", 
            f"Component analysis completed!\n\n"
            f"Component counts:\n{component_counts}")

    def analyze_paths(self):
        if not self.network_data:
            return
        
        self.paths_display.clear()
        
        # Get all field nodes
        fields = [n for n in self.G.nodes() if n.startswith('F')]
        if not fields:
            self.paths_display.setText("No fields found in the network.")
            return
            
        # Find paths to each field
        path_text = "Paths to Fields:\n\n"
        for field in sorted(fields):
            path_text += f"=== Field {field} ===\n"
            # Find all paths from distribution points to this field
            sources = [n for n in self.G.nodes() if n.startswith('DP')]
            
            field_paths = []
            for source in sources:
                try:
                    paths = list(nx.all_simple_paths(self.G, source, field))
                    field_paths.extend(paths)
                except nx.NetworkXNoPath:
                    continue
            
            if field_paths:
                for i, path in enumerate(field_paths, 1):
                    path_text += f"Path {i}: {' -> '.join(path)}\n"
            else:
                path_text += "No paths found to this field\n"
            path_text += "\n"
            
        self.paths_display.setText(path_text)
        
        QMessageBox.information(self, "Success", f"Path analysis completed for {len(fields)} fields!")