import time
import tracemalloc
from queue import PriorityQueue
from collections import deque
from Code import config
from Code import helpFunctions
from Code.gameboard import Gameboard
from Code.vehicle import Vehicle

# Depth-Limited Search (DLS) algorithm
def dls_algorithm(gameboard: Gameboard, limit):
    #Start memory tracing
    tracemalloc.start()

    # Start calculating the time
    start = time.time()
    
    # Number of expanded nodes
    expanded_nodes = 0

    # Initialize the stack (frontier) for DLS
    frontier = deque()
    
    # Keep track of visited states to avoid revisiting the same gameboard
    visited = {}

    # Add the initial gameboard and its depth (0) to the frontier
    frontier.append((gameboard, 0))
    visited[gameboard] = (gameboard, None)  # No parent for root

    while frontier:
        # Pop the most recent gameboard
        current_gameboard, depth = frontier.pop()
        
        # Skip if depth exceeds the limit
        if depth > limit:
            continue
        
        # Increment expanded node count
        expanded_nodes += 1

        # Get the successors of the current state
        for new_vehicles in current_gameboard.check_for_moves():
            next_gameboard = Gameboard(config.GAMEBOARD_WIDTH, config.GAMEBOARD_HEIGHT, new_vehicles)

            if next_gameboard not in visited:

                # Check if next gameboard is the goal state
                if next_gameboard.has_solved():
                    end = time.time()
                    _, peak = tracemalloc.get_traced_memory()

                    tracemalloc.stop()

                    path = helpFunctions.trace_back_solution(visited, gameboard, current_gameboard)
                    path.append(next_gameboard)

                    return path, end-start, peak, expanded_nodes, len(path), None

                visited[next_gameboard] = (next_gameboard, current_gameboard)
                frontier.append((next_gameboard, depth + 1))

    # Return failure if no solution was found within the limit
    end = time.time()
    _, peak = tracemalloc.get_traced_memory()

    tracemalloc.stop()
    return None, end-start, peak, expanded_nodes, None, None

# BFS algorithm
def bfs_algorithm(gameboard: Gameboard):
    #Start memory tracing
    tracemalloc.start()

    # Get start time currently
    start = time.time()

    # Number of expanded nodes
    expanded_nodes = 0
    # Initialize the queue for BFS
    queue = deque()
    # Keep track of visited states to avoid cycles
    visited = {}

    # Add the start state to the queue and mark it as visited
    queue.append(gameboard)
    visited[gameboard] = (gameboard, None)

    # While there are states to explore in the queue
    while queue:
        # Get the current state from the queue and increase the expanded nodes count
        current_gameboard = queue.popleft()
        expanded_nodes += 1

        # Get the successors of the current state
        for new_vehicles in current_gameboard.check_for_moves():
            next_gameboard = Gameboard(config.GAMEBOARD_WIDTH, config.GAMEBOARD_HEIGHT, new_vehicles)
            # If the next state has not been visited yet
            if next_gameboard not in visited:
                # Check if the next state has solved the game
                if next_gameboard.has_solved():
                    end = time.time()
                    _, peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()

                    path = helpFunctions.trace_back_solution(visited, gameboard, current_gameboard)
                    path.append(next_gameboard)

                    return path, end-start, peak, expanded_nodes, len(path), None
                
                # If not solved, add the next state to the queue and mark it as visited
                queue.append(next_gameboard)
                visited[next_gameboard] = (next_gameboard, current_gameboard)

    # If no solution is found, return None and print statistics
    end = time.time()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    return None, end-start, peak, expanded_nodes, None, None

