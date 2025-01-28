from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTextEdit, QFileDialog, QTreeWidget, QTreeWidgetItem,
                             QMessageBox, QHeaderView, QSplitter)
from PySide6.QtCore import Qt
import networkx as nx
import re
from .path_extractor import PathExtractor

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
        self.connections = [] #Store connections as strings instead of using networkx
        self.node_labels = {}
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
                    self.connections = []
                    self.node_labels.clear()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error reading file: {str(e)}")

    def analyze_components(self):
        if not self.network_data:
            return
        
        # Clear previous results
        self.results_tree.clear()
        self.connections.clear()
        self.node_labels.clear()
        
        # Extract all components with their labels using regex
        extracted_components = re.findall(r'(\w+)\["([^\]]+)"\]', self.network_data)
        
        # Organize components by type
        component_groups = {}
        
        for component_id, component_label in extracted_components:
            # Extract component type from ID
            component_type = re.match(r'[A-Za-z]+', component_id).group()
            
            # Store in groups if it's a known component type
            if component_type in self.components:
                if component_type not in component_groups:
                    component_groups[component_type] = set()
                component_groups[component_type].add(component_id)
                self.node_labels[component_id] = component_label
        
        # Extract connections
        self.connections = re.findall(r'(\w+)\s*-+>\s*(\w+)', self.network_data)
        # Convert connections to the format expected by PathExtractor
        self.connections = [f"{source}--->{target}" for source, target in self.connections]
        
        # Create tree items
        for comp_type, comp_set in sorted(component_groups.items()):
            parent = QTreeWidgetItem(self.results_tree)
            parent.setText(0, self.components[comp_type])
            parent.setText(1, f"Total: {len(comp_set)}")
            parent.setExpanded(True)
            
            for comp_id in sorted(comp_set):
                child = QTreeWidgetItem(parent)
                child.setText(0, self.components[comp_type])
                child.setText(1, comp_id)
                
                # Add label and connectivity information
                details = self.node_labels.get(comp_id, "")
                if comp_type == 'F':
                    # Find predecessors by checking connections
                    predecessors = [src for src, tgt in [conn.split("--->") for conn in self.connections] 
                                  if tgt == comp_id]
                    if predecessors:
                        details += f" (Connected to: {', '.join(predecessors)})"
                
                child.setText(2, details)
        
        # Enable path analysis
        self.analyze_paths_btn.setEnabled(True)
        
        # Show component counts
        field_count = len(component_groups.get('F', []))
        total_count = sum(len(comp_set) for comp_set in component_groups.values())
        
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
        
        # Get raw connection lines from the mermaid file
        connection_lines = [line.strip() for line in self.network_data.split('\n') 
                        if '-->' in line]
        
        # Create path extractor with raw connection lines
        path_extractor = PathExtractor(connection_lines)
        
        # Build connection maps to determine start and end points
        outgoing_map = {}
        incoming_map = {}
        all_nodes = set()
        
        for conn in connection_lines:
            for source, target in path_extractor.extract_connections(conn):
                all_nodes.add(source)
                all_nodes.add(target)
                
                if source not in outgoing_map:
                    outgoing_map[source] = set()
                outgoing_map[source].add(target)
                
                if target not in incoming_map:
                    incoming_map[target] = set()
                incoming_map[target].add(source)
        
        # Find start points (nodes with no incoming connections)
        start_points = [node for node in all_nodes if node not in incoming_map]
        
        # Find end points (nodes with no outgoing connections)
        end_points = [node for node in all_nodes if node not in outgoing_map]
        
        # Sort points for consistent display
        start_points.sort()
        end_points.sort()
        
        # Find all paths
        path_extractor.find_all_paths(start_points, end_points)
        
        # Get path analysis results
        path_text = path_extractor.get_path_summary()
        
        # Display results
        self.paths_display.setText(path_text)
        
        # Calculate summary statistics
        total_paths = sum(len(paths) for paths in path_extractor.paths.values())
        total_endpoints = len(end_points)
        endpoints_with_paths = sum(1 for paths in path_extractor.paths.values() if paths)
        
        if total_paths == 0:
            QMessageBox.warning(self, "Analysis Complete", 
                f"No valid paths found from detected source points ({', '.join(start_points)}) "
                f"to end points ({', '.join(end_points)}).\n"
                "Please check the diagnostic information for details.")
            return
            
        # Calculate average path length
        path_lengths = []
        for paths in path_extractor.paths.values():
            for path in paths:
                path_lengths.append(len(path) - 1)  # -1 because n nodes = n-1 segments
                
        avg_path_length = sum(path_lengths) / len(path_lengths) if path_lengths else 0
        
        # Show summary message
        QMessageBox.information(self, "Analysis Complete", 
            f"Found paths to {endpoints_with_paths} out of {total_endpoints} end points.\n"
            f"Start points detected: {', '.join(start_points)}\n"
            f"End points detected: {', '.join(end_points)}\n"
            f"Total number of unique paths: {total_paths}\n"
            f"Average path length: {avg_path_length:.1f} segments")