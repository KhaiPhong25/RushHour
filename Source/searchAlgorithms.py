from gameboard import Gameboard
import time
#import resource
from queue import PriorityQueue
from collections import deque
import helpFunctions
import tracemalloc
from helpFunctions import load_gameboard
from vehicle import Vehicle

# Depth-Limited Search (DLS) algorithm
def dls_algorithms(gameboard: Gameboard, limit):
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

    while frontier:
        # Pop the most recent gameboard
        current_gameboard, depth = frontier.pop()

        # Check if current gameboard is the goal state
        if current_gameboard.has_solved():
            end = time.time()

            print(f'Total runtime of the solution is {end - start} seconds')
            print(f'Total expanded nodes is {expanded_nodes} nodes')

            result_status = "success"
            return current_gameboard, result_status
        
        # Skip if depth exceeds the limit
        if depth > limit:
            result_status = "cutoff"
            continue

        # Skip already visited gameboards to avoid cycles
        state_id = hash(current_gameboard)
        if state_id in visited:
            continue
        
        visited[state_id] = (current_gameboard)
        
        # Increment expanded node count
        expanded_nodes += 1

        # Generate all possible moves from the current gameboard
        for vehicles in current_gameboard.check_for_moves():
            width = 6
            height = 6

            # Create a new gameboard for each move and add it to the frontier with increased depth
            next_gameboard = Gameboard(width, height, vehicles)
            frontier.append((next_gameboard, depth + 1))

    # Return failure if no solution was found within the limit
    return None, result_status

# Iterative Deepening Search (IDS) algorithm
def ids_algorithm(gameboard: Gameboard, max_depth):
    for depth in range(max_depth + 1):
        # Perform DLS with the current depth
        result, status = dls_algorithms(gameboard, depth)

        # Return result if a solution is found
        if status == "success":
            return result
        
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

    # If the start state is already solved, return the solution path
    if gameboard.has_solved():
        end = time.time()
        current, peak = tracemalloc.get_traced_memory()
        print(f'Total runtime of the solution is {end - start} seconds')
        print(f'Peak memory usage is {peak / (1024 * 1024)} megabytes')
        print(f'Total expanded nodes is {expanded_nodes} nodes')
        tracemalloc.stop()
        return gameboard.get_solution_path()
    
    # Add the start state to the queue and mark it as visited
    queue.append(gameboard)
    visited[hash(gameboard)] = gameboard

    # While there are states to explore in the queue
    while queue:
        # Get the current state from the queue and increase the expanded nodes count
        current_gameboard = queue.popleft()
        expanded_nodes += 1

        # Get the successors of the current state
        for child in current_gameboard.check_for_moves():
            next_gameboard = Gameboard(gameboard.width, gameboard.height, child)
            # If the next state has not been visited yet
            if hash(next_gameboard) not in visited:
                # Check if the next state has solved the game
                if next_gameboard.has_solved():
                    end = time.time()
                    current, peak = tracemalloc.get_traced_memory()
                    print(f'Total runtime of the solution is {end - start} seconds')
                    print(f'Peak memory usage is {peak / (1024 * 1024)} megabytes')
                    print(f'Total expanded nodes is {expanded_nodes} nodes')
                    tracemalloc.stop()
                    return next_gameboard.get_solution_path()
                
                # If not solved, add the next state to the queue and mark it as visited
                queue.append(next_gameboard)
                visited[hash(next_gameboard)] = next_gameboard

    # If no solution is found, return None and print statistics
    end = time.time()
    current, peak = tracemalloc.get_traced_memory()
    print(f'Total runtime of the solution is {end - start} seconds')
    print(f'Peak memory usage is {peak / (1024 * 1024)} megabytes')
    print(f'Total expanded nodes is {expanded_nodes} nodes')
    tracemalloc.stop()
    
    return None

# UCS algorithm
def ucs_algorithm(gameboard: Gameboard):
    #Start memory tracing
    tracemalloc.start()
    
    # Start calculating the time
    start = time.time()
    
    # Number of expanded nodes
    expanded_nodes = 0
    
    # Initialize the priority queue
    open_set = PriorityQueue()
    
    # Start with the initial state of the gameboard
    start_state = gameboard.get_state()
    
    # Push the initial state into the priority queue with cost 0
    open_set.put((0, start_state))
    
    # Keep track of visited states to avoid cycles
    visited = set()
    
    cost_so_far = {start_state: 0}
    
    while open_set:
        # Get the state with the lowest cost
        current_cost, current_state = open_set.get()
        
        # Reconstruct a Gameboard from the current_state
        vehicles = [Vehicle(*v) for v in current_state]
        current_board = Gameboard(gameboard.width, gameboard.height, vehicles)
        
        # If we reach the goal state i.e. solved, return the path
        if current_board.has_solved():
            # Final statistics for running time and peak memory usage
            end = time.time()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            # Display the statistics
            print(f'Total runtime of the solution is {end - start} seconds')
            print(f'Peak memory usage is {peak / (1024.0 * 1024.0)} megabytes')
            print(f'Total expanded nodes is {expanded_nodes} nodes')
            
            return current_state, current_cost
        
        # If this state has already been visited, skip it
        if current_state in visited:
            continue
        
        # Mark this state as visited
        visited.add(current_state)
        expanded_nodes += 1
        
        # Generate successors and their costs
        # Generate successors
        for new_vehicles in current_board.check_for_moves():
            next_state = tuple((v.id, v.x, v.y, v.orientation) for v in new_vehicles)
            if next_state in visited:
                continue  # Skip already visited states
            
            moved_vehicle = next(v for v in new_vehicles if v not in vehicles)
            move_cost = moved_vehicle.length
            new_cost = current_cost + move_cost

            if next_state not in cost_so_far or new_cost < cost_so_far[next_state]:
                cost_so_far[next_state] = new_cost
                open_set.put((new_cost, next_state))
    
    # Statistics: If no solution is found
    
    # Final statistics for running time and peak memory usage
    end = time.time()
    current, peak = tracemalloc.get_traced_memory()
    
    # Display the statistics
    print(f'Total runtime of the solution is {end - start} seconds')
    print(f'Peak memory usage is {peak / (1024.0 * 1024.0)} megabytes')
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
            print(f"Solution found in {end_time - start_time:.2f} seconds")
            print(f"Peak memory usage is {peak / (1024 * 1024):.2f} MB")
            print(f"Total expanded node: {num_expanded_node}")
            return helpFunctions.trace_back_solution(visited, game_board, current_board)
        
        # Generate all possible moves from current state
        for move in current_board.check_for_moves():
            # Create new game board from this move configuration
            new_game_board = Gameboard(game_board.width, game_board.height, move)

            # Calculate new path cost (g)
            # Add vehicle length as cost when it moves
            new_priority = current_priority
            for i in range (0, len(move)):
                if move[i] != current_board.vehicles[i]:
                    new_priority += move[i].length 
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
    print(f"Solution found in {end_time - start_time:.2f} seconds")
    print(f"Peak memory usage is {peak / (1024 * 1024):.2f} MB")
    print(f"Total expanded node: {num_expanded_node}")

    return None

# test case
filename = "Map/gameboard1.json"
gameboard = helpFunctions.load_gameboard(filename)
print('\n \n')
A_star_algorithm(gameboard)
print(dls_algorithms(gameboard, 10000))
print(bfs_algorithm(gameboard))
#helpFunctions.print_solution_path(A_star_algorithm(gameboard))