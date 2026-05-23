import argparse
from pathlib import Path

import pandas as pd


# Chỉnh 2 dòng này nếu muốn chọn nhanh khoảng index cần xuất.
# Ví dụ START_INDEX = 0 và END_INDEX = 100 sẽ xuất 101 dòng đầu.
START_INDEX = 0
END_INDEX = 100

DEFAULT_INPUT = Path("data/vietnam_apartments.parquet")
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT = SCRIPT_DIR / "output_text_description" / "name_description_sample.xlsx"


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Export name and description rows from the apartment parquet file "
            "by inclusive integer index range."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Input parquet file. Default: {DEFAULT_INPUT}",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output Excel file. Default: {DEFAULT_OUTPUT}",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=START_INDEX,
        help=f"Start index, inclusive. Default: {START_INDEX}",
    )
    parser.add_argument(
        "--end",
        type=int,
        default=END_INDEX,
        help=f"End index, inclusive. Default: {END_INDEX}",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.start < 0:
        raise ValueError("--start must be >= 0")
    if args.end < args.start:
        raise ValueError("--end must be greater than or equal to --start")
    if not args.input.exists():
        raise FileNotFoundError(f"Input file not found: {args.input}")

    df = pd.read_parquet(args.input, columns=["name", "description"])

    if args.start >= len(df):
        raise IndexError(
            f"--start={args.start} is outside the dataset. "
            f"Valid index range: 0 to {len(df) - 1}"
        )

    end = min(args.end, len(df) - 1)
    output_df = df.iloc[args.start : end + 1].copy()
    output_df.insert(0, "index", output_df.index)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_excel(args.output, index=False)

    print(f"Exported {len(output_df)} rows: index {args.start} -> {end}")
    print(f"Output file: {args.output}")


if __name__ == "__main__":
    main()
