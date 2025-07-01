from gameboard import Gameboard
from vehicle import Vehicle
from queue import PriorityQueue
from collections import deque
import helpFunctions
import tracemalloc
import time
import config

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

    # Initialize result status
    result_status = "failure"

    # Add the initial gameboard and its depth (0) to the frontier
    frontier.append((gameboard, 0))
    initial_id = hash(gameboard)
    visited[initial_id] = (gameboard, None)  # No parent for root

    # Early goal check
    if gameboard.has_solved():
        end = time.time()
        _, peak = tracemalloc.get_traced_memory()

        print(f'Total runtime of the solution is {end - start:.2f} seconds')
        print(f'Peak memory usage is {peak / (1024 * 1024):.2f} MB')
        print(f'Total expanded nodes {expanded_nodes} nodes')
        tracemalloc.stop()

        result_status = "success"
        path = helpFunctions.trace_back_solution(visited, gameboard, gameboard)

        return path, result_status

    while frontier:
        # Pop the most recent gameboard
        current_gameboard, depth = frontier.pop()

        # Check if current gameboard is the goal state
        if current_gameboard.has_solved():
            end = time.time()
            _, peak = tracemalloc.get_traced_memory()

            print(f'Total runtime of the solution is {end - start:.2f} seconds')
            print(f'Peak memory usage is {peak / (1024 * 1024):.2f} MB')
            print(f'Total expanded nodes is {expanded_nodes} nodes')
            tracemalloc.stop()

            result_status = "success"
            path = helpFunctions.trace_back_solution(visited, gameboard, current_gameboard)

            return path, result_status
        
        # Skip if depth exceeds the limit
        if depth >= limit:
            result_status = "cutoff"
            continue
        
        # Increment expanded node count
        expanded_nodes += 1

        # Get the successors of the current state
        for new_vehicles in current_gameboard.check_for_moves():
            next_gameboard = Gameboard(config.WIDTH, config.HEIGHT, new_vehicles)
            next_id = hash(next_gameboard)

            if next_id not in visited:
                visited[next_id] = (next_gameboard, current_gameboard)
                frontier.append((next_gameboard, depth + 1))

    # Return failure if no solution was found within the limit
    return None, result_status

# Iterative Deepening Search (IDS) algorithm
def ids_algorithm(gameboard: Gameboard, max_depth):
    for depth in range(max_depth + 1):
        # Perform DLS with the current depth
        solution, status = dls_algorithm(gameboard, depth)

        # Return result if a solution is found
        if status == "success":
            return solution
        
        # If DLS failed completely, break out
        elif status == "failure":
            break  

        # If DLS was cut off (incomplete due to depth limit), try next depth
        elif status == "cutoff":
            continue  

    # Return None if no solution was found after all depth levels
    return None

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
    visited[hash(gameboard)] = (None, gameboard)

    # If the start state is already solved, return the solution path
    if gameboard.has_solved():
        end = time.time()
        _, peak = tracemalloc.get_traced_memory()
        print(f'Total runtime of the solution is {end - start:.2f} seconds')
        print(f'Peak memory usage is {peak / (1024 * 1024):.2f} MB')
        print(f'Total expanded nodes is {expanded_nodes} nodes')
        tracemalloc.stop()

        return helpFunctions.trace_back_solution(visited, gameboard, gameboard)

    # While there are states to explore in the queue
    while queue:
        # Get the current state from the queue and increase the expanded nodes count
        current_gameboard = queue.popleft()
        expanded_nodes += 1

        # Get the successors of the current state
        for new_vehicles in current_gameboard.check_for_moves():
            next_gameboard = Gameboard(config.WIDTH, config.HEIGHT, new_vehicles)
            # If the next state has not been visited yet
            if hash(next_gameboard) not in visited:
                # Check if the next state has solved the game
                if next_gameboard.has_solved():
                    end = time.time()
                    _, peak = tracemalloc.get_traced_memory()
                    print(f'Total runtime of the solution is {end - start:.2f} seconds')
                    print(f'Peak memory usage is {peak / (1024 * 1024):.2f} MB')
                    print(f'Total expanded nodes is {expanded_nodes} nodes')
                    tracemalloc.stop()

                    path = helpFunctions.trace_back_solution(visited, gameboard, current_gameboard)
                    path.append(next_gameboard)

                    return path
                
                # If not solved, add the next state to the queue and mark it as visited
                queue.append(next_gameboard)
                visited[hash(next_gameboard)] = (next_gameboard, current_gameboard)

    # If no solution is found, return None and print statistics
    end = time.time()
    _, peak = tracemalloc.get_traced_memory()
    print(f'Total runtime of the solution is {end - start:.2f} seconds')
    print(f'Peak memory usage is {peak / (1024 * 1024):.2f} MB')
    print(f'Total expanded nodes is {expanded_nodes} nodes')
    tracemalloc.stop()
    
    return None

