class TreeNode:
    def __init__(self, name, kind="nonterminal", value=None, coord=None):
        self.name = name
        self.kind = kind
        self.value = value
        self.coord = coord
        self.children = []

    def add_child(self, child):
        self.children.append(child)

def print_tree(node, indent=0):
    prefix = "  " * indent
    if node.kind == "token":
        print(prefix + "{0}: {1}".format(node.name, node.value))
    elif node.kind == "epsilon":
        print(prefix + "ε")
    else:
        print(prefix + node.name)
    for child in node.children:
        print_tree(child, indent + 1)

def escape_dot_label(text):
    return str(text).replace("\\", "\\\\").replace('"', '\\"')

def node_label(node):
    if node.kind == "token":
        return "{0}: {1}".format(node.name, node.value)
    return node.name

def build_dot_lines(root):
    lines = ["digraph ParseTree {"]
    lines.append("  rankdir=TB;")
    lines.append("  node [shape=box];")

    node_ids = {}
    counter = [0]

    def visit(node):
        node_id = "n{0}".format(counter[0])
        counter[0] += 1
        node_ids[id(node)] = node_id
        lines.append('  {0} [label="{1}"];'.format(node_id, escape_dot_label(node_label(node))))
        for child in node.children:
            visit(child)
            child_id = node_ids[id(child)]
            lines.append("  {0} -> {1};".format(node_id, child_id))
        if len(node.children) >= 2:
            chain = " -> ".join(node_ids[id(child)] for child in node.children)
            lines.append("  {{ rank=same; {0} [style=invis] }}".format(chain))
    visit(root)
    lines.append("}")
    return lines

def write_dot_file(root, path):
    with open(path, "w", encoding="utf-8") as file:
        file.write("\n".join(build_dot_lines(root)))
        file.write("\n")