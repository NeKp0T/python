import os

import texgen as tex


def list_to_tex(table: list[list[str]], body: str = "") -> str:
    return tex.document(
        preampula=tex.lines(
            # tex.package("cmap"),
            # tex.package("fontenc", options="[T2A]"),
            # tex.package("babel", options="[russian]"),
            # tex.package("inputenc", options="[utf8]"),
            tex.package("amsmath, amssymb"),
            tex.package("enumerate"),
            tex.package("graphicx"),
            tex.package("hyperref"),
            tex.package("fancyhdr")
        ),
        body=tex.table(table) + body
    )


if __name__ == "__main__":
    table_text = list_to_tex([
        ["1", "$\\frac 1 2$", "$1$"],
        ["hey", "hey", "hey"],
        [f"${100000 + i}$" for i in range(3)]
    ])

    try:
        os.mkdir("artifacts")
    except OSError as _:
        pass

    with open("artifacts/easy.tex", "w") as output:
        output.write(table_text)

    print(table_text)
