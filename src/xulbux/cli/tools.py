from ..format_codes import FormatCodes
from ..console import Console


def render_format_codes():
    args = Console.get_args({"input": "before"})

    if not args.input.values:
        FormatCodes.print("\n[_|i|dim]Provide a string to parse and render\n"
                          "its format codes as ANSI console output.[_]\n")

    else:
        ansi = FormatCodes.to_ansi("".join(args.input.values))
        ansi_escaped = FormatCodes.escape_ansi(ansi)
        ansi_stripped = FormatCodes.remove_ansi(ansi)

        print(f"\n{ansi}\n")

        if len(ansi) != len(ansi_stripped):
            FormatCodes.print(f"[_|i|dim]{ansi_escaped}[_]\n")
        else:
            FormatCodes.print("[_|i|dim](The provided string doesn't contain any valid format codes.)\n")