# UCS algorithm
def ucs_algorithm(game_board: Gameboard):
    #Start memory tracing
    tracemalloc.start()
    
    # Start calculating the time
    start = time.time()
    
    # Number of expanded nodes
    expanded_nodes = 0
    
    # Initialize the priority queue
    open_set = PriorityQueue()

    node_counter = 0 # Used to break ties in priority queue

    # Keep track of visited states to avoid cycles
    visited = {}
    
    # Push the initial state into the priority queue with cost 0
    open_set.put((0, node_counter, game_board))
    visited[hash(game_board)] = (0, game_board)
    
    while open_set:
        # Get the state with the lowest cost
        current_cost, _, current_board = open_set.get()
        expanded_nodes += 1
        
        # If we reach the goal state i.e. solved, return the path
        if current_board.has_solved():
            # Final statistics for running time and peak memory usage
            end = time.time()
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            # Display the statistics
            print(f'Total runtime of the solution is {end - start:.2f} seconds')
            print(f'Peak memory usage is {peak / (1024.0 * 1024.0):.2f} MB')
            print(f'Total expanded nodes is {expanded_nodes} nodes')
            
            path = helpFunctions.trace_back_solution(visited, game_board, current_board)
            return path
        
        # Generate successors and their costs
        # Generate successors
        for new_vehicles in current_board.check_for_moves():
            new_game_board = Gameboard(config.WIDTH, config.HEIGHT, new_vehicles)
            
            # calculate new cost
            new_cost = current_cost
            for vehicle in new_vehicles:
                if vehicle not in current_board.vehicles:
                    new_cost += vehicle.length
                    break

            # Check if this state is new or has better priority than previous visit
            if hash(new_game_board) not in visited or new_cost < visited[hash(new_game_board)][0]:
                node_counter += 1
                open_set.put((new_cost, node_counter, new_game_board))
                visited[hash(new_game_board)] = (new_cost, new_game_board, current_board)
    
    # Statistics: If no solution is found
    
    # Final statistics for running time and peak memory usage
    end = time.time()
    current, peak = tracemalloc.get_traced_memory()
    
    # Display the statistics
    print(f'Total runtime of the solution is {end - start:.2f} seconds')
    print(f'Peak memory usage is {peak / (1024.0 * 1024.0):.2f} MB')
    print(f'Total expanded nodes is {expanded_nodes} nodes')
    
    # If no solution is found, return None
    return None

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
    heuristic_value_root = helpFunctions.number_blocking_vehicle(game_board)

    # Add initial state to frontier
    frontier.put((heuristic_value_root, node_counter, game_board))
    visited[hash(game_board)] = (heuristic_value_root, game_board)

    while not frontier.empty():
        # Get the next node with lowest priority (f = g + h)
        current_priority, _, current_board = frontier.get()
        num_expanded_node += 1

        # Subtract heuristic to get actual path cost (g) from f score
        current_priority -= helpFunctions.number_blocking_vehicle(current_board)

        # Check if current state is the solution
        if current_board.has_solved():
            end_time = time.time()
            _, peak = tracemalloc.get_traced_memory()
            print(f"Total runtime of the solution is {end_time - start_time:.2f} seconds")
            print(f"Peak memory usage is {peak / (1024 * 1024):.2f} MB")
            print(f"Total expanded node is {num_expanded_node} nodes")

            path = helpFunctions.trace_back_solution(visited, game_board, current_board)
            return path
        
        # Generate all possible moves from current state
        for new_vehicles in current_board.check_for_moves():
            # Create new game board from this move configuration
            new_game_board = Gameboard(config.WIDTH, config.HEIGHT, new_vehicles)

            # Calculate new path cost (g)
            # Add vehicle length as cost when it moves
            new_priority = current_priority
            for vehicle in new_vehicles:
                if vehicle not in current_board.vehicles:
                    new_priority += vehicle.length 
                    break

            # Calculate new f score (f = g + h)
            new_priority += helpFunctions.number_blocking_vehicle(new_game_board)

            # Check if this state is new or has better priority than previous visit
            if hash(new_game_board) not in visited or new_priority < visited[hash(new_game_board)][0]:
                node_counter += 1
                frontier.put((new_priority, node_counter, new_game_board))
                visited[hash(new_game_board)] = (new_priority, new_game_board, current_board)
    
    # if no solution is found, return None
    end_time = time.time()
    _, peak = tracemalloc.get_traced_memory()
    print(f"Total runtime of the solution is {end_time - start_time:.2f} seconds")
    print(f"Peak memory usage is {peak / (1024 * 1024):.2f} MB")
    print(f"Total expanded node is {num_expanded_node} nodes")

    return None

# test case
filename = "Map/gameboard2.json"
gameboard = helpFunctions.load_gameboard(filename)
print(gameboard)
print('\n \n')
#A_star_algorithm(gameboard)
#print(ids_algorithm(gameboard, 10000))
#print(bfs_algorithm(gameboard))
# print(ucs_algorithm(gameboard))
helpFunctions.print_solution_path(ids_algorithm(gameboard, 1000))
#print(ucs_algorithm(gameboard))
#helpFunctions.print_solution_path(bfs_algorithm(gameboard))
