import networkx as nx

from docplex.mp.model import Model

def solve(M: int, N: int, G: nx.DiGraph, W: list[list[int]], D: int, cost: list[int]):
    # Create MILP solver
    model = Model(name = 'Scheduling')

    # x[i, n] = 1: processor n do task i
    x = model.binary_var_matrix(M, N, name = 'x')

    # ST[i]: time starting task i
    ST = model.continuous_var_list(M, lb = 0, ub = D, name = 'ST')

    # FT[i]: time finishing task i
    FT = model.continuous_var_list(M, lb = 0, ub = D, name = 'FT')

    # same[i, j] = 1: i, j in the same processor
    same = model.binary_var_matrix(M, M, name = 'same')

    big_M = 1e4

    # Constraint: Each task is done once
    for i in range(M):
        done = model.sum_vars(x[i, n] for n in range(N))
        model.add_constraint(done == 1)

    # if task i, j in the same processor
    for i in range(M):
        for j in range(M):
            for n in range(N):
                model.add_constraint(same[i, j] >= x[i, n] + x[j, n] - 1)
                model.add_constraint(1 - same[i, j] >= x[i, n] - x[j, n])
                model.add_constraint(1 - same[i, j] >= x[j, n] - x[i, n])

    # Constraint: Task time
    for i in range(M):
        for n in range(N):
            model.add_constraint(FT[i] - ST[i] >= W[n][i] * x[i, n])

    # Constraint: If i, j in the same processor, can only do task after finish the condition tasks
    for i, j in G.edges:
        model.add_constraint(ST[j] - FT[i] >= big_M * (same[i, j] - 1))

    # Constraint: Each processor cannot do 2 task each time
    time = model.continuous_var_matrix(M, M, name = 'time') # max(ST[j] - FT[i], ST[i] - FT[j])
    b =  model.binary_var_matrix(M, M, name = 'b') # binary var for cases
    for i in range(M):
        for j in range(M):
            if j != i:
                # if ST[j] - FT[i] >= 0 then b = 0
                model.add_constraint(ST[j] - FT[i] >= -big_M * b[i, j])
                # if ST[i] - FT[j] >= 0 then b = 1
                model.add_constraint(ST[i] - FT[j] >= big_M * (b[i, j] - 1))
                # caculate max(ST[j] - FT[i], ST[i] - FT[j])
                model.add_constraint(time[i, j] >= ST[j] - FT[i])
                model.add_constraint(time[i, j] >= ST[i] - FT[j])
                model.add_constraint(time[i, j] <= ST[j] - FT[i] + big_M * b[i, j])
                model.add_constraint(time[i, j] <= ST[i] - FT[j] + big_M * (1 - b[i, j]))
                # Main constraint
                model.add_constraint(time[i, j] >= big_M * (same[i, j] - 1))

    # Constraint: If i, j in different processors, can only do task after data transfer time
    for i, j, weight in G.edges(data = True):
        model.add_constraint(ST[j] - FT[i] >= weight['weight'] - big_M * same[i, j])

    # Set objective to minimize execution cost
    Execution_cost = model.sum(cost[n] * W[n][i] * x[i, n] for i in range(M) for n in range(N))
    model.minimize(Execution_cost)

    # Solve 
    solution = model.solve()

    # Print optimal solution
    if solution:
        print("Execution cost:", model.objective_value)
        for n in range(N):
            print(f"processor {n + 1}:")
            task = {}
            for i in range(M):
                if x[i, n].solution_value >= 0.9:
                    task[i] = ST[i].solution_value
            sorted_task = sorted(task.keys(), key = lambda x: task[x])
            for index in sorted_task:
                print(f"task {index + 1}: {ST[index].solution_value} -> {FT[index].solution_value}")
    else:
        print("No feasible solution")

if __name__ == '__main__':
    # Example usage
    M = 8
    N = 3
    G = nx.DiGraph()
    G.add_nodes_from(list(range(M)))
    G.add_edge(0, 1, weight = 2)
    G.add_edge(0, 2, weight = 3)
    G.add_edge(0, 5, weight = 3)
    G.add_edge(1, 3, weight = 1)
    G.add_edge(1, 4, weight = 4)
    G.add_edge(1, 6, weight = 5)
    G.add_edge(2, 4, weight = 3)
    G.add_edge(2, 6, weight = 7)
    G.add_edge(3, 5, weight = 2)
    G.add_edge(3, 7, weight = 5)
    G.add_edge(4, 5, weight = 1)
    G.add_edge(4, 6, weight = 3)
    W = [
        [4, 1, 3, 2, 4, 3, 5, 5],
        [3, 1, 3, 3, 2, 1, 2, 6],
        [3, 4, 2, 2, 3, 3, 7, 6]
    ]
    D = 18
    cost = [6, 8, 5]

    solve(M, N, G, W, D, cost)
