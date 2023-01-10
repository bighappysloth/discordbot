import argparse


def to_text(table, spacing=2):
    # Determine the maximum width of each column
    column_widths = [max(len(str(cell)) for cell in column) for column in table]

    # Print the table in text format
    for row in table:
        print(
            " ".join(
                "{:{width}}".format(cell, width=width + spacing)
                for cell, width in zip(row, column_widths)
            )
        )


def to_latex(table, caption=None, size=None, alignment=None, spacing=2):
    # Determine the maximum width of each column
    column_widths = [max(len(str(cell)) for cell in column) for column in table]

    # Print the table in LaTeX format
    if caption is not None:
        print("\\caption{{{}}}".format(caption))
    if size is not None:
        print("\\resizebox{{\\textwidth}}{{{}}}{{".format(size))
    print(
        "\\begin{tabularx}{\\textwidth}{"
        + "".join(
            "{}{{X}}".format(alignment[i] if alignment is not None else "c")
            for i in range(len(column_widths))
        )
        + "}"
    )
    print("\hline")
    for row in table:
        print(
            " ".join(
                "{:{width}}".format(cell, width=width + spacing)
                for cell, width in zip(row, column_widths)
            )
            + " \\\\"
        )
        print("\hline")
    print("\\end{tabularx}")
    if size is not None:
        print("}")


if __name__ == "__main__":
    # Parse the command-line arguments
    parser = argparse.ArgumentParser(
        description="Convert a list of lists of strings to a table"
    )
    parser.add_argument(
        "table",
        nargs="+",
        help="the table to be converted, as a list of lists of strings",
    )
    parser.add_argument("--caption", help="the caption for the table")
    parser.add_argument("--size", help="the size of the table")
    parser.add_argument("--alignment", help="the alignment of the columns in the table")
    parser.add_argument(
        "--spacing", type=int, default=2, help="the minimum spacing between columns"
    )
    args = parser.parse_args()

    # Convert the table to text or LaTeX format
    to_text(args.table, args.spacing)
    to_latex(args.table, args.caption, args.size, args.alignment, args.spacing)
