# Data Card — XHop

## Overview

**XHop** is parallel multi-hop QA in English, French, Russian, Arabic and Chinese, derived from
**MuSiQue** (2/3/4-hop) and **HotpotQA** (2-hop, with gold question decompositions).

The design goal is to make the language of the query and the language of each individual
supporting passage independently controllable, so that the effect of a language switch can
be attributed to a *specific hop* — in particular separating the **bridging** hop from the
**answer-bearing** hop.

| | |
|---|---|
| Languages | en, fr, ru, ar, zh |
| Records per language | 1,312 |
| Total records | 6,560 |
| Size | 55 MB |
| Decomposition | 176 records/lang (HotpotQA), `chain_ok` 71.6-97.7% by language |
| Format | JSONL, UTF-8 |
| Alignment | positional — line *i* is the same item in all five languages |

## Composition

| Split | Source | Records | Hops | Upstream `type` values |
|---|---|---:|:---:|---|
| `two_hop/musique` | MuSiQue | 627 | 2 | `2hop` |
| `two_hop/hotpotqa` | HotpotQA | 176 | 2 | `bridge` |
| `three_hop/musique` | MuSiQue | 327 | 3 | `3hop1` (215), `3hop2` (112) |
| `four_hop/musique` | MuSiQue | 182 | 4 | `4hop1` (91), `4hop2` (28), `4hop3` (63) |

Each record carries its gold passages (`answers`) plus distractors (`non_answers`),
totalling 20 passages throughout.

## Provenance

### Source data

English MuSiQue and HotpotQA. HotpotQA records were filtered to a 182-item subset before
translation; 6 were subsequently dropped (see *Exclusions*), leaving 176.

### Translation

> **TODO — must be completed before release.**
>
> Record here: the MT system and exact model/version used, whether the same system was
> used for all five languages, whether questions/passages/answers were translated
> separately or jointly, any human post-editing or verification, and the date of
> translation. No translation provenance survives in the source repository, so this must
> be reconstructed from lab records.
>
> Without this section the release is not publishable — the `chain_ok` figures below are
> direct evidence that translation choices materially affect what the data supports.

Translations are believed to be **machine-produced and not human-verified**. Treat all
non-English text accordingly.

### Exclusions

Six HotpotQA records were removed because their `hop_seq` was `[-1,-1]` — the answer string
occurs in *both* gold passages, so which hop is answer-bearing is undeterminable. Positions
`[25, 34, 58, 75, 101, 128]` in the source ordering. `hop_seq` is language-invariant, so the
same items are absent from every language.

## Known limitations

### 1. `hop_seq` is unverified at 3 and 4 hops

`hop_seq_verified` is `false` for `three_hop` and `four_hop`. In those splits `hop_seq` is
the identity order (`[0,1,2]`, `[0,1,2,3]`) on **every** record, which records file order,
not verified reasoning order. Contrast `two_hop/hotpotqa`, where 87 of 176 records carry a
genuine non-identity order.

Per-hop analysis at 3 and 4 hops requires establishing the ordering first. The field is
present for schema uniformity, not because it has been checked.

### 2. Decomposition chains, and what was repaired

`sub_q1` and `sub_q2` were translated independently of each other per language, which broke
the link between them. Two repairs were applied at build time; both are auditable and
neither rewrites translated text.

**Repair 1 — `sub_q2.answer` normalized (223 records).** `sub_q2` asks the same thing as the
full 2-hop question, so its answer equals the record's `answer` by construction (English:
176/176). Independent translation diverged anyway, sometimes only in case
(`Начальник Протокола` / `Начальник протокола`), sometimes in word choice
(`игровой автомат с шариками` / `пинбольный автомат`). `sub_q2.answer` is set to the
record's `answer` — canonical because it is what scoring compares against — and the original
kept in `sub_q2.answer_raw`.

| repaired | en | fr | ru | ar | zh |
|---|---:|---:|---:|---:|---:|
| | 0 | 38 | 61 | 68 | 56 |

