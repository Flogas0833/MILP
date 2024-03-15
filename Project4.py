import cplex

def add_depot(old_d: list[list[int]]) -> None:
    new_d= old_d[0][:]
    for row, e in zip(old_d, new_d):
        row.append(e)
    
    old_d.append(new_d + [0])

def solve(M, N, Q, q, d):
    # Create MILP solver
    model = cplex.Cplex()

    # Create variables
    x_names = [[f"x{i}_{j}" for j in range(M + 2)] for i in range(M + 2)]
    x = {}
    for i in range(M + 2):
        for j in range(M + 2):
            x[(i, j)] = model.variables.add(names=[x_names[i][j]], types='B')[0]

    # Constraint: Each point is visited at most once
    for j in range(1, M + 1):
        model.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=[x[(i, j)] for i in range(M + 1)], val=[1.0] * (M + 1))],
            senses="L",
            rhs=[1]
        )

    # Constraint: Each point is gone out at most once
    for i in range(1, M + 1):
        model.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=[x[(i, j)] for j in range(1, M + 2)], val=[1.0] * (M + 1))],
            senses="L",
            rhs=[1]
        )

    # Constraint: Staff start and end his trip at 0
    start = cplex.SparsePair(ind=[x[(0, j)] for j in range(1, M + 1)], val=[1.0] * M)
    end = cplex.SparsePair(ind=[x[(i, M + 1)] for i in range(1, M + 1)], val=[1.0] * M)
    model.linear_constraints.add(lin_expr=[start], senses="E", rhs=[1])
    model.linear_constraints.add(lin_expr=[end], senses="E", rhs=[1])

    # Constraint: Staff cannot travel from point i to itself
    for i in range(M + 2):
        model.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=[x[(i, i)]], val=[1.0])],
            senses="E",
            rhs=[0]
        )
    
    # Constraint: Staff take enough goods
    for t in range(N):
        model.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=[x[(i, j)] for i in range(M + 1) for j in range(M + 1)], val=[Q[t][j]] * (M + 1) * (M + 1))],
            senses="L",
            rhs=[q[t]]
        )

    # Set objective to minimize total distance
    model.objective.set_sense(model.objective.sense.minimize)
    obj = [(x[(i, j)], d[i][j]) for i in range(M + 2) for j in range(M + 2) if i != j]
    model.objective.set_linear(obj)

    # Solve the problem
    model.solve()

    # Print the optimal solution
    print("Total Distance:", model.solution.get_objective_value())

    current_point = 0
    route = [0]
    while current_point != M+ 1:
        for i in range(M + 2):
            if model.solution.get_values(x[(current_point, i)]) == 1:
                current_point = i
                if current_point == M + 1:
                    route.append(0)
                else:
                    route.append(i)
                break
    print(', '.join(map(str, route)))

if __name__ == '__main__':
    # Example usage
    M = 3
    N = 2
    Q = [
        [0, 1, 2, 0],
        [0, 2, 1, 1],
    ]
    q = [2, 3]
    d = [
    [0, 2, 4, 6],
    [2, 0, 2, 4],
    [4, 2, 0, 2],
    [6, 4, 2, 0]
    ]

    add_depot(d)

    solve(M, N, Q, q, d)
