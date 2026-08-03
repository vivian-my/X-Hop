"""Build the release tree from the upstream MuSiQue and HotpotQA sources.

    python scripts/build.py --musique <dir> --hotpot <dir> --out data

Output (JSONL, one record per line, ISO 639-1 language codes):

    data/two_hop/musique/{en,fr,ru,ar,zh}.jsonl     627 records/lang
    data/two_hop/hotpotqa/{en,fr,ru,ar,zh}.jsonl    176 records/lang
    data/three_hop/musique/{...}.jsonl              327 records/lang
    data/four_hop/musique/{...}.jsonl               182 records/lang

Every language file is POSITIONALLY ALIGNED: line i is the same item in all five
languages. Cross-lingual conditions are built at load time by drawing passage 1
from one language file and passage 2 from another -- see make_cross_lingual.py.
That is why 5 files suffice for a 5x5 grid.

Source notes
  MuSiQue 2-hop must be the POST-reorder copy (answers[0]=hop1, answers[1]=hop2).
  A pre-reorder copy exists in which 331 of 627 records have `answers` reversed;
  building from it silently mislabels which hop is answer-bearing.

  HotpotQA sub-questions come from {lang}_1.json / {lang}_2.json, but ONLY their
  question/answer fields. The passage pools in those files are English in every
  language (byte-identical to English_1/_2) and are discarded here; passages come
  from {lang}_b.json, which is properly translated.
"""
import argparse
import json
import re
import unicodedata
from pathlib import Path

LANGS = [("English", "en"), ("French", "fr"), ("Russian", "ru"),
         ("Arabic", "ar"), ("Chinese", "zh")]

# Stray dialogue markers left by the upstream decomposition annotation.
PREFIX = re.compile(r"^\s*(?:Q|A|Question|Answer)\s*[:：]\s*", re.I)


def clean_q(s):
    return PREFIX.sub("", s).strip()


def _norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"[^\w\s]", " ", s)


def _toks(s):
    return [t for t in _norm(s).split() if len(t) >= 3]


def bridge_match(bridge, question, en_bridge):
    """How the bridge entity from sub_q1 surfaces in sub_q2's question.

    Exact string containment is the wrong test outside English: Russian and
    Arabic inflect the entity ("Страсбург" -> "Страсбура"), and word order
    shifts. Those are correct translations, not defects, so they are matched
    by shared stem rather than rewritten -- substituting the citation form
    back in would produce ungrammatical text.

      exact / normalized  - present verbatim, or modulo case/diacritics/punct
      inflected           - present in a morphological or reordered variant
      latin_untranslated  - question kept the English name; a real defect
      absent              - bridge does not appear at all
    """
    if not bridge.strip():
        return "absent"
    if bridge in question:
        return "exact"
    nb, nq = _norm(bridge), _norm(question)
    if nb and nb in nq:
        return "normalized"
    bt = _toks(bridge)
    if bt:
        qt = _toks(question)
        stem = lambda t: t[:max(4, len(t) - 3)]
        hit = sum(1 for t in bt if any(stem(u) == stem(t) for u in qt))
        if hit / len(bt) >= 0.5:
            return "inflected"
    if not re.search(r"[a-z]", nb):  # non-Latin script: compare by character
        chars = [ch for ch in bridge if ch.strip()]
        if chars and sum(ch in question for ch in chars) / len(chars) >= 0.6:
            return "inflected"
    if en_bridge and _norm(en_bridge) in nq:
        return "latin_untranslated"
    return "absent"

# out_dir, musique subdir, n_hops, hop order verified upstream?
MUSIQUE_SPLITS = [("two_hop", "2_hop", 2, True),
                  ("three_hop", "3_hop", 3, False),
                  ("four_hop", "4_hop", 4, False)]

FIELDS = ["id", "source", "type", "n_hops", "question", "answer",
          "answers", "non_answers", "supporting_facts",
          "hop_seq", "hop_seq_verified",
          "sub_q1", "sub_q2", "bridge_match", "chain_ok"]


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dump_jsonl(recs, p):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        for r in recs:
            assert list(r) == FIELDS, f"field order drift in {p}"
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return p.stat().st_size


def norm_musique(r, i, n_hops, verified):
    return {
        "id": f"musique_{n_hops}hop_{i}",
        "source": "musique",
        "type": r["type"],
        "n_hops": n_hops,
        "question": r["question"],
        "answer": r["answer"],
        "answers": r["answers"],
        "non_answers": r["non_answers"],
        "supporting_facts": r["supporting_facts"],
        "hop_seq": list(range(n_hops)),
        "hop_seq_verified": verified,
        # MuSiQue carries no question decomposition. Written explicitly so the
        # schema is uniform across sources and Arrow/parquet inference is clean.
        "sub_q1": None,
        "sub_q2": None,
        "bridge_match": None,
        "chain_ok": None,
    }


