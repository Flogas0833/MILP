import cplex

def solve(N, c, a, f, m, A, C):
    # Create MILP solver
    model = cplex.Cplex()

    # Create variables 
    x_names = [f"x{i}" for i in range(N)]
    x = {}
    for i in range(N):
        x[i] = model.variables.add(names=[x_names[i]], types='C')[0]
    
    # Constraint: limited fund
    model.linear_constraints.add(
        lin_expr=[cplex.SparsePair(ind=[x[i] for i in range(N)], val=[c[i] for i in range(N)])],
        senses="L",
        rhs=[C]
    )

    # Constraint: limited space
    model.linear_constraints.add(
        lin_expr=[cplex.SparsePair(ind=[x[i] for i in range(N)], val=[a[i] for i in range(N)])],
        senses="L",
        rhs=[A]
    )

    # Constraint: produce at least m product
    for i in range(N):
        model.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=[x[i]], val=[1.0])],
            senses="G",
            rhs=[m[i]]
        )
    
    # Set objective to maximize profit
    model.objective.set_sense(model.objective.sense.maximize)
    obj = [(x[i], f[i]) for i in range(N)]
    model.objective.set_linear(obj)

    # Solve the problem
    model.solve()

    # Print optimal solution
    print("profit: ", model.solution.get_objective_value())
    for i in range(N):
        print(f"Product {i+1}: {model.solution.get_values(x[i])}")

if __name__ == '__main__':
    # Example usage
    N = 10
    c = [20, 30, 15, 25, 10, 50, 40, 45, 35, 60]
    a = [3, 2, 4, 1, 5, 2, 3, 4, 5, 2]
    f = [40, 35, 50, 45, 60, 55, 65, 70, 75, 80] 
    m = [2, 1, 3, 2, 1, 4, 3, 2, 1, 5]  
    A = 100
    C = 1000

    solve(N, c, a, f, m, A, C)
