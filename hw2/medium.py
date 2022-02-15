from codetreegen import codetreegen
import os

from easy import list_to_tex
import texgen as tex


def plus_one(x: int) -> int:
    return x + 1


if __name__ == "__main__":
    im = codetreegen(plus_one)

    try:
        os.mkdir("artifacts")
    except OSError as _:
        pass
    im.save("artifacts/medium.png")

    table_text = list_to_tex([
        ["1", "$\\frac 1 2$", "$1$"],
        ["hey", "hey", "hey"],
        [f"${100000 + i}$" for i in range(3)],
    ],
        body=tex.paragraphs(
            "\\includegraphics[width=8cm]{artifacts/medium.png}",
            "\\href{https://anaconda.org/NeKpoT/codetreegen}{\\underline{link to the package}}"
        )
    )

    try:
        os.mkdir("artifacts")
    except OSError as _:
        pass

    with open("artifacts/medium.tex", "w") as output:
        output.write(table_text)

    os.system("pdflatex ./artifacts/medium.tex -interaction=nonstopmode -output-directory=artifacts")

    print(table_text)


