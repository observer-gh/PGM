#!/usr/bin/env python3
import os
import glob
import argparse
import pandas as pd


def summarize_csv(file_path, out):
    df = pd.read_csv(file_path)
    out.write(f"{'='*80}\n")
    out.write(f"File: {os.path.basename(file_path)}\n\n")

    out.write("1) First 10 rows:\n")
    out.write(df.head(10).to_string(index=False))
    out.write("\n\n")

    out.write("2) Statistics (describe):\n")
    out.write(df.describe(include='all').to_string())
    out.write("\n\n")

    out.write("3) Missing values per column:\n")
    out.write(df.isnull().sum().to_string())
    out.write("\n\n")


def main():
    parser = argparse.ArgumentParser(
        description="Summarize all CSVs in a folder: head(10), describe(), missing counts."
    )
    parser.add_argument(
        "-i", "--input_dir", required=True,
        help="CSV 파일들이 들어 있는 디렉터리 경로"
    )
    parser.add_argument(
        "-o", "--output", default="csv_summary.txt",
        help="출력할 요약 결과 파일명 (기본: csv_summary.txt)"
    )
    args = parser.parse_args()

    csv_files = glob.glob(os.path.join(args.input_dir, "*.csv"))
    if not csv_files:
        print(f"No CSV files found in '{args.input_dir}'")
        return

    with open(args.output, "w", encoding="utf-8") as out:
        for fp in sorted(csv_files):
            summarize_csv(fp, out)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()
