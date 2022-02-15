from functools import partial


def paragraphs(*pars: str) -> str:
    return "\n\n".join(pars)


def lines(*lns: str) -> str:
    return "\n".join(lns) + "\n"


def begin(name: str, contents: str, options: str = "") -> str:
    return f"\\begin{{{name}}}{options}\n" + \
           contents + \
           f"\\end{{{name}}}\n"


def listlike(*items: str, prefix: str = "\\item", name: str) -> str:
    return begin(
        name,
        "\n".join(map(lambda item: "\\item " + item, items))
    )


itemize = partial(listlike, name="itemize")

enumerate = partial(listlike, name="enumerate")


def document(documentclass: str = "article", preampula: str = "", body: str = "") -> str:
    return f"\\documentclass[12pt]{{{documentclass}}}\n" + \
           preampula + \
           begin("document", body)


def package(name: str, options="") -> str:
    return f"\\usepackage{options}{{{name}}}"


class InvalidArgumentException(Exception):
    pass


def table(contents: list[list[str]]) -> str:
    h: int = len(contents)
    if h == 0:
        w: int = 0
    else:
        w: int = len(contents[0])

    for row in contents:
        if len(row) != w:
            raise InvalidArgumentException(f"Table rows do not have the same length: {w} != {len(row)}")

    return begin("table",
                 options="[]",
                 contents=begin(
                     name="tabular",
                     options="{" + "|l" * w + "|}",
                     contents=
                     "\\hline \n" +
                     "".join(
                         map(
                             lambda r: " & ".join(r) + "\\\\ \\hline \n",
                             contents
                         )
                     )

                 )
                 )
