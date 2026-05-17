import os
import sys

from grammar_lang.lexer import LexerError, tokenize
from grammar_lang.parser import ParseError, parse_tokens
from grammar_lang.extractor import GrammarError, grammar_from_tree, precheck_start_count
from grammar_lang.first_follow import LL1ConflictError, build_parse_table, compute_first, compute_follow
from grammar_lang.codegen import write_python_table

class CommandLineError(Exception):
    pass

class GeneratorTableError(Exception):
    pass

def read_text(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()

def get_generated_table_path():
    return os.path.abspath(os.path.join("grammar_lang", "generated_table.py"))

def is_generating_table_for_input_language(output_path):
    current_output_path = os.path.abspath(output_path)
    generated_path = get_generated_table_path()
    current_output_path = os.path.normcase(current_output_path)
    generated_path = os.path.normcase(generated_path)
    return current_output_path == generated_path

def generated_table_exists():
    return os.path.exists(get_generated_table_path())

def load_table_module(output_path):
    if is_generating_table_for_input_language(output_path):
        from grammar_lang import handwritten_table
        return handwritten_table
    if generated_table_exists():
        try:
            from grammar_lang import generated_table
        except ImportError as error:
            raise GeneratorTableError(
                "File grammar_lang/generated_table.py exists but could not be imported."
            ) from error
        return generated_table
    from grammar_lang import handwritten_table
    return handwritten_table

def prepare_output_directory(output_path):
    directory = os.path.dirname(output_path)
    if directory != "":
        os.makedirs(directory, exist_ok=True)

def build_table(input_path, output_path):
    text = read_text(input_path)
    tokens = tokenize(text)
    precheck_start_count(tokens)
    table_module = load_table_module(output_path)
    tree = parse_tokens(tokens, table_module)
    grammar = grammar_from_tree(tree)
    first = compute_first(grammar)
    follow = compute_follow(grammar, first)
    parse_table = build_parse_table(grammar, first, follow)
    prepare_output_directory(output_path)
    write_python_table(output_path, grammar, first, follow, parse_table)

    return output_path

def parse_command_line(arguments):
    if len(arguments) != 2:
        raise CommandLineError("Input file and output file must be specified")
    input_path = arguments[0]
    output_path = arguments[1]
    if input_path.startswith("--"):
        raise CommandLineError("Unexpected option: {0}".format(input_path))
    if output_path.startswith("--"):
        raise CommandLineError("Unexpected option: {0}".format(output_path))
    return input_path, output_path

def main():
    try:
        input_path, output_path = parse_command_line(sys.argv[1:])
        generated_path = build_table(input_path, output_path)
        print("Generated table:", generated_path)
    except CommandLineError as error:
        print(error)
        sys.exit(1)
    except (OSError, GeneratorTableError, LexerError, ParseError, GrammarError, LL1ConflictError) as error:
        print(error)
        sys.exit(1)

if __name__ == "__main__":
    main()