#!/usr/bin/env python3
"""tot_json_csv.py — Convert between tot_test.json (button config) and CSV.

JSON structure: dict keyed by button number (string) -> list of 9 fields:
    [name, x, y, label, color, effect_type, topic/file, payload, output]

CSV: one row per button with columns:
    button_number,name,x,y,label,color,effect_type,topic_or_file,payload,output

Usage:
    # JSON -> CSV  (read JSON from stdin, write CSV to stdout)
    python3 tot_json_csv.py -cc < tot_test.json > tot_buttons.csv

    # CSV -> JSON  (read CSV from stdin, write JSON to stdout)
    python3 tot_json_csv.py -cj < tot_buttons.csv > tot_test.json

Optional positional args (file paths) may replace stdin/stdout:
    python3 tot_json_csv.py -cc tot_test.json tot_buttons.csv
    python3 tot_json_csv.py -cj tot_buttons.csv tot_test.json
"""

import csv
import json
import sys


FIELDNAMES = [
    "button_number",
    "name",
    "x",
    "y",
    "label",
    "color",
    "effect_type",
    "topic_or_file",
    "payload",
    "output",
]


def json_to_csv(in_stream, out_stream):
    data = json.load(in_stream)

    rows = []
    for button_number, fields in data.items():
        fields = list(fields) + [""] * (9 - len(fields))
        rows.append(
            {
                "button_number": button_number,
                "name": fields[0],
                "x": fields[1],
                "y": fields[2],
                "label": fields[3],
                "color": fields[4],
                "effect_type": fields[5],
                "topic_or_file": fields[6],
                "payload": fields[7],
                "output": fields[8],
            }
        )

    rows.sort(key=lambda r: int(r["button_number"]))

    # Use QUOTE_NONNUMERIC so every non-empty string field is quoted,
    # while numeric fields (button_number, x, y) stay unquoted.
    # This guarantees filenames with dots (e.g. "atatin.wav") are one
    # quoted token and not mistaken for delimiter-separated numbers.
    out = []
    out.append(",".join(f'"{h}"' for h in FIELDNAMES) + "\n")
    for row in rows:
        values = []
        for h in FIELDNAMES:
            v = row[h]
            s = str(v) if v is not None else ""
            # Quote every string field; numbers are also fine quoted-as-string
            # for round-trip safety (csv_to_json reads them back as strings).
            escaped = s.replace('"', '""')
            values.append(f'"{escaped}"')
        out.append(",".join(values) + "\n")
    out_stream.write("".join(out))
    return len(rows)


def csv_to_json(in_stream, out_stream):
    reader = csv.DictReader(in_stream)
    rows = list(reader)

    data = {}
    for row in rows:
        button_number = row["button_number"]
        fields = [
            row["name"],
            row["x"],
            row["y"],
            row["label"],
            row["color"],
            row["effect_type"],
            row["topic_or_file"],
            row["payload"],
            row["output"],
        ]
        data[button_number] = fields

    # Sort keys numerically for stable JSON output
    sorted_keys = sorted(data, key=lambda k: int(k))
    ordered = {k: data[k] for k in sorted_keys}

    json.dump(ordered, out_stream, indent=4, ensure_ascii=False)
    out_stream.write("\n")
    return len(rows)


def main(argv):
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2

    flag = argv[1]
    if flag not in ("-cc", "-cj"):
        print(f"Unknown flag: {flag}\n{__doc__}", file=sys.stderr)
        return 2

    # Optional positional: input_file [output_file]
    positional = argv[2:]
    has_positional = len(positional) > 0

    in_path = positional[0] if has_positional else None
    out_path = positional[1] if has_positional and len(positional) > 1 else None

    try:
        if in_path:
            in_stream = open(in_path, "r", encoding="utf-8", newline="")
        else:
            in_stream = sys.stdin

        if out_path:
            out_stream = open(out_path, "w", encoding="utf-8", newline="")
        else:
            out_stream = sys.stdout

        try:
            if flag == "-cc":
                count = json_to_csv(in_stream, out_stream)
                msg = f"Wrote {count} button rows to CSV"
            else:  # -cj
                count = csv_to_json(in_stream, out_stream)
                msg = f"Wrote {count} buttons to JSON"
        finally:
            if in_path:
                in_stream.close()
            if out_path:
                out_stream.close()

        # Status goes to stderr so it doesn't pollute stdout data stream
        print(msg, file=sys.stderr)
        return 0

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
