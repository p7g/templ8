class _EOF(Exception):
    pass


class TemplateSyntaxError(Exception):
    pass


def compile(template_str, filename="<template>", indentation="    "):
    lines = []
    indent = 0
    i = 0
    skip_next_newline = False

    def push_line(code):
        lines.append(indentation * indent + code)

    def enter_block():
        nonlocal indent
        indent += 1

    def leave_block():
        nonlocal indent
        indent -= 1
        if indent < 0:
            raise TemplateSyntaxError("Extraneous 'end'")

    def next():
        nonlocal i
        if i >= len(template_str):
            raise _EOF
        c = template_str[i]
        i += 1
        return c

    def peek(n=0):
        if i + n >= len(template_str):
            raise _EOF
        return template_str[i + n]

    def skipspaces():
        had_spaces = False
        while peek().isspace():
            had_spaces = True
            next()
        return had_spaces

    push_line("def evaluate_template(context):")
    enter_block()
    push_line("_buf = []")
    push_line("def emit(text):")
    enter_block()
    push_line("_buf.append(text)")
    leave_block()

    emit_buf = ""

    while i < len(template_str):
        c = next()

        if skip_next_newline and c == "\n":
            skip_next_newline = False
            continue

        try:
            if c == "\\" and peek() == "{" and peek(1) == "{":
                next()
                next()
                emit_buf += "{{"
            elif c == "{" and next() == "{":
                if emit_buf:
                    push_line(f"emit({repr(emit_buf)})")
                    emit_buf = ""

                if peek() == "=":
                    is_expr = True
                    next()
                else:
                    is_expr = False
                python_str = ""

                while True:
                    had_spaces = skipspaces()
                    c = next()
                    if c == "\\" and peek() == "}" and peek(1) == "}":
                        next()
                        next()
                        python_str += "}}"
                        continue
                    elif c == "}" and peek() == "}":
                        next()
                        if python_str == "end":
                            leave_block()
                            skip_next_newline = True
                        elif is_expr:
                            push_line(f"emit(str({python_str}))")
                        else:
                            push_line(python_str)
                            if python_str[-1] == ":":
                                enter_block()
                                skip_next_newline = True
                        break
                    if had_spaces and python_str:
                        python_str += " "
                    python_str += c
            else:
                emit_buf += c
        except _EOF:
            raise TemplateSyntaxError("Unexpected EOF")

    if emit_buf:
        push_line(f"emit({repr(emit_buf)})")

    push_line("return ''.join(_buf)")
    leave_block()

    if indent != 0:
        raise TemplateSyntaxError("Unclosed block")

    code = compile(source="\n".join(lines), filename=filename, mode="exec")
    template_globals = {}
    exec(code, template_globals)
    return template_globals["evaluate_template"]
