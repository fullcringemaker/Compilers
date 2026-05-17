class EvaluationError(Exception):
    pass

def child(node, index):
    try:
        return node.children[index]
    except IndexError:
        raise EvaluationError("invalid parse tree near {0}".format(node.name))

def is_epsilon(node):
    return len(node.children) == 1 and node.children[0].kind == "epsilon"

def evaluate(root):
    if root.name != "E":
        raise EvaluationError("calculator parse tree root must be E")
    return eval_E(root)

def eval_E(node):
    value = eval_T(child(node, 0))
    return eval_E1(child(node, 1), value)

def eval_E1(node, accumulated):
    if is_epsilon(node):
        return accumulated
    term_value = eval_T(child(node, 1))
    return eval_E1(child(node, 2), accumulated + term_value)

def eval_T(node):
    value = eval_F(child(node, 0))
    return eval_T1(child(node, 1), value)

def eval_T1(node, accumulated):
    if is_epsilon(node):
        return accumulated
    factor_value = eval_F(child(node, 1))
    return eval_T1(child(node, 2), accumulated * factor_value)

def eval_F(node):
    first = child(node, 0)
    if first.name == "n":
        return first.value
    return eval_E(child(node, 1))
