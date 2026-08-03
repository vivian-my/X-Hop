"""Reproduce the merged 803-record 2-hop set used in the paper.

    python scripts/make_combined.py --out combined/

Concatenates two_hop/musique (627) and two_hop/hotpotqa (176) per language, in
that order, giving the record sequence the original experiments ran on.

LICENSING: the two sources are distributed under different terms, and HotpotQA's
is copyleft. The release ships them separately so users can take either alone;
this script produces a derivative combining both, which inherits the more
restrictive terms. See LICENSES/ before redistributing the output.
"""
import argparse
import json
from pathlib import Path

CODES = ["en", "fr", "ru", "ar", "zh"]


def read(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=Path, default=Path("data"))
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    a.out.mkdir(parents=True, exist_ok=True)
    for c in CODES:
        recs = (read(a.data / "two_hop/musique" / f"{c}.jsonl")
                + read(a.data / "two_hop/hotpotqa" / f"{c}.jsonl"))
        p = a.out / f"{c}.jsonl"
        with open(p, "w", encoding="utf-8") as f:
            for r in recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        n_m = sum(r["source"] == "musique" for r in recs)
        print(f"  {p}  {len(recs)} records ({n_m} musique + {len(recs) - n_m} hotpotqa)")


if __name__ == "__main__":
    main()
