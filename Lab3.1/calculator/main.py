import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from calculator.calc_lexer import CalcLexerError, tokenize
from calculator.evaluator import EvaluationError, evaluate
from calculator.table_loader import TableLoadError, load_table
from grammar_lang.parser import ParseError, parse_tokens
from grammar_lang.tree import print_tree, write_dot_file

class CommandLineError(Exception):
    pass

def parse_command_line(arguments):
    expression = None
    show_tree = False
    dot_path = None
    index = 0
    while index < len(arguments):
        argument = arguments[index]
        if argument == "--tree":
            show_tree = True
            index += 1
        elif argument == "--dot":
            if index + 1 >= len(arguments):
                raise CommandLineError("Option --dot requires a file path")
            dot_path = arguments[index + 1]
            index += 2
        elif argument.startswith("--"):
            raise CommandLineError("Unknown option: {0}".format(argument))
        elif expression is None:
            expression = argument
            index += 1
        else:
            raise CommandLineError("Unexpected argument: {0}".format(argument))
    if expression is None:
        raise CommandLineError("Expression must be specified")
    return expression, show_tree, dot_path

def main():
    try:
        expression, show_tree, dot_path = parse_command_line(sys.argv[1:])
        table_module = load_table()
        tokens = tokenize(expression)
        root = parse_tokens(tokens, table_module)
        result = evaluate(root)
        if show_tree:
            print_tree(root)
        if dot_path is not None:
            write_dot_file(root, dot_path)
        print(result)
    except CommandLineError as error:
        print(error)
        sys.exit(1)
    except (TableLoadError, CalcLexerError, ParseError, EvaluationError) as error:
        print(error)
        sys.exit(1)

if __name__ == "__main__":
    main()
