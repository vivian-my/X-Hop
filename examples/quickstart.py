"""Load the dataset and build one cross-lingual condition. No dependencies.

    python examples/quickstart.py
"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


def load(split, source, lang):
    with open(DATA / split / source / f"{lang}.jsonl", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def paragraph_text(passage):
    """Join stored sentences only when preparing model input."""
    return " ".join(sentence.strip() for sentence in passage["sentences"])


# --- 1. a monolingual record -------------------------------------------------
en = load("two_hop", "hotpotqa", "en")
r = en[20]
print(f"question : {r['question']}")
print(f"answer   : {r['answer']}")
# hop_seq maps reasoning order onto positions in `answers`
bridge, final = (r["answers"][i]["title"] for i in r["hop_seq"])
print(f"hop 1 (bridging)      : {bridge}")
print(f"hop 2 (answer-bearing): {final}")

# --- 2. the question decomposition, where present ----------------------------
if r["sub_q1"]:
    print(f"\nsub_q1   : {r['sub_q1']['question']}  -> {r['sub_q1']['answer']}")
    print(f"sub_q2   : {r['sub_q2']['question']}  -> {r['sub_q2']['answer']}")
    print(f"chain_ok : {r['chain_ok']}")

# Outside English the sub-questions were translated independently, so the bridge
# entity often does not match across them. Filter before chaining sub_q1 -> sub_q2.
ru = load("two_hop", "hotpotqa", "ru")
usable = [x for x in ru if x["chain_ok"]]
print(f"\nru: {len(usable)}/{len(ru)} records have a usable decomposition chain")

# --- 3. a cross-lingual condition --------------------------------------------
# Files are positionally aligned, so line i is the same item in every language.
# Take the query in English, the bridging hop in Russian, the answer hop in Chinese.
zh = load("two_hop", "hotpotqa", "zh")
i = 0
q = en[i]
b_pos, f_pos = q["hop_seq"]
mixed = dict(q, answers=[None, None])
mixed["answers"][b_pos] = ru[i]["answers"][b_pos]   # bridging hop -> Russian
mixed["answers"][f_pos] = zh[i]["answers"][f_pos]   # answer hop   -> Chinese

assert en[i]["id"] == ru[i]["id"] == zh[i]["id"]    # alignment guarantee
print(f"\ncross-lingual cell  query=en  hop1=ru  hop2=zh")
print(f"  hop 1 title: {mixed['answers'][b_pos]['title']}")
print(f"  hop 2 title: {mixed['answers'][f_pos]['title']}")

# Exactly two controlled paragraphs, presented in reasoning order. Passages with
# the same title remain separate because they occupy different answer positions.
paragraphs = [paragraph_text(mixed["answers"][pos]) for pos in mixed["hop_seq"]]
assert len(paragraphs) == 2
print(f"  hop 1 paragraph: {paragraphs[0]}")
print(f"  hop 2 paragraph: {paragraphs[1]}")

# scripts/make_cross_lingual.py does this for whole splits, including the full grid.
