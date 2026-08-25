# Do Language Models Reason Across Languages?

**X-HOP: Multilingual multi-hop question answering dataset**

XHop extends [MuSiQue](https://github.com/stonybrooknlp/musique) and
[HotpotQA](https://hotpotqa.github.io/) from English to French, Russian, Arabic,
and Chinese. Because the five language files are aligned, the language of the
question and each supporting passage can be controlled independently.

<p align="center">
  <img src="assets/example.svg" alt="A two-hop XHop example with evidence in French and Chinese" width="800">
</p>

| | |
|---|---|
| Languages | English, French, Russian, Arabic, Chinese |
| Sources | MuSiQue and HotpotQA |
| Reasoning depth | 2, 3, and 4 hops |
| Records | 1,312 per language; 6,560 total |
| Format | Aligned UTF-8 JSONL |

> [!NOTE]
> Translation provenance, citation details, and final license texts are still
> being completed. Review [DATA_CARD.md](DATA_CARD.md) and
> [LICENSES/](LICENSES/) before publishing results or redistributing the data.

## Quick start

XHop has no runtime dependencies. Clone the repository and run the example:

```bash
git clone https://github.com/vivian-my/X-Hop.git
cd X-Hop
python examples/quickstart.py
```

Or load one language directly:

```python
import json
from pathlib import Path


def load(split, source, language):
    path = Path("data") / split / source / f"{language}.jsonl"
    with path.open(encoding="utf-8") as file:
        return [json.loads(line) for line in file]


records = load("two_hop", "hotpotqa", "en")
record = records[0]

print(record["question"])
print(record["answer"])

# hop_seq maps reasoning order to positions in answers.
passages = [record["answers"][position] for position in record["hop_seq"]]
paragraphs = [" ".join(passage["sentences"]) for passage in passages]
```

## Build a cross-lingual condition

The same line contains the same example in every language file. This makes it
possible to combine an English question, a Russian bridging passage, and a
Chinese answer-bearing passage:

```bash
python scripts/make_cross_lingual.py \
    --split two_hop \
    --source hotpotqa \
    --query en \
    --hops ru zh \
    --out en_ru_zh.jsonl
```

For all passage-language combinations, replace `--hops ... --out ...` with
`--grid --out-dir cells/`.

## Dataset contents

| Split | Source | Records per language |
|---|---|---:|
| `two_hop` | MuSiQue | 627 |
| `two_hop` | HotpotQA | 176 |
| `three_hop` | MuSiQue | 327 |
| `four_hop` | MuSiQue | 182 |

Files follow this layout:

```text
data/<split>/<source>/<language>.jsonl
```

Language codes are `en`, `fr`, `ru`, `ar`, and `zh`. Within one split and
source, line `i` has the same record ID in all five files.

## Record fields

| Field | Meaning |
|---|---|
| `id` | Stable aligned record ID |
| `question`, `answer` | Query and target answer |
| `answers` | Gold passages, each with sentences and evidence indices |
| `non_answers` | Distractor passages |
| `hop_seq` | Reasoning order as positions in `answers` |
| `sub_q1`, `sub_q2` | HotpotQA two-hop decomposition; otherwise `null` |

Join sentences only within a passage. Use `hop_seq` to order the resulting
paragraphs; do not merge different positions in `answers`.

HotpotQA provides decomposed questions for all 176 two-hop examples. See the
data card for decomposition quality and filtering guidance.

## Important limitations

- Non-English text is machine-translated and not human-verified.
- Three- and four-hop `hop_seq` values preserve file order but have not been
  verified as reasoning order.
- Exact-match scores can penalize correct answers written in a different script
  or language.
- XHop inherits artifacts and shortcuts from MuSiQue and HotpotQA.

See [DATA_CARD.md](DATA_CARD.md) for provenance, repairs, decomposition quality,
intended use, and the complete limitations.

## Repository layout

```text
data/          aligned JSONL files
examples/      minimal loading example
scripts/       build, validation, and cross-lingual generation
assets/        README figure
LICENSES/      source-specific licensing notes
DATA_CARD.md   provenance and limitations
```

## Licensing

MuSiQue and HotpotQA have different terms and are stored separately. Generated
files that combine both sources inherit the more restrictive terms. See
[LICENSES/](LICENSES/) before use or redistribution.
