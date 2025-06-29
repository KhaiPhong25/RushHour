from gameboard import Gameboard
import helpFunctions
import time
import resource
from queue import PriorityQueue
import psutil
import os
from collections import deque

# IDS algorithm

# BFS algorithm
def bfs_algorithm(gameboard: Gameboard):
    # Start calculating the time
    start = time.time()
    
    # Number of expanded nodes
    expanded_nodes = 0
    
    # Initialize the queue for BFS
    queue = deque()
    
    # Keep track of visited states to avoid cycles
    visited = set()

    # Start with the initial state of the gameboard
    start_state = gameboard.get_state()

    # If the initial state is already solved, return the solution path
    if gameboard.hasSolved(start_state):
        end = time.time()
        peak_memory_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
        
        print(f'Total runtime of the solution is {end - start} seconds')
        print(f'Peak memory usage is {peak_memory_usage} megabytes')
        print(f'Total expanded nodes is {expanded_nodes} nodes')
        
        return gameboard.get_solution_path(start_state)

    # Initialize the queue with the start state
    queue.append(start_state)
    visited.add(start_state)

    # While there are states in the queue, continue searching
    while queue:
        # Get the current state from the queue
        current_state = queue.popleft()
        # Incresing the number of expanded nodes
        expanded_nodes += 1
        # Generate successors for the current state
        for next_state in gameboard.get_successors(current_state):
            # If the new state has not been visited, add it to the queue, mark it as visited and check if it is the goal state
            if next_state not in visited:
                # If the new state is the goal state, return the solution path
                if gameboard.hasSolved(next_state):
                    end = time.time()
                    peak_memory_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
                    
                    print(f'Total runtime of the solution is {end - start} seconds')
                    print(f'Peak memory usage is {peak_memory_usage} megabytes')
                    print(f'Total expanded nodes is {expanded_nodes} nodes')
                    
                    return gameboard.get_solution_path(next_state)
            
                queue.append(next_state)
                visited.add(next_state)

    # If no solution is found, return None
    return None


# UCS algorithm
def ucs_algorithm(gameboard: Gameboard):
    # Get current process (?)
    process = psutil.Process(os.getpid())
    
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
    
    while not open_set.empty():
        # Get the state with the lowest cost
        current_cost, current_state = open_set.get()
        
        # If we reach the goal state i.e. solved, return the path
        if gameboard.hasSolved(current_state):
            # Final statistics for running time and peak memory usage
            end = time.time()
            peak_memory_bytes = process.memory_info().peak_wset
            peak_memory_mb = peak_memory_bytes / (1024 * 1024)

            # Display the statistics
            print(f'Total runtime of the solution is {end - start} seconds')
            print(f'Peak memory usage is {peak_memory_mb} megabytes')
            print(f'Total expanded nodes is {expanded_nodes} nodes')
            
            return gameboard.get_solution_path(current_state)
        
        # If this state has already been visited, skip it
        if current_state in visited:
            continue
        
        # Mark this state as visited
        visited.add(current_state)
        expanded_nodes += 1
        
        # Generate successors and their costs
        for move, next_state in gameboard.checkformoves(current_state):
            if next_state not in visited:
                new_cost = current_cost + gameboard.get_move_cost(move)
                open_set.put((new_cost, next_state))
    
    # Statistics: If no solution is found
    
    # Final statistics for running time and peak memory usage
    end = time.time()
    peak_memory_bytes = process.memory_info().peak_wset
    peak_memory_mb = peak_memory_bytes / (1024 * 1024)
    
    # Display the statistics
    print(f'Total runtime of the solution is {end - start} seconds')
    print(f'Peak memory usage is {peak_memory_mb} megabytes')
    print(f'Total expanded nodes is {expanded_nodes} nodes')
    
    # If no solution is found, return None
    return None


# A* algorithm