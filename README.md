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

<figure class="hopfig">
<script type="application/json" class="hop-data">{"id":"hotpotqa_66","model":"Mistral-Nemo-12B","queryLang":"en","languages":{"en":"English","fr":"French","ru":"Russian","ar":"Arabic","zh":"Chinese"},"rtl":["ar"],"question":"What building is opposite the ceremonial meeting place of the Accession Council in the United Kingdom?","gold":"Mark Masons' Hall","hop1":{"en":"<span class=\"hop-e is-bridge\">St James's Palace</span> is the most senior royal palace in the United Kingdom. Located in the City of Westminster, although no longer the principal residence of the monarch, it is the ceremonial meeting place of the Accession Council and the London residence of several members of the royal family.","fr":"Le <span class=\"hop-e is-bridge\">palais de Saint James</span> est le palais royal le plus ancien au Royaume-Uni. Situé dans la ville de Westminster, bien qu'il ne soit plus la résidence principale du monarque, il s'agit du lieu de rencontre cérémoniel du Conseil d'Accession et de la résidence londonienne de plusieurs membres de la famille royale.","ru":"<span class=\"hop-e is-bridge\">Сент-Джеймсский дворец</span> является самым старшим королевским дворцом в Соединенном Королевстве. Находясь в районе Вестминстер, хоть и не являясь больше основной резиденцией монарха, этоcerемoniальное место встречи Совета по восшествию на трон и лондонская резиденция нескольких членов королевской семьи.","ar":"<span class=\"hop-e is-bridge\">قصر سانت جيمس</span> هو أكبر قصر ملكي في المملكة المتحدة. تقع في مدينة ويستمنستر، على الرغم من أنها لم تعد المقر الرئيسي للملك، إلا أنها مكان الاجتماع الاحتفالي لمجلس الانضمام والمقر اللندني لعدد من أعضاء العائلة المالكة.","zh":"<span class=\"hop-e is-bridge\">圣詹姆斯宫</span>是英国最高级的皇宫。 位于威斯敏斯特市，虽然不再是君主的主要住所，但它是即位委员会的庆典会议地点，也是若干王室成员在伦敦的住所。"},"hop2":{"en":"<span class=\"hop-e is-answer\">Mark Masons' Hall</span> in London is the headquarters of The Grand Lodge of Mark Master Masons of England and Wales, which also controls the Royal Ark Mariner degree. It is located in 86 St James's Street in the central London district of St James's, opposite <span class=\"hop-e is-bridge\">St James's Palace</span>. While Freemasons' Hall is the headquarters of the United Grand Lodge of England and the Supreme Grand Chapter of Royal Arch Masons of England, <span class=\"hop-e is-answer\">Mark Masons' Hall</span> is the home of several other important appendant orders of Freemasonry in England and Wales.","fr":"<span class=\"hop-e is-answer\">Mark Masons' Hall</span> à Londres est le siège de la Grande Loge des Maîtres Maçons de Marque d'Angleterre et du Pays de Galles, qui contrôle également le degré de Royal Ark Mariner. Il est situé au 86 St James's Street dans le quartier central de Londres de St James's, en face du <span class=\"hop-e is-bridge\">Palais de St James's</span>. Bien que la Salle des Francs-Maçons soit le siège de la Grande Loge Unie d'Angleterre et du Suprême Grand Chapitre des Maçons du Royal Arc d'Angleterre, la Salle des Maçons de Mark est le foyer de plusieurs autres ordres annexes importants de la Franc-Maçonnerie en Angleterre et au Pays de Galles.","ru":"<span class=\"hop-e is-answer\">Зал Марка Мейсона</span> в Лондоне является штаб-квартирой Великой ложи мастеров-масонов марка Англии и Уэльса, которая также контролирует степень Королевского мариниста. Он расположен на улице Сент-Джеймс, 86 в центральном лондонском районе Сент-Джеймс, напротив <span class=\"hop-e is-bridge\">дворца Сент-Джеймс</span>. Хотя Зал свободных каменщиков является штаб-квартирой Объединенной Великой Ложи Англии и Верховного Великого Chapter Королевских Архитекторов Англии, Зал Марк Мейсонов является домом для нескольких других важных сопутствующих орденов свободного каменщичества в Англии и Уэльсе.","ar":"<span class=\"hop-e is-answer\">قاعة مارك ميسون</span> في لندن هي المقر الرئيسي للجراند لودج لماسون مارك ماستر في إنجلترا وويلز، والتي تتحكم أيضًا في درجة مارينر رويال آرك. يقع في 86 شارع سانت جيمس في منطقة سانت جيمس المركزية بلندن، مقابل <span class=\"hop-e is-bridge\">قصر سانت جيمس</span>. بينما تعتبر قاعة الماسونيين الحر مركزًا للجراند لودج المتحدة لإنجلترا والفصل الأعلى للماسونيين الملكيين في إنجلترا، فإن قاعة الماسونيين مارك هي موطن للعديد من الأوامر التكملية المهمة الأخرى للماسونية في إنجلترا وويلز.","zh":"伦敦的<span class=\"hop-e is-answer\">马克梅森大厅</span>是英格兰和威尔士马克大师石匠大 Lodge 的总部，同时也控制着皇家方舟水手学位。 它位于伦敦市中心圣詹姆斯区的圣詹姆斯街86号，正对着<span class=\"hop-e is-bridge\">圣詹姆斯宫</span>。 虽然共济会大厅是英格兰大公 lodge 和英格兰皇家拱形共济会的总部，但马克共济会大厅是英格兰和威尔士其他一些重要附属共济会秩序的所在地。"},"hop1Role":"bridging &mdash; where the Accession Council meets","hop2Role":"answer-bearing &mdash; what stands opposite it","runs":{"en|en":{"prediction":"Mark Masons' Hall","correct":true,"f1":100},"en|fr":{"prediction":"Mark Masons' Hall","correct":true,"f1":100},"en|ru":{"prediction":"Freemasons' Hall","correct":false,"f1":40},"en|ar":{"prediction":"Freemasons' Hall","correct":false,"f1":40},"en|zh":{"prediction":"St. James's Palace","correct":false,"f1":0},"fr|en":{"prediction":"St. James's Palace","correct":false,"f1":0},"fr|fr":{"prediction":"Mark Masons' Hall","correct":true,"f1":100},"fr|ru":{"prediction":"The Grand Lodge of Mark Master Masons of England and Wales","correct":false,"f1":29},"fr|ar":{"prediction":"Freemasons' Hall","correct":false,"f1":40},"fr|zh":{"prediction":"Freemasons' Hall","correct":false,"f1":40},"ru|en":{"prediction":"Mark Masons' Hall","correct":true,"f1":100},"ru|fr":{"prediction":"Mark Masons' Hall","correct":true,"f1":100},"ru|ru":{"prediction":"The building opposite the ceremonial meeting place of the Accession Council in the United Kingdom is the Freemasons' Hall.","correct":false,"f1":9},"ru|ar":{"prediction":"Freemasons' Hall","correct":false,"f1":40},"ru|zh":{"prediction":"St. James's Palace","correct":false,"f1":0},"ar|en":{"prediction":"St. James's Palace","correct":false,"f1":0},"ar|fr":{"prediction":"Mark Masons' Hall","correct":true,"f1":100},"ar|ru":{"prediction":"The building opposite the ceremonial meeting place of the Accession Council in the United Kingdom is the Grand Lodge of Mark Master Masons.","correct":false,"f1":15},"ar|ar":{"prediction":"Freemasons' Hall","correct":false,"f1":40},"ar|zh":{"prediction":"St. James's Palace","correct":false,"f1":0},"zh|en":{"prediction":"Mark Masons' Hall","correct":true,"f1":100},"zh|fr":{"prediction":"Mark Masons' Hall","correct":true,"f1":100},"zh|ru":{"prediction":"St. James's Palace","correct":false,"f1":0},"zh|ar":{"prediction":"The Grand Lodge of Mark Master Masons in England and Wales","correct":false,"f1":29},"zh|zh":{"prediction":"Mark Masons' Hall","correct":true,"f1":100}}}</script>
<p class="hop-key"><i class="hop-e is-bridge">bridging entity</i><i class="hop-e is-answer">answer</i><span>Mistral-Nemo-12B</span></p>
<div class="hop-body">
<div class="hop-item hop-q"><div class="hop-meta"><span class="hop-k">Question</span><span class="hop-role">English, fixed</span></div><p class="hop-t" dir="auto" data-slot="question">What building is opposite the ceremonial meeting place of the Accession Council in the United Kingdom?</p></div>
<div class="hop-item hop-hop"><div class="hop-meta"><span class="hop-k">Hop-1</span><span class="hop-role">bridging &mdash; where the Accession Council meets</span><div class="hop-langs" data-langs="h1" role="group" aria-label="Language of this passage"><button type="button" data-lang="en" aria-pressed="false">English</button><button type="button" data-lang="fr" aria-pressed="false">French</button><button type="button" data-lang="ru" aria-pressed="false">Russian</button><button type="button" data-lang="ar" aria-pressed="false">Arabic</button><button type="button" data-lang="zh" aria-pressed="false">Chinese</button></div></div><p class="hop-t" dir="auto" data-slot="hop1"></p></div>
<div class="hop-item hop-hop"><div class="hop-meta"><span class="hop-k">Hop-2</span><span class="hop-role">answer-bearing &mdash; what stands opposite it</span><div class="hop-langs" data-langs="h2" role="group" aria-label="Language of this passage"><button type="button" data-lang="en" aria-pressed="false">English</button><button type="button" data-lang="fr" aria-pressed="false">French</button><button type="button" data-lang="ru" aria-pressed="false">Russian</button><button type="button" data-lang="ar" aria-pressed="false">Arabic</button><button type="button" data-lang="zh" aria-pressed="false">Chinese</button></div></div><p class="hop-t" dir="auto" data-slot="hop2"></p></div>
<div class="hop-answer">
<div class="hop-pred"><div class="hop-meta"><span class="hop-k">Prediction</span><span class="hop-badge" data-slot="badge"></span><span class="hop-role" data-slot="pred-note"></span></div><p class="hop-t" dir="auto" data-slot="prediction"></p></div>
<div class="hop-gold"><div class="hop-meta"><span class="hop-k">Gold answer</span></div><p class="hop-t" dir="auto" data-slot="gold">Mark Masons' Hall</p></div>
</div></div>
<style>.hopfig{--ink:#1a1c20;--ink-2:#4a4c52;--ink-3:#6b7280;--line:#ececf0;
--line-2:#d9dae0;--bridge:#7a5c12;--bridge-bg:#faedc4;--answer:#1c6a55;--answer-bg:#d3ece3;
margin:2rem 0;padding:20px 20px 14px;background:#ffffff;
border:1px solid var(--line);border-radius:12px;color:var(--ink);
font-family:'Newsreader Variable',Georgia,serif;font-size:16px;line-height:1.6}
.hopfig *{box-sizing:border-box}
.hopfig .hop-item{padding-bottom:15px;margin-bottom:15px;border-bottom:1px solid var(--line)}
.hopfig .hop-meta{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;margin-bottom:7px}
.hopfig .hop-k{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:10.5px;
letter-spacing:.08em;text-transform:uppercase;font-weight:600;color:var(--ink-3)}
.hopfig .hop-role{font-size:13px;color:var(--ink-3);font-style:italic}
.hopfig .hop-langs{display:flex;gap:2px;background:#f7f7f5;
border:1px solid var(--line);border-radius:8px;padding:2px;margin-left:auto}
.hopfig .hop-langs button{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:11.5px;
line-height:1;padding:5px 9px;border:0;border-radius:6px;background:none;color:var(--ink-3);
cursor:pointer;transition:background .12s ease,color .12s ease}
.hopfig .hop-langs button:hover{color:var(--ink)}
.hopfig .hop-langs button[aria-pressed="true"]{background:var(--ink);color:#fff;font-weight:600}
.hopfig .hop-langs button:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
.hopfig .hop-t{margin:0;color:var(--ink)}
.hopfig .hop-q .hop-t{font-size:18px;line-height:1.5}
.hopfig .hop-hop .hop-t{font-size:15px;line-height:1.65;color:var(--ink-2)}
.hopfig .hop-e{border-radius:3px;padding:1px 3px;font-weight:600}
.hopfig .hop-e.is-bridge{background:var(--bridge-bg);color:var(--bridge)}
.hopfig .hop-e.is-answer{background:var(--answer-bg);color:var(--answer)}
.hopfig .hop-key{display:flex;flex-wrap:wrap;gap:6px 16px;align-items:center;
font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:11px;color:var(--ink-3);margin:0 0 14px}
.hopfig .hop-key i{font-style:normal;border-radius:3px;padding:1px 6px;font-weight:600}
.hopfig .hop-answer{display:grid;grid-template-columns:1fr 1fr;gap:13px}
@media (max-width:560px){.hopfig .hop-answer{grid-template-columns:1fr}
.hopfig .hop-langs{margin-left:0}}
.hopfig .hop-pred,.hopfig .hop-gold{border:1px solid var(--line);border-radius:9px;
padding:11px 13px;background:#f7f7f5}
.hopfig .hop-pred .hop-t,.hopfig .hop-gold .hop-t{font-size:16px;font-weight:600}
.hopfig .hop-badge{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:10px;
font-weight:600;letter-spacing:.03em;padding:2px 8px;border-radius:999px;
border:1px solid var(--line-2);color:var(--ink)}
.hopfig .hop-badge.is-ok{background:var(--ink);color:#fff;border-color:var(--ink)}
.hopfig .hop-badge.is-ok::before{content:"\2713 "}
.hopfig .hop-badge.is-bad{background:#fff;color:var(--ink);border-color:var(--line-2)}
.hopfig .hop-badge.is-bad::before{content:"\2717 "}
.hopfig .hop-pred.is-ok{border-left:3px solid var(--ink)}
.hopfig .hop-pred.is-bad{border-left:3px solid var(--line-2)}
.hopfig [dir="rtl"]{text-align:right}
@media (prefers-reduced-motion:reduce){.hopfig *{transition:none!important}}</style>
<script>(function(){
var fig=document.currentScript.closest('.hopfig');
if(!fig||fig.dataset.hopInit)return;fig.dataset.hopInit='1';
var D=JSON.parse(fig.querySelector('.hop-data').textContent);
var state={h1:'en',h2:'en'};
function slot(n){return fig.querySelector('[data-slot="'+n+'"]');}
function put(name,txt,lang){var el=slot(name);if(!el)return;
el.textContent=txt;
if(lang)el.setAttribute('dir',D.rtl.indexOf(lang)>=0?'rtl':'ltr');}
function putHTML(name,html,lang){var el=slot(name);if(!el)return;
el.innerHTML=html;
if(lang)el.setAttribute('dir',D.rtl.indexOf(lang)>=0?'rtl':'ltr');}
function render(){
['h1','h2'].forEach(function(k){
var hop=k==='h1'?'hop1':'hop2',lang=state[k];
putHTML(hop,D[hop][lang],lang);
fig.querySelectorAll('[data-langs="'+k+'"] button').forEach(function(b){
b.setAttribute('aria-pressed',b.dataset.lang===lang?'true':'false');});});
var run=D.runs[state.h1+'|'+state.h2];
var pred=fig.querySelector('.hop-pred'),badge=slot('badge');
pred.classList.remove('is-ok','is-bad');badge.classList.remove('is-ok','is-bad');
put('prediction',run.prediction,D.queryLang);
badge.textContent=run.correct?'correct':'wrong';
badge.classList.add(run.correct?'is-ok':'is-bad');
pred.classList.add(run.correct?'is-ok':'is-bad');
put('pred-note','F1 '+run.f1);}
fig.querySelectorAll('[data-langs] button').forEach(function(b){
b.addEventListener('click',function(){
state[b.closest('[data-langs]').dataset.langs]=b.dataset.lang;render();});});
render();
})();</script>
</figure>


<p align="center">
  <img src="assets/example.svg" alt="A two-hop XHop example with evidence in French and Chinese" width="800">
  <br>
  <sub>An English question answered using context in French and Chinese.</sub>
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
