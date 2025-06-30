from gameboard import Gameboard
import time
from queue import PriorityQueue
from collections import deque
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
    visited = set()

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
        if current_gameboard in visited:
            continue
        
        visited.add(current_gameboard)
        
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
    visited = set()

    # Start with the initial state of the gameboard
    #start_state = gameboard.get_state()

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
    visited.add(gameboard)

    # While there are states to explore in the queue
    while queue:
        # Get the current state from the queue and increase the expanded nodes count
        current_gameboard = queue.popleft()
        expanded_nodes += 1

        # Get the successors of the current state
        for child in current_gameboard.check_for_moves():
            next_gameboard = Gameboard(gameboard.width, gameboard.height, child)
            # If the next state has not been visited yet
            if next_gameboard.get_state() not in visited:
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
                visited.add(next_gameboard)

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