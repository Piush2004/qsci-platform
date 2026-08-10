try:
    from ortools.constraint_solver import routing_enums_pb2
    from ortools.constraint_solver import pywrapcp
except ImportError:
    print("OR-Tools not installed. Mocking VRP solver.")
    pywrapcp = None

class VRPSolver:
    """
    Solves the Capacitated Vehicle Routing Problem (CVRP) using Google OR-Tools.
    This serves as the Classical SOTA baseline against Quantum QAOA.
    """
    def __init__(self, num_vehicles: int, depot_index: int = 0):
        self.num_vehicles = num_vehicles
        self.depot_index = depot_index
        
    def solve(self, distance_matrix: list, demands: list, vehicle_capacities: list):
        """
        Solve CVRP given a distance matrix and demands.
        """
        if pywrapcp is None:
            return {"status": "OR-Tools not installed", "routes": []}
            
        # 1. Create Data Model
        data = {
            'distance_matrix': distance_matrix,
            'demands': demands,
            'vehicle_capacities': vehicle_capacities,
            'num_vehicles': self.num_vehicles,
            'depot': self.depot_index
        }
        
        # 2. Create Routing Index Manager and Routing Model
        manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                               data['num_vehicles'], data['depot'])
        routing = pywrapcp.RoutingModel(manager)
        
        # 3. Create and register a transit callback
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['distance_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # 4. Add Capacity constraint
        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            return data['demands'][from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            data['vehicle_capacities'],  # vehicle maximum capacities
            True,  # start cumul to zero
            'Capacity'
        )
        
        # 5. Setting first solution heuristic
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
        search_parameters.time_limit.FromSeconds(5)

        # 6. Solve the problem
        solution = routing.SolveWithParameters(search_parameters)
        
        if solution:
            return self._extract_routes(data, manager, routing, solution)
        else:
            return {"status": "No solution found"}

    def _extract_routes(self, data, manager, routing, solution):
        """
        Extract routes from the OR-Tools solution.
        """
        routes = []
        total_distance = 0
        total_load = 0
        
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            route = []
            route_distance = 0
            route_load = 0
            
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route_load += data['demands'][node_index]
                route.append({"node": node_index, "load": route_load})
                
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
                
            node_index = manager.IndexToNode(index)
            route.append({"node": node_index, "load": route_load})
            
            routes.append({
                "vehicle_id": vehicle_id,
                "route": route,
                "distance": route_distance,
                "load": route_load
            })
            total_distance += route_distance
            total_load += route_load
            
        return {
            "status": "Optimal",
            "routes": routes,
            "total_distance": total_distance,
            "total_load": total_load
        }
