import re

class PathExtractor:
    def __init__(self, connections):
        self.connections = connections
        self.paths = {}
        self.diagnostics = []
        
    def extract_connections(self, line):
        """
        Extract all connections from a line that might contain multiple targets.
        Example: 
        'MC01["Label"] ---> DP1["Label"] & DP2["Label"]' 
        -> [('MC01', 'DP1'), ('MC01', 'DP2')]
        """
        # First split on '--->
        parts = line.split('--->')
        if len(parts) != 2:
            return []
            
        source_part, targets_part = parts
        
        # Extract source node ID
        source_match = re.match(r'(\w+)(?:\[[^\]]+\])?', source_part.strip())
        if not source_match:
            return []
        source = source_match.group(1)
        
        # Split targets on & and extract each target node ID
        connections = []
        targets = targets_part.split('&')
        for target in targets:
            target_match = re.match(r'(\w+)(?:\[[^\]]+\])?', target.strip())
            if target_match:
                target_id = target_match.group(1)
                connections.append((source, target_id))
                
        return connections

    def find_all_paths(self, start_points, end_points):
        """Find all possible paths from start points to end points."""
        # Create adjacency maps
        outgoing_map = {}
        incoming_map = {}
        
        # Process connections
        for conn_line in self.connections:
            for source, target in self.extract_connections(conn_line):
                # Build outgoing connections
                if source not in outgoing_map:
                    outgoing_map[source] = set()
                outgoing_map[source].add(target)
                
                # Build incoming connections
                if target not in incoming_map:
                    incoming_map[target] = set()
                incoming_map[target].add(source)
        
        # Find root nodes (nodes with no incoming connections)
        all_nodes = set(outgoing_map.keys()) | set(incoming_map.keys())
        root_nodes = {node for node in all_nodes if node not in incoming_map}
        
        # Clear previous results
        self.paths = {}
        self.diagnostics = []
        
        # Process each end point
        for end in end_points:
            self.paths[end] = []
            
            # Verify end point exists in the graph
            if end not in incoming_map and end not in outgoing_map:
                self.diagnostics.append(f"Warning: End point {end} is not connected to the network")
                continue
                
            # For efficiency, first check if end point is reachable from any root
            reachable_nodes = self._get_reachable_nodes(end, incoming_map)
            if not (reachable_nodes & root_nodes):
                self.diagnostics.append(f"Warning: No complete path exists to {end} from any source")
                self._analyze_path_breaks(end, incoming_map, outgoing_map)
                continue
                
            # Find paths from each start point
            for start in start_points:
                paths = self._find_paths(start, end, outgoing_map)
                if paths:
                    self.paths[end].extend(paths)
            
            if not self.paths[end]:
                self.diagnostics.append(f"Warning: No paths found to {end} from specified start points")
                self._analyze_path_breaks(end, incoming_map, outgoing_map)

    def _get_reachable_nodes(self, target, incoming_map):
        """Get all nodes that can reach the target."""
        reachable = set()
        to_visit = {target}
        
        while to_visit:
            node = to_visit.pop()
            reachable.add(node)
            if node in incoming_map:
                for prev_node in incoming_map[node]:
                    if prev_node not in reachable:
                        to_visit.add(prev_node)
        
        return reachable

    def _analyze_path_breaks(self, end_node, incoming_map, outgoing_map):
        """Analyze and report where paths break."""
        current_nodes = {end_node}
        visited = set()
        level = 0
        
        while current_nodes:
            next_nodes = set()
            for node in current_nodes:
                if node not in incoming_map:
                    self.diagnostics.append(f"  - Path breaks at {node} (level {level}): No incoming connections")
                else:
                    for prev_node in incoming_map[node]:
                        if prev_node not in visited:
                            next_nodes.add(prev_node)
                            visited.add(prev_node)
            current_nodes = next_nodes
            level += 1

    def _find_paths(self, start, end, outgoing_map, path=None, visited=None):
        """
        Recursively find all paths from start to end.
        Uses visited set to prevent cycles.
        """
        if path is None:
            path = [start]
        if visited is None:
            visited = {start}
            
        if start == end:
            return [path]
            
        if start not in outgoing_map:
            return []
            
        paths = []
        for next_node in outgoing_map[start]:
            if next_node not in visited:
                visited.add(next_node)
                new_paths = self._find_paths(next_node, end, outgoing_map, 
                                           path + [next_node], visited)
                paths.extend(new_paths)
                visited.remove(next_node)
                
        return paths

    def get_path_data(self):
        """
        Get path data in a structured format suitable for the React component.
        Returns a dictionary with diagnostics and paths.
        """
        data = {
            "diagnostics": self.diagnostics,
            "paths": {}
        }
        
        for end_point, paths in sorted(self.paths.items()):
            if paths:
                data["paths"][end_point] = []
                for path in paths:
                    # Determine path type based on end point
                    if end_point.startswith('F'):
                        path_type = "Field Connection"
                    elif end_point.startswith('MC'):
                        path_type = "Canal Connection"
                    elif end_point.startswith('ZT'):
                        path_type = "Gate Connection"
                    elif end_point.startswith('SW'):
                        path_type = "Smart Water Connection"
                    else:
                        path_type = "Other Connection"
                    
                    path_info = {
                        "path": path,
                        "length": len(path) - 1,  # Number of segments
                        "type": path_type
                    }
                    data["paths"][end_point].append(path_info)
        
        return data

    def get_path_summary(self):
        """Get a text summary of all found paths with diagnostics (legacy format)."""
        summary = "Path Summary:\n"
        summary += "=" * 30 + "\n\n"
        
        if self.diagnostics:
            summary += "Diagnostic Information:\n"
            summary += "-" * 20 + "\n"
            for diag in self.diagnostics:
                summary += f"{diag}\n"
            summary += "\n"
        
        for end_point, paths in sorted(self.paths.items()):
            summary += f"Paths to {end_point}:\n"
            summary += "-" * 20 + "\n"
            
            if not paths:
                summary += "No complete paths found\n"
            else:
                for i, path in enumerate(paths, 1):
                    summary += f"Path {i}: {' ---> '.join(path)}\n"
            summary += "\n"
            
        return summary