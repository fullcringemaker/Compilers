class TableLoadError(Exception):
    pass

def load_table():
    try:
        from output import calculator_table
    except ImportError as error:
        raise TableLoadError(
            "Table file output/calculator_table.py was not found. "
            "Generate it first with generator.py"
        ) from error
    if not hasattr(calculator_table, "PARSE_TABLE"):
        raise TableLoadError("File output/calculator_table.py does not contain PARSE_TABLE")

    return calculator_table