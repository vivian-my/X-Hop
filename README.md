<div align="center">

# Do Language Models Reason Across Languages?

**X-HOP · A multilingual multi-hop question answering dataset**

![Languages](https://img.shields.io/badge/languages-5-4c6ef5)
![Records](https://img.shields.io/badge/records-6%2C560-12b886)
![Hops](https://img.shields.io/badge/hops-2%20%C2%B7%203%20%C2%B7%204-f59f00)
![Format](https://img.shields.io/badge/format-JSONL-7950f2)

</div>

---

X-HOP extends [MuSiQue](https://github.com/stonybrooknlp/musique) and [HotpotQA](https://hotpotqa.github.io/) from English to French, Russian, Arabic, and Chinese. All data instances are multi-parallel.  


<p align="center">
  <img src="assets/Screenshot 2026-09-01 at 12.52.46.png" alt="A two-hop XHop example with evidence in French and English" width="600">
  <br>
  <sub>An English question answered using context in different languages. See more cases in: <a href="https://vivian-my.github.io/X-Hop/assets/demo.html"><b>Link</b></a></sub>
</p>

## Dataset Statistics

| | |
|:---|:---|
| **Languages** | English, French, Russian, Arabic, Chinese |
| **Sources** | MuSiQue and HotpotQA |
| **Reasoning depth** | 2, 3, and 4 hops |

## Quick start

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

## Record fields

| Field | Meaning |
|:---|:---|
| `question`, `answer` | Query and target answer |
| `answers` | Gold passages, each with sentences and evidence indices |
| `non_answers` | Distractor passages |
| `hop_seq` | Reasoning order as positions in `answers` |
| `sub_q1`, `sub_q2` | HotpotQA two-hop decomposition; otherwise `null` |
