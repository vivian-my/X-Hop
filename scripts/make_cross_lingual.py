"""Build a cross-lingual evaluation cell from the aligned monolingual files.

This is the intended usage of the release: the five language files per split are
positionally aligned, so a cell is defined by choosing a language INDEPENDENTLY
for the query and for each supporting passage.

    # query in English, bridging hop in Russian, answer hop in Chinese
    python scripts/make_cross_lingual.py --split two_hop --source musique \
        --query en --hops ru zh --out cell.jsonl

    # the full 5x5 passage grid for an English query
    python scripts/make_cross_lingual.py --split two_hop --source musique \
        --query en --grid --out-dir cells/

Each output record keeps the query from the query-language file and takes hop k's
gold passage from the k-th language given in --hops. Distractors follow the first
hop language. `hop_seq` maps positions in `answers` to reasoning order, so hop 1
is the bridging hop and hop N is the answer-bearing one.
"""
import argparse
import itertools
import json
from pathlib import Path

CODES = ["en", "fr", "ru", "ar", "zh"]


def read(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def build_cell(langs, query, hops):
    """langs: {code: records}. hops: one language code per hop, in reasoning order."""
    q_recs = langs[query]
    out = []
    for i, q in enumerate(q_recs):
        seq = q["hop_seq"]
        if len(hops) != len(seq):
            raise SystemExit(f"--hops needs {len(seq)} languages for this split")
        # answers[seq[k]] is the passage for hop k+1; pull it from hops[k]'s file.
        answers = [None] * len(seq)
        for k, pos in enumerate(seq):
            answers[pos] = langs[hops[k]][i]["answers"][pos]
        out.append({
            "id": q["id"],
            "source": q["source"],
            "n_hops": q["n_hops"],
            "query_lang": query,
            "hop_langs": list(hops),
            "question": q["question"],
            "answer": q["answer"],
            "answers": answers,
            "non_answers": langs[hops[0]][i]["non_answers"],
            "supporting_facts": q["supporting_facts"],
            "hop_seq": seq,
            "hop_seq_verified": q["hop_seq_verified"],
            "sub_q1": q["sub_q1"],
            "sub_q2": q["sub_q2"],
            "chain_ok": q["chain_ok"],
        })
    return out


def write(recs, p):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  {p}  {len(recs)} records")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=Path, default=Path("data"))
    ap.add_argument("--split", required=True, choices=["two_hop", "three_hop", "four_hop"])
    ap.add_argument("--source", default="musique", choices=["musique", "hotpotqa"])
    ap.add_argument("--query", required=True, choices=CODES)
    ap.add_argument("--hops", nargs="+", choices=CODES,
                    help="one language per hop, in reasoning order")
    ap.add_argument("--grid", action="store_true",
                    help="emit every hop-language combination instead of one cell")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--out-dir", type=Path)
    a = ap.parse_args()

    d = a.data / a.split / a.source
    langs = {c: read(d / f"{c}.jsonl") for c in CODES}
    n_hops = len(langs["en"][0]["hop_seq"])

    if a.grid:
        if not a.out_dir:
            ap.error("--grid requires --out-dir")
        for combo in itertools.product(CODES, repeat=n_hops):
            write(build_cell(langs, a.query, combo),
                  a.out_dir / f"{a.query}_{'_'.join(combo)}.jsonl")
    else:
        if not a.hops or not a.out:
            ap.error("need --hops and --out (or --grid and --out-dir)")
        write(build_cell(langs, a.query, a.hops), a.out)


if __name__ == "__main__":
    main()