**Repair 2 — bridge entity classified, not rewritten.** Exact containment is the wrong test
outside English. Inspection showed most apparent failures were morphological
(`Страсбург` → `Страсбура`, genitive) or word-order variants — correct translations that a
substring test rejects. Rewriting them to the citation form would produce ungrammatical
text, so `bridge_match` records *how* the entity surfaces instead:

| `bridge_match` | en | fr | ru | ar | zh | interpretation |
|---|---:|---:|---:|---:|---:|---|
| `exact` | 172 | 113 | 65 | 87 | 83 | usable for verbatim substitution |
| `normalized` | 0 | 20 | 4 | 1 | 3 | case/diacritic/punctuation variant |
| `inflected` | 0 | 30 | 96 | 82 | 40 | morphological or reordered variant |
| `latin_untranslated` | 0 | 7 | 8 | 4 | 29 | English name retained — genuine defect |
| `absent` | 4 | 6 | 3 | 2 | 21 | bridge missing — genuine defect |
| **`chain_ok`** | **172** | **163** | **165** | **170** | **126** | first three |
| | 97.7% | 92.6% | 93.8% | 96.6% | 71.6% | |

**Residual limitations.** The 4 English `absent` cases are upstream annotation quirks —
`sub_q2` describes the bridge instead of naming it — so 172/176 is the ceiling in every
language, not 176. Chinese is the weakest at 71.6%, driven by 29 questions that kept the
English entity name. `inflected` is detected by shared stem prefix and character overlap, a
heuristic: it may admit a small number of coincidental matches and miss suppletive forms.
Filter on `bridge_match == "exact"` if you need certainty over coverage.

### 3. Answer strings are not always in the target script

Proper nouns frequently remain in Latin script after translation. Share of answers written
in the expected script:

| Split / source | en | fr | ru | ar | zh |
|---|---:|---:|---:|---:|---:|
| `two_hop/musique` | 100% | 100% | 89% | 98% | 89% |
| `two_hop/hotpotqa` | 100% | 100% | 92% | 97% | 92% |
| `three_hop/musique` | 100% | 100% | 83% | 100% | 87% |
| `four_hop/musique` | 100% | 100% | 83% | 88% | 83% |

Consequence: string-match metrics (EM, token F1) against the target-language gold conflate
*factual correctness* with *answering in the expected language*. A low score cannot be
attributed to either without separating them — e.g. by additionally scoring against gold in
all five languages and reporting the max.

### 4. Translationese

All non-English data is translated from English source questions and passages. It reflects
English-centric entity distributions, discourse structure and world knowledge, and is not a
sample of naturally occurring questions in those languages.

### 5. Inherited upstream limitations

MuSiQue and HotpotQA distractors, annotation artifacts and known reasoning shortcuts carry
over unchanged.

## Intended use

Evaluating multilingual and cross-lingual multi-hop reasoning, especially the effect of
language mismatch localized to a specific hop.

**Not intended for** training or fine-tuning without accounting for the machine-translation
noise documented above, nor as evidence about naturally occurring non-English questions.

## Licensing

MuSiQue and HotpotQA carry **different** licenses and HotpotQA's is copyleft. The two
sources are shipped in separate files so that either can be used alone under its own terms.
`scripts/make_combined.py` produces a derivative containing both, which inherits the more
restrictive terms.

> **TODO — confirm the exact upstream license texts and versions and place them in
> `LICENSES/` before release.**

## Reproducing

```bash
python scripts/build.py --musique <musique_dir> --hotpot <hotpot_dir> --out data
python scripts/validate.py
```

`build.py` requires the **post-reorder** MuSiQue 2-hop copy, in which `answers[0]` is the
bridging hop and `answers[1]` the answer-bearing one. A pre-reorder copy exists in which 331
of 627 records have `answers` reversed; building from it silently inverts the hop labels
that the dataset exists to study.
