"""
Route Optimizer Service
Uses NetworkX for optimal route planning based on:
- Predicted crowd levels
- Distance between attractions
- Time constraints
"""

import json
import math
import numpy as np
from typing import List, Dict, Tuple
from itertools import permutations
import os

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

class RouteOptimizer:
    """
    Optimizes tourist itineraries based on crowd predictions and distances.
    """
    
    def __init__(self, attractions_path: str = None):
        """
        Initialize optimizer.
        
        Args:
            attractions_path: Path to jaipur_attractions.json
        """
        self.attractions = {}
        self.distance_matrix = {}
        self.graph = None
        
        if attractions_path:
            self._load_attractions(attractions_path)
            self._build_graph()
    
    def _load_attractions(self, attractions_path: str):
        """Load attractions and build distance matrix."""
        with open(attractions_path, "r") as f:
            data = json.load(f)
            self.attractions = {a["id"]: a for a in data["attractions"]}
        
        # Pre-compute distance matrix
        self._compute_distance_matrix()
    
    def _compute_distance_matrix(self):
        """Compute pairwise distances using haversine formula."""
        attraction_ids = list(self.attractions.keys())
        
        for i, id1 in enumerate(attraction_ids):
            for j, id2 in enumerate(attraction_ids):
                if i >= j:
                    continue
                
                a1 = self.attractions[id1]
                a2 = self.attractions[id2]
                
                distance = self._haversine(
                    a1["latitude"], a1["longitude"],
                    a2["latitude"], a2["longitude"]
                )
                
                self.distance_matrix[f"{id1}_{id2}"] = distance
                self.distance_matrix[f"{id2}_{id1}"] = distance
    
    def _build_graph(self):
        """Build NetworkX graph for optimization."""
        if not HAS_NETWORKX:
            return
        
        self.graph = nx.Graph()
        
        # Add nodes
        for attr_id in self.attractions.keys():
            self.graph.add_node(attr_id)
        
        # Add edges with weights (distance)
        for key, distance in self.distance_matrix.items():
            if "_" in key:
                id1, id2 = key.split("_")
                self.graph.add_edge(id1, id2, weight=distance)
    
    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points on Earth.
        Returns distance in kilometers.
        """
        R = 6371  # Earth radius in km
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def get_distance(self, from_id: str, to_id: str) -> float:
        """Get distance between two attractions."""
        if from_id == to_id:
            return 0
        
        key = f"{from_id}_{to_id}"
        if key in self.distance_matrix:
            return self.distance_matrix[key]
        elif f"{to_id}_{from_id}" in self.distance_matrix:
            return self.distance_matrix[f"{to_id}_{from_id}"]
        else:
            return 0
    
    def optimize_itinerary(self, 
                          selected_attractions: List[str],
                          crowd_predictions: Dict,
                          time_budget_hours: int = 8,
                          max_travel_time: float = 0.5) -> Dict:
        """
        Optimize route for selected attractions.
        
        Args:
            selected_attractions: List of attraction IDs
            crowd_predictions: Dict with crowd forecast for each attraction
            time_budget_hours: Total time available
            max_travel_time: Max travel time between attractions (hours)
        
        Returns:
            Optimized itinerary with timing
        """
        if len(selected_attractions) <= 1:
            return self._single_attraction_itinerary(selected_attractions[0] if selected_attractions else None)
        
        # Score attractions for optimization
        scores = self._compute_attraction_scores(selected_attractions, crowd_predictions)
        
        # Use nearest neighbor heuristic (simple TSP)
        optimized_route = self._nearest_neighbor_tsp(selected_attractions, scores)
        
        # Add timing
        itinerary = self._add_timing(optimized_route, time_budget_hours, max_travel_time)
        
        return itinerary
    
    def _compute_attraction_scores(self, attractions: List[str], crowd_predictions: Dict) -> Dict:
        """Compute visit-worthiness score for each attraction."""
        scores = {}
        
        for attr_id in attractions:
            if attr_id not in self.attractions:
                continue
            
            attr_data = self.attractions[attr_id]
            
            # Base score: heritage priority
            score = attr_data["heritage_priority"] * 10
            
            # Adjust for predicted crowd (lower is better)
            if attr_id in crowd_predictions:
                crowd_level = crowd_predictions[attr_id]
                if crowd_level == "LOW":
                    score += 20
                elif crowd_level == "MODERATE":
                    score += 10
                elif crowd_level == "BUSY":
                    score -= 5
                elif crowd_level == "CROWDED":
                    score -= 15
            
            scores[attr_id] = score
        
        return scores
    
    def _nearest_neighbor_tsp(self, attractions: List[str], scores: Dict) -> List[str]:
        """
        Solve TSP using nearest neighbor heuristic.
        Prefers high-score attractions and minimizes distance.
        """
        # For small lists, use brute force
        if len(attractions) <= 5:
            return self._brute_force_tsp(attractions, scores)
        
        # Greedy nearest neighbor
        unvisited = set(attractions)
        # Start with highest score
        current = max(attractions, key=lambda x: scores.get(x, 0))
        route = [current]
        unvisited.remove(current)
        
        while unvisited:
            next_attr = min(unvisited, 
                          key=lambda x: self.get_distance(current, x))
            route.append(next_attr)
            unvisited.remove(next_attr)
            current = next_attr
        
        return route
    
    def _brute_force_tsp(self, attractions: List[str], scores: Dict) -> List[str]:
        """Find optimal route for small lists."""
        best_route = attractions
        best_score = self._route_cost(attractions, scores)
        
        for perm in permutations(attractions):
            cost = self._route_cost(list(perm), scores)
            if cost < best_score:
                best_score = cost
                best_route = list(perm)
        
        return best_route
    
    def _route_cost(self, route: List[str], scores: Dict) -> float:
        """Calculate total cost of route (distance + time penalty)."""
        total_cost = 0
        
        # Distance cost
        for i in range(len(route) - 1):
            distance = self.get_distance(route[i], route[i+1])
            total_cost += distance
        
        # Invert scores (higher score = lower cost)
        for attr_id in route:
            score = scores.get(attr_id, 0)
            total_cost -= score / 1000  # Small weight to prioritize scores
        
        return total_cost
    
    def _add_timing(self, route: List[str], total_hours: int, max_travel_time: float) -> Dict:
        """Add timing to optimized route."""
        itinerary = {
            "attractions": [],
            "total_distance_km": 0,
            "total_travel_time_hours": 0,
            "total_visit_time_hours": 0
        }
        
        time_per_attraction = total_hours / len(route) if route else 0
        current_time = 0
        
        for i, attr_id in enumerate(route):
            if attr_id not in self.attractions:
                continue
            
            attr_data = self.attractions[attr_id]
            
            # Travel time
            if i > 0:
                distance = self.get_distance(route[i-1], attr_id)
                travel_time = distance / 25  # Assume 25 km/h avg speed
                itinerary["total_distance_km"] += distance
                itinerary["total_travel_time_hours"] += travel_time
                current_time += travel_time
            
            # Visit time (proportional to priority)
            visit_time = min(time_per_attraction, 2.0)  # Max 2h per site
            itinerary["total_visit_time_hours"] += visit_time
            
            itinerary["attractions"].append({
                "id": attr_id,
                "name": attr_data["name"],
                "category": attr_data["category"],
                "latitude": attr_data["latitude"],
                "longitude": attr_data["longitude"],
                "start_time_hours": round(current_time, 2),
                "visit_duration_hours": round(visit_time, 2),
                "recommended": True
            })
            
            current_time += visit_time
        
        return itinerary
    
    def _single_attraction_itinerary(self, attr_id: str = None) -> Dict:
        """Create itinerary for single attraction."""
        if not attr_id or attr_id not in self.attractions:
            return {"attractions": [], "total_distance_km": 0}
        
        attr_data = self.attractions[attr_id]
        
        return {
            "attractions": [{
                "id": attr_id,
                "name": attr_data["name"],
                "category": attr_data["category"],
                "latitude": attr_data["latitude"],
                "longitude": attr_data["longitude"],
                "start_time_hours": 0,
                "visit_duration_hours": 2.0,
                "recommended": True
            }],
            "total_distance_km": 0,
            "total_travel_time_hours": 0,
            "total_visit_time_hours": 2.0
        }