# UCS algorithm
def ucs_algorithm(game_board: Gameboard):
    #Start memory tracing
    tracemalloc.start()
    
    # Start calculating the time
    start = time.time()
    
    # Number of expanded nodes
    expanded_nodes = 0
    
    # Initialize the priority queue
    frontier = PriorityQueue()

    node_counter = 0 # Used to break ties in priority queue

    # Keep track of visited states to avoid cycles
    visited = {}
    
    # Push the initial state into the priority queue with cost 0
    frontier.put((0, node_counter, game_board))
    visited[game_board] = (0, game_board)
    
    while not frontier.empty():
        # Get the state with the lowest cost
        current_cost, _, current_board = frontier.get()

        if current_board in visited and current_cost > visited[current_board][0]:
            continue
        
        expanded_nodes += 1
        
        # If we reach the goal state i.e. solved, return the path
        if current_board.has_solved():
            # Final statistics for running time and peak memory usage
            end = time.time()
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            path = helpFunctions.trace_back_solution(visited, game_board, current_board)
            return path, end-start, peak, expanded_nodes, len(path), current_cost
        
        # Generate successors and their costs
        # Generate successors
        for new_vehicles in current_board.check_for_moves():
            new_game_board = Gameboard(config.GAMEBOARD_WIDTH, config.GAMEBOARD_HEIGHT, new_vehicles)
            
            # calculate new cost
            new_cost = current_cost
            for vehicle in new_vehicles:
                if vehicle not in current_board.vehicles:
                    new_cost += vehicle.length
                    break

            # Check if this state is new or has better priority than previous visit
            if new_game_board not in visited or new_cost < visited[new_game_board][0]:
                node_counter += 1
                frontier.put((new_cost, node_counter, new_game_board))
                visited[new_game_board] = (new_cost, new_game_board, current_board)
    
    # Statistics: If no solution is found
    
    # Final statistics for running time and peak memory usage
    end = time.time()
    current, peak = tracemalloc.get_traced_memory()
    
    tracemalloc.stop()
    # If no solution is found, return None
    return None, end-start, peak, expanded_nodes, None, None

# A* algorithm
def A_star_algorithm(game_board):
    """
    Solves the Rush Hour puzzle using A* search algorithm.
    
    Input:
        initial_board (Gameboard): The starting configuration of the Rush Hour game
        
    Output:
        Gameboard: The solved board configuration if found, None otherwise
    """
    start_time = time.time()
    tracemalloc.start()

    # Initialize priority queue for frontier nodes
    frontier = PriorityQueue()
    node_counter = 0 # Used to break ties in priority queue
    num_expanded_node = 0 # Used to count expanded node
    visited = {} # Dictionary to track visited states and their priorities

    # Calculate initial heuristic (number of vehicles blocking the target vehicle)
    heuristic_value_root = helpFunctions.heuristic_blocking_chain(game_board)

    # Add initial state to frontier
    frontier.put((heuristic_value_root, node_counter, game_board))
    visited[game_board] = (heuristic_value_root, game_board)

    while not frontier.empty():
        # Get the next node with lowest priority (f = g + h)
        current_priority, _, current_board = frontier.get()
        num_expanded_node += 1

        # Subtract heuristic to get actual path cost (g) from f score
        current_priority -= helpFunctions.heuristic_blocking_chain(current_board)

        # Check if current state is the solution
        if current_board.has_solved():
            end_time = time.time()
            _, peak = tracemalloc.get_traced_memory()

            tracemalloc.stop()
            path = helpFunctions.trace_back_solution(visited, game_board, current_board)
            return path, end_time-start_time, peak, num_expanded_node, len(path), current_priority
        
        # Generate all possible moves from current state
        for new_vehicles in current_board.check_for_moves():
            # Create new game board from this move configuration
            new_game_board = Gameboard(config.GAMEBOARD_WIDTH, config.GAMEBOARD_HEIGHT, new_vehicles)

            # Calculate new path cost (g)
            # Add vehicle length as cost when it moves
            new_priority = current_priority
            for vehicle in new_vehicles:
                if vehicle not in current_board.vehicles:
                    new_priority += vehicle.length 
                    break

            # Calculate new f score (f = g + h)
            new_priority += helpFunctions.heuristic_blocking_chain(new_game_board)

            # Check if this state is new or has better priority than previous visit
            if new_game_board not in visited or new_priority < visited[new_game_board][0]:
                node_counter += 1
                frontier.put((new_priority, node_counter, new_game_board))
                visited[new_game_board] = (new_priority, new_game_board, current_board)
    
    # if no solution is found, return None
    end_time = time.time()
    _, peak = tracemalloc.get_traced_memory()

    tracemalloc.stop()
    return None, end_time-start_time, peak, num_expanded_node, None, None