<div align="center">

# XHop: Multilingual Multi-Hop Reasoning Dataset

**Cross-lingual multi-hop question answering, one hop at a time.**

[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Dataset-FFD21E?style=for-the-badge)](https://huggingface.co/datasets/CHANGE-ME/XHop)
[![Website](https://img.shields.io/badge/Website-XHop-4A90D9?style=for-the-badge&logo=googlechrome&logoColor=white)](https://CHANGE-ME.github.io/XHop)
[![Paper](https://img.shields.io/badge/Paper-arXiv-B31B1B?style=for-the-badge&logo=arxiv&logoColor=white)](https://arxiv.org/abs/CHANGE-ME)

[![Languages](https://img.shields.io/badge/languages-5-3d5a80)](#splits)
[![Records](https://img.shields.io/badge/records-6%2C560-3d5a80)](#splits)
[![Hops](https://img.shields.io/badge/hops-2%20%7C%203%20%7C%204-3d5a80)](#splits)
[![License](https://img.shields.io/badge/license-per%20source-6E7781)](LICENSES/)

</div>

---

**XHop** extends two English multi-hop question-answering datasets,
[HotpotQA](https://hotpotqa.github.io/) and [MuSiQue](https://github.com/stonybrooknlp/musique),
to five languages: English, Chinese, French, Arabic, and Russian. By varying the language
of each supporting document, **XHop** enables fine-grained evaluation of multilingual
multi-hop reasoning, revealing how model performance changes when the evidence required to
answer a question is distributed across languages. As illustrated below, the model must
integrate information from two documents written in different languages to derive the
final answer.

<div align="center">
<img alt="A 2-hop XHop example. An English question, one context block holding a French bridging passage that names Briana Corrigan and a Chinese answer-bearing passage identifying her as a Northern Irish singer, and the English answer." src="assets/example.svg" width="860">
</div>

<div align="center">
<sub>Record <code>hotpotqa_766</code>, unmodified from <code>data/two_hop/hotpotqa/</code>.
Both hops arrive in a single context, exactly as the model receives them; the
parenthesised italics give the English meanings and are not part of that input.
Neither passage answers the question alone — the first names the singer, the second gives
her nationality, and they are written in different scripts.</sub>
</div>

The five language files in each split are **positionally aligned** — line *i* is the same
item in all five. A cross-lingual condition is assembled at load time by drawing each
passage from a different language file, so 5 files yield the full 5×5 grid and no
combination has to be shipped. Because the language of the query and of *each individual
hop* varies independently, a failure can be attributed to a **specific hop** rather than
to "the setting was multilingual."

## Splits

| Split | Source | Records/lang | Hops | `hop_seq` verified | Decomposition |
|---|---|---:|:---:|:---:|:---:|
| `two_hop/musique` | MuSiQue | 627 | 2 | yes | — |
| `two_hop/hotpotqa` | HotpotQA | 176 | 2 | yes | yes |
| `three_hop/musique` | MuSiQue | 327 | 3 | **no** | — |
| `four_hop/musique` | MuSiQue | 182 | 4 | **no** | — |

6,560 records total (1,312 per language). JSONL, UTF-8, one record per line.

```
data/<split>/<source>/{en,fr,ru,ar,zh}.jsonl
```

## Quick start

```python
import json

def load(split, source, lang):
    with open(f"data/{split}/{source}/{lang}.jsonl", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

en, ru, zh = (load("two_hop", "hotpotqa", L) for L in ("en", "ru", "zh"))

# Files are aligned, so line i is the same question in every language.
i = 0
q = en[i]
bridge_pos, answer_pos = q["hop_seq"]        # reasoning order -> positions in `answers`

# Query in English, bridging hop in Russian, answer-bearing hop in Chinese.
passages = [None, None]
passages[bridge_pos] = ru[i]["answers"][bridge_pos]
passages[answer_pos] = zh[i]["answers"][answer_pos]
```

`examples/quickstart.py` runs this end to end. `scripts/make_cross_lingual.py` does it for
whole splits, including the full grid:

```bash
python scripts/make_cross_lingual.py --split two_hop --source musique \
    --query en --hops ru zh --out cell.jsonl
python scripts/make_cross_lingual.py --split two_hop --source musique \
    --query en --grid --out-dir cells/          # all 25 passage combinations
```

## Record schema

```jsonc
{
  "id": "hotpotqa_5a8b57f25542995d1e6f1371",
  "source": "hotpotqa",            // "musique" | "hotpotqa"
  "type": "bridge",                // upstream reasoning-shape label
  "n_hops": 2,
  "question": "...",
  "answer": "Chief of Protocol",

  "answers":     [[title, [sentence, ...]], ...],   // the n gold passages
  "non_answers": [[title, [sentence, ...]], ...],   // distractors
  "supporting_facts": [[title, sentence_index], ...],

  "hop_seq": [1, 0],               // reasoning order -> indices into `answers`;
                                   // hop 1 = bridging, hop n = answer-bearing
  "hop_seq_verified": true,        // false => placeholder order, see below

  "sub_q1": {"question": "...", "answer": "Shirley Temple"},   // null on MuSiQue
  "sub_q2": {"question": "...",
             "answer": "Chief of Protocol",   // == `answer`, normalized
             "answer_raw": null},             // original translation, if it differed
  "bridge_match": "exact",         // exact|normalized|inflected|latin_untranslated|absent
  "chain_ok": true
}
```

Every record carries 20 passages total (gold + distractors), so more hops means
proportionally fewer distractors.

### `hop_seq`

`answers[hop_seq[0]]` is the bridging hop; `answers[hop_seq[-1]]` is the answer-bearing
one. The distinction carries the finding — models are far more sensitive to the language
of the answer-bearing hop than the bridging one.

> **`hop_seq_verified` is `false` for `three_hop` and `four_hop`.** There `hop_seq` is the
> identity order and records *file order, not verified reasoning order* — those files never
> went through a hop-ordering pass. Do not use it for per-hop analysis at 3 and 4 hops
> without establishing the ordering yourself.

### Question decomposition

The 176 HotpotQA records carry a gold decomposition into two single-hop questions, stored
as fields on the record so questions and passages cannot drift apart.

Sub-questions were translated independently per language, which broke the link between
them. Two repairs are applied at build time, neither rewriting translated text:
`sub_q2.answer` is normalized to the record's `answer` (223 records; the original is kept
in `answer_raw`), and the bridge entity is *classified* rather than substituted — Russian
and Arabic inflect it (`Страсбург` → `Страсбура`), which is correct translation that a
substring test wrongly rejects.

| `bridge_match` | en | fr | ru | ar | zh | |
|---|---:|---:|---:|---:|---:|---|
| `exact` | 172 | 113 | 65 | 87 | 83 | present verbatim |
| `normalized` | 0 | 20 | 4 | 1 | 3 | case / diacritics / punctuation |
| `inflected` | 0 | 30 | 96 | 82 | 40 | morphological or word-order variant |
| `latin_untranslated` | 0 | 7 | 8 | 4 | 29 | English name retained — a defect |
| `absent` | 4 | 6 | 3 | 2 | 21 | bridge missing — a defect |
| **`chain_ok`** | **172** | **163** | **165** | **170** | **126** | first three kinds |

Filter on `chain_ok` before chaining `sub_q1` → `sub_q2`; filter on
`bridge_match == "exact"` if you need verbatim substitution.

## Repository layout

```
data/          the dataset
scripts/       build.py · validate.py · make_cross_lingual.py · make_combined.py
               make_figure.py — regenerates assets/example.svg from the data
examples/      quickstart.py
assets/        the README figure
LICENSES/      per-source terms
DATA_CARD.md   provenance, limitations, known defects
```

```bash
python scripts/validate.py     # alignment, schema, hop counts, per-language script checks
sha256sum -c CHECKSUMS.sha256  # verify a download
```

## Licensing

MuSiQue and HotpotQA are distributed under **different** licenses, and HotpotQA's is
copyleft. They are shipped in separate files so either can be used alone under its own
terms. `scripts/make_combined.py` produces a derivative of both, which inherits the more
restrictive terms. See [`LICENSES/`](LICENSES/).

## Limitations

Read [`DATA_CARD.md`](DATA_CARD.md) before publishing results. In brief: translations are
machine-produced and unverified; `hop_seq` is unverified at 3 and 4 hops; decomposition
chains still break on 4–29 records per language (worst in Chinese); and answer strings
sometimes stay in Latin script in non-Latin languages, which depresses exact-match scoring
in a way that conflates *factual correctness* with *answering in the expected language*.

## Citation

```bibtex
@misc{xhop,
  title  = {XHop: Cross-lingual Multi-Hop Question Answering},
  author = {CHANGE-ME},
  year   = {2026},
  url    = {https://github.com/vivian-my/XHop}
}
```