def norm_hotpot(r, q1, q2, en_q1):
    """r from {lang}_b.json (translated passages); q1/q2 from {lang}_{1,2}.json
    (questions only -- their passage pools are English and are discarded).

    Two repairs are applied to the raw decomposition:

    1. sub_q2 asks the same thing as the full 2-hop question, so its answer is
       the record's answer by construction (English: 176/176). Independent
       per-language translation broke that -- "Начальник Протокола" vs
       "Начальник протокола". The record's answer is canonical because it is
       what scoring compares against, so sub_q2's answer is set to it and the
       divergent translation kept as `answer_raw` for audit.

    2. The bridge entity is classified, not rewritten -- see bridge_match().
    """
    q2_answer_raw = q2["answer"] if q2["answer"] != r["answer"] else None
    match = bridge_match(clean_q(q1["answer"]), clean_q(q2["question"]),
                         en_q1["answer"])
    return {
        "id": f"hotpotqa_{r['id']}",
        "source": "hotpotqa",
        "type": r["type"],
        "n_hops": 2,
        "question": r["question"],
        "answer": r["answer"],
        "answers": r["answers"],
        "non_answers": r["non_answers"],
        "supporting_facts": r["supporting_facts"],
        "hop_seq": r["hop_seq"],
        "hop_seq_verified": True,
        "sub_q1": {"question": clean_q(q1["question"]),
                   "answer": clean_q(q1["answer"])},
        "sub_q2": {"question": clean_q(q2["question"]),
                   "answer": r["answer"],
                   "answer_raw": q2_answer_raw},
        "bridge_match": match,
        # True when the bridge entity actually surfaces in sub_q2, in any
        # grammatical form. sub_q2's answer is guaranteed correct by repair 1,
        # so this is the only remaining condition.
        "chain_ok": match in ("exact", "normalized", "inflected"),
    }


def build_musique(mus_root, out, name, subdir, n_hops, verified):
    ids_ref = None
    for lang, code in LANGS:
        raw = load(mus_root / subdir / f"{lang}.json")
        recs = [norm_musique(r, i, n_hops, verified) for i, r in enumerate(raw)]
        ids = [r["id"] for r in recs]
        if ids_ref is None:
            ids_ref = ids
        elif ids != ids_ref:
            raise SystemExit(f"{name}/{lang}: id sequence diverges from English")
        for r in recs:
            assert len(r["answers"]) == n_hops, f"{r['id']}: {len(r['answers'])} answers"
        n = dump_jsonl(recs, out / name / "musique" / f"{code}.jsonl")
        print(f"  {name}/musique/{code}.jsonl  {len(recs):>4} records  {n / 1e6:5.1f} MB")


def build_hotpot(hot_root, out, name):
    en_b = load(hot_root / "English_b.json")
    # hop_seq == [-1,-1] means the answer string occurs in both paragraphs, so
    # hop order is undeterminable. Language-invariant, so the same positions
    # drop from every language.
    drop = {i for i, r in enumerate(en_b) if r["hop_seq"] == [-1, -1]}
    print(f"  dropping {len(drop)} records with undeterminable hop order "
          f"at positions {sorted(drop)}")

    en_s1 = {r["id"]: r for r in load(hot_root / "English_1.json")}
    ids_ref = None
    for lang, code in LANGS:
        b = load(hot_root / f"{lang}_b.json")
        s1 = {r["id"]: r for r in load(hot_root / f"{lang}_1.json")}
        s2 = {r["id"]: r for r in load(hot_root / f"{lang}_2.json")}
        recs = [norm_hotpot(r, s1[r["id"]], s2[r["id"]], en_s1[r["id"]])
                for i, r in enumerate(b) if i not in drop]
        ids = [r["id"] for r in recs]
        if ids_ref is None:
            ids_ref = ids
        elif ids != ids_ref:
            raise SystemExit(f"{name}/{lang}: id sequence diverges from English")
        for r in recs:
            assert len(r["answers"]) == 2, f"{r['id']}: {len(r['answers'])} answers"
            assert sorted(r["hop_seq"]) == [0, 1], f"{r['id']}: bad hop_seq"
        n = dump_jsonl(recs, out / name / "hotpotqa" / f"{code}.jsonl")
        ok = sum(r["chain_ok"] for r in recs)
        fixed = sum(r["sub_q2"]["answer_raw"] is not None for r in recs)
        print(f"  {name}/hotpotqa/{code}.jsonl  {len(recs):>4} records  {n / 1e6:5.1f} MB"
              f"   chain_ok {ok:>3}/{len(recs)}   sub_q2 answers repaired: {fixed}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--musique", type=Path, required=True,
                    help="dir containing 2_hop/ 3_hop/ 4_hop/ (2_hop must be POST-reorder)")
    ap.add_argument("--hotpot", type=Path, required=True,
                    help="dir containing {lang}_b.json, {lang}_1.json, {lang}_2.json")
    ap.add_argument("--out", type=Path, default=Path("data"))
    a = ap.parse_args()

    for name, subdir, n_hops, verified in MUSIQUE_SPLITS:
        print(f"{name}  <- musique/{subdir}"
              + ("" if verified else "   [hop_seq_verified=false]"))
        build_musique(a.musique, a.out, name, subdir, n_hops, verified)
        if name == "two_hop":
            print(f"{name}  <- hotpotqa")
            build_hotpot(a.hotpot, a.out, name)
        print()


if __name__ == "__main__":
    main()
