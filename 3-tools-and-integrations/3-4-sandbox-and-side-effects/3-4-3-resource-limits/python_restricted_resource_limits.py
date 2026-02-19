from RestrictedPython import compile_restricted
from RestrictedPython.Guards import safe_builtins


def execute_restricted(code: str):
    compiled = compile_restricted(code, "<string>", "exec")

    restricted_globals = {
        "__builtins__": safe_builtins
    }

    restricted_locals = {}

    exec(compiled, restricted_globals, restricted_locals)

    return restricted_locals


def main():
    safe_code = "result = 2 + 2"
    result = execute_restricted(safe_code)

    print(result)


if __name__ == "__main__":
    main()
