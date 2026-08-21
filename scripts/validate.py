"""Integrity checks for the release tree.  python scripts/validate.py [--data data]

Fails loudly on anything a downstream user would otherwise hit silently:
cross-language misalignment, wrong hop counts, invalid supporting-sentence
annotations, schema drift, or a language file whose text is not actually in that
language.
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

CODES = ["en", "fr", "ru", "ar", "zh"]
SPLITS = [("two_hop", ["musique", "hotpotqa"], 2),
          ("three_hop", ["musique"], 3),
          ("four_hop", ["musique"], 4)]
FIELDS = ["id", "source", "type", "n_hops", "question", "answer",
          "answers", "non_answers", "hop_seq", "hop_seq_verified", "sub_q1", "sub_q2",
          "bridge_match", "chain_ok"]
ANSWER_FIELDS = ["title", "sentences", "supporting_sentence_indices"]
MUSIQUE_2HOP_REVERSED = {
    "musique_2hop_65", "musique_2hop_80", "musique_2hop_113", "musique_2hop_138",
    "musique_2hop_277", "musique_2hop_278", "musique_2hop_349", "musique_2hop_354",
    "musique_2hop_420", "musique_2hop_425", "musique_2hop_435", "musique_2hop_480",
    "musique_2hop_509", "musique_2hop_561", "musique_2hop_567", "musique_2hop_613",
}
NON_EXPLICIT_BRIDGE_IDS = {
    "hotpotqa_171", "hotpotqa_315", "hotpotqa_333",
}
SOURCE_REPAIR_ANSWERS_EN = {
    "hotpotqa_260": "Hindi",
    "hotpotqa_261": "second wife",
    "hotpotqa_373": "February 1, 1999",
    "hotpotqa_551": "the green fairy",
    "hotpotqa_725": "Volcano Bay",
    "hotpotqa_851": "Magic formula investing",
    "hotpotqa_894": "Bandai",
    "hotpotqa_940": "Mary Harron",
    "hotpotqa_953": "Academy Award for Best Art Direction",
}
SOURCE_REPAIR_SUPPORT = {
    "hotpotqa_260": [[0], [0, 2, 3]],
    "hotpotqa_373": [[0, 3], [0, 1]],
    "hotpotqa_551": [[0, 2], [2]],
    "hotpotqa_725": [[0, 1], [1]],
}
BROKEN_ANSWER_FRAGMENTS = {
    "Паола Д'Alessandris", "Паула Д'Alessandris", "ЛидерTeamsters",
    "художественную direction", "قلعة سكيب ton", "المبلغ المحسوم من قبل bookmaker",
    "كو Phi Phi Leh", "داليشيče", "بuble", "重新 regrouped",
    "美国法 Marshal Rooster Cogburn",
}

SCRIPTS = [("Cyrillic", re.compile(r"[Ѐ-ӿ]")),
           ("Arabic", re.compile(r"[؀-ۿݐ-ݿ]")),
           ("CJK", re.compile(r"[一-鿿㐀-䶿]"))]
EXPECT = {"en": "Latin", "fr": "Latin", "ru": "Cyrillic", "ar": "Arabic", "zh": "CJK"}

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)
    return cond


def script_of(t):
    for name, pat in SCRIPTS:
        if pat.search(t):
            return name
    return "Latin" if t.strip() else "empty"


def read(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=Path("data"))
    a = ap.parse_args()

    for split, sources, n_hops in SPLITS:
        for source in sources:
            langs = {c: read(a.data / split / source / f"{c}.jsonl") for c in CODES}
            ref = [r["id"] for r in langs["en"]]
            check(len(set(ref)) == len(ref), f"{split}/{source}: duplicate ids")

            for c, recs in langs.items():
                tag = f"{split}/{source}/{c}"
                check([r["id"] for r in recs] == ref, f"{tag}: id sequence misaligned vs en")
                for i, r in enumerate(recs):
                    check(list(r) == FIELDS, f"{tag} rec {i}: schema drift")
                    check(r["n_hops"] == n_hops, f"{tag} {r['id']}: n_hops != {n_hops}")
                    check(len(r["answers"]) == n_hops, f"{tag} {r['id']}: wrong answer count")
                    check(sorted(r["hop_seq"]) == list(range(n_hops)),
                          f"{tag} {r['id']}: hop_seq not a permutation")
                    check(r["hop_seq"] == langs["en"][i]["hop_seq"],
                          f"{tag} rec {i}: hop_seq differs from en")
                    for j, passage in enumerate(r["answers"]):
                        valid_shape = (isinstance(passage, dict)
                                       and list(passage) == ANSWER_FIELDS
                                       and isinstance(passage.get("title"), str)
                                       and isinstance(passage.get("sentences"), list)
                                       and isinstance(passage.get("supporting_sentence_indices"), list))
                        if not check(valid_shape, f"{tag} {r['id']}: malformed answers[{j}]"):
                            continue
                        indices = passage["supporting_sentence_indices"]
                        check(all(type(x) is int for x in indices),
                              f"{tag} {r['id']}: non-integer supporting sentence index")
                        check(len(indices) == len(set(indices)),
                              f"{tag} {r['id']}: duplicate supporting sentence index")
                        check(all(0 <= x < len(passage["sentences"]) for x in indices),
                              f"{tag} {r['id']}: supporting sentence index out of range")
                    # positional alignment of the passage pool
                    check(len(r["non_answers"]) == len(langs["en"][i]["non_answers"]),
                          f"{tag} rec {i}: non_answers count differs from en")
                    check([x["supporting_sentence_indices"] for x in r["answers"]] ==
                          [x["supporting_sentence_indices"]
                           for x in langs["en"][i]["answers"]],
                          f"{tag} rec {i}: supporting sentence annotations differ from en")

                if split == "two_hop" and source == "musique":
                    reversed_ids = {r["id"] for r in recs if r["hop_seq"] == [1, 0]}
                    check(reversed_ids == MUSIQUE_2HOP_REVERSED,
                          f"{tag}: audited hop_seq overrides changed")

                # language of the text itself -- catches untranslated files
                qs = Counter(script_of(r["question"]) for r in recs)
                ps = Counter(script_of(r["answers"][0]["sentences"][0]) for r in recs)
                for what, cnt in [("question", qs), ("passage", ps)]:
                    top, n = cnt.most_common(1)[0]
                    check(top == EXPECT[c] and n / len(recs) > 0.90,
                          f"{tag}: {what} script is {top} ({100 * n / len(recs):.0f}%), "
                          f"expected {EXPECT[c]}")

                if source == "hotpotqa":
                    for r in recs:
                        check(r["sub_q1"] and r["sub_q2"],
                              f"{tag} {r['id']}: missing decomposition")
                        # invariant: sub_q2 asks the same thing as the full
                        # question, so its answer must be the record's answer
                        check(r["sub_q2"]["answer"] == r["answer"],
                              f"{tag} {r['id']}: sub_q2 answer != answer")
                        check(r["chain_ok"] ==
                              (r["bridge_match"] in ("exact", "normalized", "inflected")),
                              f"{tag} {r['id']}: chain_ok inconsistent with bridge_match")
                    failed_ids = {r["id"] for r in recs if not r["chain_ok"]}
                    check(failed_ids == NON_EXPLICIT_BRIDGE_IDS,
                          f"{tag}: unexpected unusable decomposition chains: "
                          f"{sorted(failed_ids)}")
                    check(not any(r["bridge_match"] == "latin_untranslated" for r in recs),
                          f"{tag}: untranslated Latin bridge remains")
                    for r in recs:
                        if r["id"] in SOURCE_REPAIR_ANSWERS_EN:
                            passage_text = " ".join(
                                sentence for passage in r["answers"]
                                for sentence in passage["sentences"])
                            check(r["answer"] in passage_text,
                                  f"{tag} {r['id']}: corrected answer absent from gold passages")
                            bridge_text = " ".join(
                                r["answers"][r["hop_seq"][0]]["sentences"])
                            check(r["sub_q1"]["answer"] in bridge_text,
                                  f"{tag} {r['id']}: corrected bridge absent from hop 1")
                    if c == "en":
                        by_id = {r["id"]: r for r in recs}
                        for record_id, answer in SOURCE_REPAIR_ANSWERS_EN.items():
                            check(by_id[record_id]["answer"] == answer,
                                  f"{tag} {record_id}: audited source answer changed")
                        for record_id, expected in SOURCE_REPAIR_SUPPORT.items():
                            actual = [p["supporting_sentence_indices"]
                                      for p in by_id[record_id]["answers"]]
                            check(actual == expected,
                                  f"{tag} {record_id}: audited support repair changed")
                else:
                    for r in recs:
                        check(r["sub_q1"] is None and r["chain_ok"] is None,
                              f"{tag} {r['id']}: unexpected decomposition on musique")

                for r in recs:
                    for fragment in BROKEN_ANSWER_FRAGMENTS:
                        check(fragment not in r["answer"],
                              f"{tag} {r['id']}: broken answer fragment {fragment!r}")

            print(f"ok  {split}/{source:<9} {len(ref):>4} records x 5 languages")

    # two_hop/hotpotqa must stay joinable with the decomposition it carries
    KINDS = ["exact", "normalized", "inflected", "latin_untranslated", "absent"]
    print(f"\nbridge_match distribution (decomposition chain integrity):")
    print(f"{'':4}" + "".join(f"{k:>20}" for k in KINDS) + f"{'chain_ok':>12}")
    for c in CODES:
        recs = read(a.data / f"two_hop/hotpotqa/{c}.jsonl")
        cnt = Counter(r["bridge_match"] for r in recs)
        ok = sum(r["chain_ok"] for r in recs)
        print(f"  {c} " + "".join(f"{cnt.get(k, 0):>20}" for k in KINDS)
              + f"{ok:>7}/{len(recs)}")
    rep = sum(r["sub_q2"]["answer_raw"] is not None
              for c in CODES for r in read(a.data / f"two_hop/hotpotqa/{c}.jsonl"))
    print(f"\nsub_q2 answers normalized to the record answer: {rep} across all languages")

    unverified = [s for s, _, _ in SPLITS
                  if not read(a.data / s / "musique/en.jsonl")[0]["hop_seq_verified"]]
    if unverified:
        print(f"\nnote: hop_seq_verified=false in {', '.join(unverified)} "
              f"(identity order, never validated upstream)")

    if fails:
        print(f"\nFAILED: {len(fails)} problem(s)", file=sys.stderr)
        for f in fails[:25]:
            print(f"  {f}", file=sys.stderr)
        sys.exit(1)
    print("\nall checks passed")


if __name__ == "__main__":
    main()
