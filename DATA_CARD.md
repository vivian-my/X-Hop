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

Each entry in `answers` contains `title`, `sentences`, and
`supporting_sentence_indices`. Keeping sentence-level evidence annotations inside
their passage makes them stable when passages are translated, reordered, or mixed
across languages. There is no separate `supporting_facts` field.

The stored sentence arrays preserve evidence boundaries. When constructing model
input, join the sentences within each answer position into one paragraph, then use
`hop_seq` to order those paragraphs by reasoning role. Passages are never merged
across answer positions, including when their titles are identical.

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
the link between them. The build now applies auditable, record-scoped repairs.

**Repair 1 — `sub_q2.answer` normalized (247 records).** `sub_q2` asks the same thing as the
full 2-hop question, so its answer equals the record's `answer` by construction. Independent
translation diverged anyway, sometimes only in case
(`Начальник Протокола` / `Начальник протокола`), sometimes in word choice
(`игровой автомат с шариками` / `пинбольный автомат`). `sub_q2.answer` is set to the
record's `answer` — canonical because it is what scoring compares against — and the original
kept in `sub_q2.answer_raw`.

| repaired | en | fr | ru | ar | zh |
|---|---:|---:|---:|---:|---:|
| | 5 | 44 | 66 | 71 | 61 |

**Repair 2 — inconsistent bridge translations corrected.** The unusable translated chains
were reviewed against the English decomposition. English names left inside otherwise
translated questions, corrupted transliterations, and inconsistent translations of the
same entity were replaced with grammatical target-language questions. This makes 69
previously unusable chains usable. The repairs live in `DECOMPOSITION_OVERRIDES` in
`scripts/build.py`, so they are reproducible rather than one-off edits to generated JSONL.

**Repair 3 — bridge entity classified.** Exact containment is still the wrong test outside
English. Correct translations can be morphological
(`Страсбург` → `Страсбура`, genitive) or word-order variants — correct translations that a
substring test rejects. `bridge_match` records *how* the entity surfaces:

| `bridge_match` | en | fr | ru | ar | zh | interpretation |
|---|---:|---:|---:|---:|---:|---|
| `exact` | 173 | 125 | 79 | 101 | 133 | usable for verbatim substitution |
| `normalized` | 0 | 20 | 4 | 1 | 3 | case/diacritic/punctuation variant |
| `inflected` | 0 | 28 | 90 | 71 | 37 | morphological or reordered variant |
| `latin_untranslated` | 0 | 0 | 0 | 0 | 0 | English name retained — defect |
| `absent` | 3 | 3 | 3 | 3 | 3 | bridge not stated in the source decomposition |
| **`chain_ok`** | **173** | **173** | **173** | **173** | **173** | first three |
| | 98.3% | 98.3% | 98.3% | 98.3% | 98.3% | |

**Residual limitations.** Three English records (`hotpotqa_171`, `hotpotqa_315`, and
`hotpotqa_333`) describe the bridge instead of naming it. Their aligned translations are
also marked `absent`; inserting an entity would change the source decomposition rather than
repair its translation. Therefore 173/176 is the honest ceiling in every language.
`inflected` is detected by shared stem prefix and character overlap, a heuristic: it may
admit a small number of coincidental matches and miss suppletive forms.
Filter on `bridge_match == "exact"` if you need certainty over coverage.

### 3. Answer strings are not always in the target script

Malformed mixed-script answer fragments were corrected when the target passage established
the intended rendering (for example, `قلعة سكيب ton` → `قلعة سكيبطن` and
`王朝重新 regrouped...` → `王朝重新集结...`). Proper nouns, callsigns, units, and acronyms such
as `BBC`, `EPA`, `FSMA`, `Warner Music Group`, and `KUAT-TV` legitimately remain in Latin
script. Share of answers written
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

Nine clear HotpotQA source defects were repaired in `RECORD_OVERRIDES`: `hotpotqa_260`,
`261`, `373`, `551`, `725`, `851`, `894`, `940`, and `953`. These repairs correct mismatched
question/answer types, false premises, polluted answer strings, and four corresponding
support-annotation sets. The corrections are translated consistently into all five aligned
files. Other MuSiQue and HotpotQA distractor artifacts and known reasoning shortcuts carry
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

`build.py` requires the **post-reorder** MuSiQue 2-hop copy. A manual semantic audit of its
English passages found 16 residual records whose bridge and answer-bearing passages were
still reversed; the builder applies the audited `[1, 0]` overrides to those records in all
five aligned languages. A pre-reorder copy exists in which 331 of 627 records have
`answers` reversed and must not be used.
