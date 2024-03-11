import cplex

def add_depot(old_d: list[list[int]]) -> None:
    new_d= old_d[0][:]
    for row, e in zip(old_d, new_d):
        row.append(e)
    
    old_d.append(new_d + [0])

def solve_problem(N, K, d):
    # Create MILP solver
    model = cplex.Cplex()

    # Create variables and give them names
    x_names = [[[f"x{i}_{j}_{k}" for k in range(K)] for j in range(N + 2)] for i in range(N + 2)]
    x = {}
    for i in range(N + 2):
        for j in range(N + 2):
            for k in range(K):
                x[(i, j, k)] = model.variables.add(names=[x_names[i][j][k]], types='B')[0]

    # Constraint: Each point is visited by exactly one vehicle
    for j in range(1, N + 1):
        model.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=[x[(i, j, k)] for i in range(N + 1) for k in range(K)], val=[1.0] * ((N + 1) * K))],
            senses="E",
            rhs=[1]
        )

    # Constraint: Each point is gone out by exactly one vehicle
    for i in range(1, N + 1):
        model.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=[x[(i, j, k)] for j in range(1, N + 2) for k in range(K)], val=[1.0] * ((N + 1) * K))],
            senses="E",
            rhs=[1]
        )

    # Constraint: Each vehicle starts and ends at point 0
    for k in range(K):
        start = cplex.SparsePair(ind=[x[(0, j, k)] for j in range(1, N + 1)], val=[1.0] * N)
        end = cplex.SparsePair(ind=[x[(i, N + 1, k)] for i in range(1, N + 1)], val=[1.0] * N)
        model.linear_constraints.add(lin_expr=[start], senses="E", rhs=[1])
        model.linear_constraints.add(lin_expr=[end], senses="E", rhs=[1])

    # Constraint: Vehicle cannot travel from point i to itself
    for i in range(N + 2):
        for k in range(K):
            model.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=[x[(i, i, k)]], val=[1.0])],
                senses="E",
                rhs=[0]
            )

   # Set objective to minimize total distance
    model.objective.set_sense(model.objective.sense.minimize)
    obj = [(x[(i, j, k)], d[i][j]) for i in range(N + 2) for j in range(N + 2) for k in range(K) if i != j]
    model.objective.set_linear(obj)

    # Solve the problem
    model.solve()

    # Print the optimal solution
    print("Total Distance:", model.solution.get_objective_value())

    for k in range(K):
        print('Vehicle', k + 1, ':')
        current_point = 0
        route = [0]
        while current_point != N + 1:
            for i in range(N + 2):
                if model.solution.get_values(x[(current_point, i, k)]) == 1:
                    current_point = i
                    if current_point == N + 1:
                        route.append(0)
                    else:
                        route.append(i)
                    break
        print(', '.join(map(str, route)))

if __name__ == '__main__':
    # Example usage
    N = 3
    K = 2
    d = [
        [0, 10, 20, 30],
        [10, 0, 25, 35],
        [20, 25, 0, 15],
        [30, 35, 15, 0]
    ]

    add_depot(d)

    solve_problem(N, K, d)
