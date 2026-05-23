from itertools import product

class TruthTableBuilder:
    def __init__(self, ast) -> None:
        self.ast = ast
        self.variables = sorted(ast.get_vars())

    def build(self):
        table = []
        for values in product([0, 1], repeat=len(self.variables)):
            context = dict(zip(self.variables, values))
            result = self.ast.evaluate(context)
            table.append((context, result))
        return self.variables, table

def build_truth_table(ast):
    return TruthTableBuilder(ast).build()