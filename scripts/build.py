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
  MuSiQue 2-hop must be the POST-reorder copy. A semantic audit found 16 residual
  reversed records in that copy; MUSIQUE_2HOP_REVERSED corrects them at build
  time. A pre-reorder copy exists in which 331 of 627 records are reversed and
  must not be used.

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


def replace_text(value, replacements):
    """Apply literal, record-scoped translation repairs recursively."""
    if isinstance(value, str):
        for old, new in replacements.items():
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [replace_text(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: replace_text(item, replacements)
                for key, item in value.items()}
    return value


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

# English passages were manually checked for the invariant that hop 1 supplies
# the bridge and hop 2 contains the gold answer. Reasoning order is language-
# invariant, so the same overrides apply to every aligned translation.
MUSIQUE_2HOP_REVERSED = {
    65, 80, 113, 138, 277, 278, 349, 354,
    420, 425, 435, 480, 509, 561, 567, 613,
}

# Translation repairs are deliberately narrow and reviewable.  They fix
# machine-translation fragments in gold answers (and, where necessary, the
# corresponding answer-bearing sentence).  Latin text that is part of an
# official name or acronym -- BBC, EPA, FSMA, KUAT-TV, etc. -- is not a defect
# and is intentionally left alone.
ZH_ROOSTER_REPAIRS = {
    "美国法 Marshal Rooster Cogburn": "美国法警鲁斯特·科格本",
    "约翰·韦恩饰演美国。": "约翰·韦恩饰演",
    "马歇尔·公鸡·科格本。": "美国法警鲁斯特·科格本。",
}
ZH_DYNASTY_REPAIRS = {
    "王朝重新 regrouped 并击败了葡萄牙人": "王朝重新集结并击败了葡萄牙人",
    "王朝在1613年重新集结并击败了葡萄牙，1614年击败了暹罗。":
        "王朝重新集结并击败了葡萄牙人（1613年），随后于1614年击败了暹罗。",
}
TEXT_REPLACEMENTS = {
    ("ru", "hotpotqa_468"): {
        "Паола Д'Alessandris": "Паула Д'Алессандрис",
        "Паула Д'Alessandris": "Паула Д'Алессандрис",
    },
    ("ru", "hotpotqa_713"): {"A1 Записи": "A1 Recordings"},
    ("ru", "hotpotqa_925"): {"ЛидерTeamsters": "лидер профсоюза Teamsters"},
    ("ru", "hotpotqa_953"): {
        "Оскар за лучшую художественную direction":
            "премию «Оскар» за лучшую работу художника-постановщика",
        "премию Академии за Лучший Художественный Дирекшн":
            "премию «Оскар» за лучшую работу художника-постановщика",
        "Дело странного Бенжамена Баттона": "Загадочная история Бенджамина Баттона",
    },
    ("ar", "hotpotqa_478"): {"قلعة سكيب ton": "قلعة سكيبطن"},
    ("ar", "hotpotqa_820"): {
        "المبلغ المحسوم من قبل bookmaker": "المبلغ الذي يتقاضاه المراهن",
    },
    ("ar", "musique_3hop_209"): {"كو Phi Phi Leh": "كوه في في ليه"},
    ("ar", "musique_2hop_252"): {"بلدية داليشيče": "بلدية داليشي"},
    ("ar", "musique_2hop_571"): {"مايكل بuble": "مايكل بوبليه"},
    ("zh", "hotpotqa_713"): {"A1 录音": "A1唱片"},
    ("ar", "hotpotqa_260"): {
        "هو ملحن سينما هندي": "هو ملحن موسيقى للسينما الناطقة بالهندية",
    },
    ("zh", "hotpotqa_260"): {
        "是印度电影音乐作曲家": "是印地语电影音乐作曲家",
    },
    ("zh", "hotpotqa_953"): {
        "最佳美术指导学院奖": "奥斯卡最佳艺术指导奖",
        "本杰明·巴顿的奇妙经历": "本杰明·巴顿奇事",
    },
    ("fr", "hotpotqa_940"): {"La Notorious Bettie Page": "The Notorious Bettie Page"},
    ("fr", "hotpotqa_953"): {
        "L'étrange cas de Benjamin Button": "Le Cas étrange de Benjamin Button",
    },
    ("ru", "hotpotqa_373"): {"Ставки Алабамы": "Алабама Стейкс"},
    ("ru", "hotpotqa_725"): {"Wet 'n Wild Орландо": "Wet 'n Wild Orlando"},
    ("ar", "hotpotqa_373"): {"سباق ألاباما": "ألاباما ستيكس"},
    ("ar", "hotpotqa_551"): {"الأفسنتين": "أبسنت"},
    ("ar", "hotpotqa_725"): {
        "مياه 'ن برية أورلاندو": "ويت ن وايلد أورلاندو",
        "مياه 'ن برية": "ويت ن وايلد",
    },
    ("ar", "hotpotqa_940"): {"بيتي بيدج الشهيرة": "بيتي بيج الشهيرة"},
    ("ar", "hotpotqa_953"): {
        "حالة بنجامين باتون الفضولية": "حالة بنجامين باتون الغريبة",
    },
    ("zh", "hotpotqa_261"): {"维特利乌斯": "维特里乌斯"},
    ("zh", "hotpotqa_373"): {"阿拉巴马州 Stakes": "阿拉巴马锦标赛"},
    ("zh", "hotpotqa_725"): {"湿滑与狂野奥兰多": "湿身乐园奥兰多"},
    ("zh", "hotpotqa_894"): {"类似于电子宠物": "类似于拓麻歌子"},
    ("zh", "hotpotqa_940"): {"臭名昭著的贝蒂·佩吉": "臭名昭著的贝蒂·佩奇"},
    ("zh", "hotpotqa_991"): {
        "大曼彻斯特的Metrolink": "大曼彻斯特轻轨",
        "大曼彻斯特Metrolink轻轨系统": "大曼彻斯特轻轨系统",
    },
    **{("zh", f"musique_2hop_{i}"): ZH_ROOSTER_REPAIRS
       for i in range(95, 99)},
    **{("zh", f"musique_3hop_{i}"): ZH_DYNASTY_REPAIRS
       for i in (283, 296, 308, 316, 323, 325, 326)},
    **{("zh", f"musique_4hop_{i}"): ZH_DYNASTY_REPAIRS
       for i in (67, 75, *range(80, 105))},
}


# Clear upstream QA defects: these records had a malformed question, a gold
# label that answered a different question, or insufficient support indices.
# Values are kept aligned across all five languages.
RECORD_OVERRIDES = {
    ("en", 260): {
        "question": "The composer of India's first science-fiction film series writes music for cinema in which language?",
        "answer": "Hindi",
    },
    ("fr", 260): {
        "question": "Dans quelle langue cinématographique compose le compositeur de la première série de films de science-fiction indienne ?",
        "answer": "hindi",
    },
    ("ru", 260): {
        "question": "На каком языке снимается кино, для которого пишет музыку композитор первой индийской научно-фантастической киносерии?",
        "answer": "хинди",
    },
    ("ar", 260): {
        "question": "بأي لغة تُنتج السينما التي يؤلف لها الموسيقى ملحن أول سلسلة أفلام خيال علمي هندية؟",
        "answer": "الهندية",
    },
    ("zh", 260): {
        "question": "印度第一部科幻电影系列的作曲家为哪种语言的电影创作音乐？",
        "answer": "印地语",
    },
    ("en", 261): {
        "question": "Galeria Fundana was which wife of the third emperor in the Year of the Four Emperors?",
        "answer": "second wife",
    },
    ("fr", 261): {
        "question": "Galeria Fundana était quelle épouse du troisième empereur de l'Année des quatre empereurs ?",
        "answer": "la deuxième femme",
    },
    ("ru", 261): {
        "question": "Какой женой третьего императора в Год четырёх императоров была Галерия Фундана?",
        "answer": "второй женой",
    },
    ("ar", 261): {
        "question": "أي زوجة للإمبراطور الثالث في عام الأباطرة الأربعة كانت غاليريا فوندانا؟",
        "answer": "الزوجة الثانية",
    },
    ("zh", 261): {
        "question": "加列里娅·丰达娜是四帝之年第三位皇帝的第几任妻子？",
        "answer": "第二任妻子",
    },
    ("en", 373): {
        "question": "When was the horse that won the Alabama Stakes at Saratoga Race Course born?",
        "answer": "February 1, 1999",
    },
    ("fr", 373): {
        "question": "Quand est née la jument qui a remporté les Alabama Stakes à l'hippodrome de Saratoga ?",
        "answer": "1er février 1999",
    },
    ("ru", 373): {
        "question": "Когда родилась лошадь, выигравшая скачки «Алабама Стейкс» на ипподроме Саратога?",
        "answer": "1 февраля 1999 года",
    },
    ("ar", 373): {
        "question": "متى وُلدت الفرس التي فازت بسباق ألاباما ستيكس في مضمار ساراتوغا؟",
        "answer": "1 فبراير 1999",
    },
    ("zh", 373): {
        "question": "在萨拉托加赛马场赢得阿拉巴马锦标赛的赛马出生于何时？",
        "answer": "1999年2月1日",
    },
    ("en", 551): {
        "question": "The drink featured in an NBC Hard Copy segment that used selections from Quintessentially Unreal is commonly called what?",
    },
    ("fr", 551): {
        "question": "Comment appelle-t-on couramment la boisson présentée dans un segment de NBC Hard Copy utilisant des extraits de Quintessentially Unreal ?",
    },
    ("ru", 551): {
        "question": "Как обычно называют напиток, которому был посвящён сюжет NBC Hard Copy с фрагментами альбома Quintessentially Unreal?",
    },
    ("ar", 551): {
        "question": "ما الاسم الشائع للمشروب الذي تناولته فقرة من برنامج NBC Hard Copy استخدمت مقاطع من ألبوم Quintessentially Unreal؟",
    },
    ("zh", 551): {
        "question": "NBC《Hard Copy》节目中使用《Quintessentially Unreal》选段介绍的饮品通常被称为什么？",
        "answer": "绿妖精",
    },
    ("en", 725): {"answer": "Volcano Bay"},
    ("fr", 725): {"answer": "Volcano Bay"},
    ("ru", 725): {"answer": "Volcano Bay"},
    ("ar", 725): {
        "question": "ما الحديقة التي حلّت محل أول حديقة مائية أمريكية صممها مؤسس سي وورلد؟",
        "answer": "بركان باي",
    },
    ("zh", 725): {"answer": "火山湾"},
    ("en", 851): {"answer": "Magic formula investing"},
    ("fr", 851): {"answer": "investissement selon la formule magique"},
    ("ru", 851): {"answer": "Магическая формула инвестирования"},
    ("ar", 851): {"answer": "استثمار الصيغة السحرية"},
    ("zh", 851): {"answer": "魔法公式投资"},
    ("en", 894): {
        "question": "Which company released the device that is similar to Princess Max?",
    },
    ("fr", 894): {
        "question": "Quelle entreprise a commercialisé l'appareil similaire à Princess Max ?",
    },
    ("ru", 894): {
        "question": "Какая компания выпустила устройство, похожее на Princess Max?",
        "answer": "Bandai",
    },
    ("ar", 894): {
        "question": "ما الشركة التي أصدرت الجهاز المشابه للأميرة ماكس؟",
    },
    ("zh", 894): {
        "question": "哪家公司发行了与公主麦克斯相似的设备？",
    },
    ("en", 940): {"answer": "Mary Harron"},
    ("fr", 940): {"answer": "Mary Harron"},
    ("ru", 940): {"answer": "Мэри Харрон"},
    ("ar", 940): {"answer": "ماري هارون"},
    ("zh", 940): {"answer": "玛丽·哈伦"},
    ("en", 953): {
        "question": "Which Academy Award for art direction did the 2008 American romantic drama directed by David Fincher win?",
    },
    ("fr", 953): {
        "question": "Quel Oscar de direction artistique le drame romantique américain de 2008 réalisé par David Fincher a-t-il remporté ?",
    },
    ("ru", 953): {
        "question": "Какую премию «Оскар» за художественное оформление получил американский романтический фильм 2008 года Дэвида Финчера?",
    },
    ("ar", 953): {
        "question": "ما جائزة الأوسكار الخاصة بالإخراج الفني التي فاز بها فيلم الدراما الرومانسية الأمريكي لعام 2008 من إخراج ديفيد فينشر؟",
    },
    ("zh", 953): {
        "question": "大卫·芬奇执导的2008年美国浪漫剧情片获得了哪项奥斯卡艺术指导奖？",
    },
}

SUPPORTING_INDEX_OVERRIDES = {
    260: [[0], [0, 2, 3]],
    373: [[0, 3], [0, 1]],
    551: [[0, 2], [2]],
    725: [[0, 1], [1]],
}


# Fresh, human-reviewed renderings of decomposition fields that independently
# translated the bridge entity two different ways (or left it in English).
# The three descriptive upstream chains below do not state the bridge at all;
# that is a source-annotation limitation, not something translation can repair.
NON_EXPLICIT_BRIDGE_IDS = {171, 315, 333}
DECOMPOSITION_OVERRIDES = {
    ("en", 916): {
        "q2_question": "What is another name, in Swedish, for Hulder?",
    },
    ("en", 260): {
        "q2_question": "The composer of Krrish writes music for cinema in which language?",
    },
    ("fr", 260): {
        "q2_question": "Le compositeur de Krrish compose pour le cinéma dans quelle langue ?",
    },
    ("ru", 260): {
        "q1_answer": "Крриш",
        "q2_question": "Для кино на каком языке пишет музыку композитор «Крриш»?",
    },
    ("ar", 260): {
        "q2_question": "للسينما الناطقة بأي لغة يؤلف ملحن كريش الموسيقى؟",
    },
    ("en", 261): {
        "q2_question": "Galeria Fundana was which wife of Vitellius?",
    },
    ("fr", 261): {
        "q2_question": "Galeria Fundana était quelle épouse de Vitellius ?",
    },
    ("ru", 261): {
        "q2_question": "Какой женой Вителлия была Галерия Фундана?",
    },
    ("ar", 261): {
        "q2_question": "أي زوجة لفيتليوس كانت غاليريا فوندانا؟",
    },
    ("zh", 261): {
        "q2_question": "加列里娅·丰达娜是维特里乌斯的第几任妻子？",
    },
    ("en", 373): {
        "q2_question": "When was Farda Amiga, winner of the Alabama Stakes, born?",
    },
    ("fr", 373): {
        "q2_question": "Quand est née Farda Amiga, gagnante des Alabama Stakes ?",
    },
    ("ru", 373): {
        "q1_answer": "Алабама Стейкс",
        "q2_question": "Когда родилась Фарда Амига, победительница «Алабама Стейкс»?",
    },
    ("ar", 373): {
        "q2_question": "متى وُلدت فاردة أميغا، الفائزة بسباق ألاباما ستيكس؟",
    },
    ("zh", 373): {
        "q1_answer": "阿拉巴马锦标赛",
        "q2_question": "阿拉巴马锦标赛冠军法尔达·阿米加出生于何时？",
    },
    ("en", 551): {
        "q1_question": "Which drink was featured in an NBC Hard Copy segment using selections from Quintessentially Unreal?",
    },
    ("fr", 551): {
        "q1_question": "Quelle boisson a été présentée dans un segment de NBC Hard Copy utilisant des extraits de Quintessentially Unreal ?",
    },
    ("ru", 551): {
        "q1_question": "Какому напитку был посвящён сюжет NBC Hard Copy с фрагментами альбома Quintessentially Unreal?",
    },
    ("ar", 551): {
        "q1_question": "ما المشروب الذي تناولته فقرة من NBC Hard Copy استخدمت مقاطع من ألبوم Quintessentially Unreal؟",
    },
    ("zh", 551): {
        "q1_question": "NBC《Hard Copy》节目中使用《Quintessentially Unreal》选段介绍了哪种饮品？",
    },
    ("en", 725): {
        "q1_answer": "Wet 'n Wild Orlando",
        "q2_question": "Which park replaced Wet 'n Wild Orlando?",
    },
    ("fr", 725): {
        "q1_answer": "Wet 'n Wild Orlando",
        "q2_question": "Quel parc a remplacé Wet 'n Wild Orlando ?",
    },
    ("ru", 725): {
        "q1_answer": "Wet 'n Wild Orlando",
        "q2_question": "Какой парк заменил Wet 'n Wild Orlando?",
    },
    ("ar", 725): {
        "q1_answer": "ويت ن وايلد أورلاندو",
        "q2_question": "ما الحديقة التي حلّت محل ويت ن وايلد أورلاندو؟",
    },
    ("zh", 725): {
        "q1_answer": "湿身乐园奥兰多",
        "q2_question": "哪个公园取代了湿身乐园奥兰多？",
    },
    ("ar", 851): {
        "q1_answer": "جويل غرينبلات",
        "q2_question": "أي تقنية وضعها جويل غرينبلات؟",
    },
    ("en", 894): {"q2_question": "Which company released Tamagotchi?"},
    ("fr", 894): {"q2_question": "Quelle entreprise a commercialisé Tamagotchi ?"},
    ("ru", 894): {"q2_question": "Какая компания выпустила Тамагочи?"},
    ("ar", 894): {
        "q1_answer": "تاماغوتشي",
        "q2_question": "ما الشركة التي أصدرت التاماغوتشي؟",
    },
    ("en", 940): {
        "q2_question": "Which Canadian filmmaker made The Notorious Bettie Page?",
    },
    ("fr", 940): {
        "q1_answer": "The Notorious Bettie Page",
        "q2_question": "Quelle cinéaste canadienne a réalisé The Notorious Bettie Page ?",
    },
    ("ru", 940): {
        "q2_question": "Какая канадская кинорежиссёр сняла «Знаменитая Бетти Пейдж»?",
    },
    ("ar", 940): {
        "q1_answer": "بيتي بيج الشهيرة",
        "q2_question": "أي مخرجة كندية صنعت فيلم «بيتي بيج الشهيرة»؟",
    },
    ("zh", 940): {
        "q2_question": "哪位加拿大电影制作人拍摄了《臭名昭著的贝蒂·佩奇》？",
    },
    ("en", 953): {
        "q2_question": "Which Academy Award for art direction did The Curious Case of Benjamin Button win?",
    },
    ("fr", 953): {
        "q2_question": "Quel Oscar de direction artistique Le Cas étrange de Benjamin Button a-t-il remporté ?",
    },
    ("ru", 953): {
        "q1_answer": "Загадочная история Бенджамина Баттона",
        "q2_question": "Какую премию «Оскар» за художественное оформление получила «Загадочная история Бенджамина Баттона»?",
    },
    ("ar", 953): {
        "q2_question": "ما جائزة الأوسكار الخاصة بالإخراج الفني التي فاز بها فيلم «حالة بنجامين باتون الغريبة»؟",
    },
    ("zh", 953): {
        "q1_answer": "本杰明·巴顿奇事",
        "q2_question": "《本杰明·巴顿奇事》获得了哪项奥斯卡艺术指导奖？",
    },
    ("fr", 143): {"q2_question": "De qui parlait Quête Interdite ?"},
    ("fr", 147): {
        "q2_question": "Quel numéro d’album est À l'intérieur du cirque électrique ?",
    },
    ("fr", 194): {
        "q2_question": "Quel rôle Thomas Doherty a-t-il joué dans la sitcom Le Pavillon ?",
    },
    ("fr", 425): {
        "q2_question": "Sur quel album figurait Nous avons trouvé l'amour ?",
    },
    ("fr", 476): {
        "q2_question": "En quel mois Parfait 10 a-t-il reconnu Nikita Gross ?",
    },
    ("fr", 518): {"q1_answer": "Christian Rivers"},
    ("fr", 561): {
        "q1_answer": "6,5 × 55 mm",
        "q2_question": "Quelle autre nation utilisait également le calibre 6,5 × 55 mm ?",
    },
    ("fr", 874): {
        "q2_question": "Sur quels continents se trouve la Région néotropicale ?",
    },
    ("fr", 916): {
        "q2_question": "Quel est un autre nom, en suédois, pour Hulder ?",
    },
    ("fr", 999): {
        "q2_question": "Quelle entreprise britannique a participé à l'enregistrement d'Aurores Boréales ?",
    },
    ("ru", 147): {
        "q2_question": "Каким по счёту альбомом был «Внутри Электрического Цирка»?",
    },
    ("ru", 338): {
        "q1_answer": "спортивный комплекс ESPN Wide World of Sports",
        "q2_question": "Сколько площадок включает спортивный комплекс ESPN Wide World of Sports?",
    },
    ("ru", 419): {
        "q2_question": "К какому типу игр относится «Секретный мир»?",
    },
    ("ru", 569): {"q2_question": "Где публиковалась «Южная Жизнь»?"},
    ("ru", 577): {"q2_question": "Где образовалась группа «Базкокс»?"},
    ("ru", 728): {"q2_question": "В каком городе была основана группа «Фолл Аут Бой»?"},
    ("ru", 820): {
        "q2_question": "Какую часть ставки обозначает существительное «Вигориш»?",
    },
    ("ru", 855): {"q2_question": "Кто приобрёл «Золотой самородок Лас-Вегас»?"},
    ("ru", 916): {"q2_question": "Как по-шведски также называется Хулдер?"},
    ("ru", 952): {
        "q1_answer": "Cars",
        "q2_question": "Какого места в британском чарте достиг сингл Cars?",
    },
    ("ru", 975): {
        "q1_answer": "AFI",
        "q2_question": "Сколько концертных альбомов выпустила AFI?",
    },
    ("ar", 143): {"q2_question": "عمّن كانت المغامرة المحرمة؟"},
    ("ar", 147): {"q2_question": "ما ترتيب ألبوم داخل السيرك الكهربائي؟"},
    ("ar", 338): {
        "q1_answer": "مجمع ESPN وايد وورلد أوف سبورتس",
        "q2_question": "كم عدد الملاعب في مجمع ESPN وايد وورلد أوف سبورتس؟",
    },
    ("ar", 569): {"q2_question": "أين نُشرت جنوب المعيشة؟"},
    ("ar", 594): {"q2_question": "إكستنتاشن هو الاسم الفني لأي مغني راب من لودرهيل بفلوريدا؟"},
    ("ar", 637): {
        "q1_answer": "يهوه",
        "q2_question": "إلى من يشير اسم يهوه؟",
    },
    ("ar", 916): {"q2_question": "ما الاسم السويدي الآخر لهولدر؟"},
    ("zh", 0): {"q2_question": "雪莉·坦普尔担任过什么政府职位？"},
    ("zh", 3): {"q2_question": "安德罗斯科金银行大会堂可以容纳多少人？"},
    ("zh", 13): {"q2_question": "德尔顿城堡位于哪个沿海地区的南侧？"},
    ("zh", 17): {"q2_question": "马格西·博格斯有什么突出特征？"},
    ("zh", 41): {"q2_question": "兰金/巴斯制作最出名的是哪类作品？"},
    ("zh", 71): {"q2_question": "萨罗德属于哪一类乐器？"},
    ("zh", 86): {"q2_question": "特内里费是哪个较大地区人口最多的岛屿？"},
    ("zh", 124): {"q2_question": "达令河有多长？"},
    ("zh", 138): {
        "q1_answer": "传送门",
        "q2_question": "传送门是2012年哪款动作冒险游戏的一部分？",
    },
    ("zh", 143): {"q2_question": "禁忌任务讲述的是谁？"},
    ("zh", 147): {"q2_question": "电动马戏团内是第几张专辑？"},
    ("zh", 199): {
        "q1_answer": "侠盗一号",
        "q2_question": "拉谢尔·艾米·贝纳特在《侠盗一号》中担任什么角色？",
    },
    ("zh", 230): {
        "q1_answer": "安特里姆郡",
        "q2_question": "安特里姆郡每平方英里的人口密度是多少？",
    },
    ("zh", 235): {"q2_question": "什么文学风格描述了《电气酷饮酸性测试》？"},
    ("zh", 244): {
        "q1_answer": "党卫队上级集团领袖",
        "q2_question": "在1942年4月之前，哪个军衔高于党卫队上级集团领袖？",
    },
    ("zh", 258): {
        "q1_answer": "林肯郡高级治安官",
        "q2_question": "林肯郡高级治安官何时更换？",
    },
    ("zh", 260): {"q2_question": "《克里希》的作曲家为哪种语言的电影创作音乐？"},
    ("zh", 309): {"q2_question": "克里斯蒂安·耶利奇与弗雷德·格尔克有什么关系？"},
    ("zh", 320): {"q2_question": "庞巴迪公司的总部在哪里？"},
    ("zh", 323): {"q2_question": "罗亚吉尔加的英文意思是什么？"},
    ("zh", 338): {
        "q1_answer": "ESPN世界体育中心",
        "q2_question": "ESPN世界体育中心有多少个场馆？",
    },
    ("zh", 340): {"q2_question": "博罗代尔位于哪个行政区？"},
    ("zh", 357): {"q2_question": "温特哈文，佛罗里达是哪个购物中心的所在地？"},
    ("zh", 382): {"q2_question": "兹维兹丹·米西莫维奇在2008—09赛季为沃尔夫斯堡贡献了多少次助攻？"},
    ("zh", 404): {"q2_question": "西德·詹姆斯原本是哪国人？"},
    ("zh", 443): {"q2_question": "布依大坝有多大？"},
    ("zh", 471): {"q2_question": "布莱恩·麦坎（棒球）获得过多少次银棒奖？"},
    ("zh", 476): {"q2_question": "完美10在哪个月认可了尼基塔·格罗斯？"},
    ("zh", 517): {"q2_question": "乌巴的军衔是什么？"},
    ("zh", 533): {"q2_question": "舍普德·尼姆酒厂成立于哪一年？"},
    ("zh", 569): {"q2_question": "南方生活在哪里出版？"},
    ("zh", 575): {"q2_question": "忙碌的菲利普斯在2011年获得了什么奖？"},
    ("zh", 577): {"q2_question": "巴兹科克斯在哪里成立？"},
    ("zh", 612): {"q2_question": "失落公路唱片为蒂夫·梅里特发行了多少张专辑？"},
    ("zh", 713): {
        "q1_answer": "《未来》（未来专辑）",
        "q2_question": "《未来》（未来专辑）于2017年由哪个厂牌发行？",
    },
    ("zh", 728): {
        "q1_answer": "打倒男孩",
        "q2_question": "打倒男孩在哪个城市成立？",
    },
    ("zh", 755): {"q2_question": "哈兰德与沃尔夫位于哪个城市？"},
    ("zh", 766): {"q2_question": "布里安娜·科里根的《时间》来自哪个国家？"},
    ("zh", 820): {"q2_question": "水钱这个名词指赌注的哪一部分？"},
    ("zh", 835): {"q2_question": "克里斯蒂斯海滩，南澳大利亚位于哪个主要城市？"},
    ("zh", 882): {
        "q1_answer": "杜克·米卡",
        "q2_question": "杜克·米卡是哪国人？",
    },
    ("zh", 885): {"q2_question": "罗纳尔多推广的一种足球动作最初据称由哪位球员使用？"},
    ("zh", 894): {
        "q1_answer": "拓麻歌子",
        "q2_question": "拓麻歌子由哪个公司发行？",
    },
    ("zh", 915): {
        "q1_answer": "国道",
        "q2_question": "国道位于哪里？",
    },
    ("zh", 916): {"q2_question": "胡尔德在瑞典语中还有什么名称？"},
    ("zh", 922): {"q2_question": "乡村舞曲在什么时候最流行？"},
    ("zh", 996): {"q2_question": "皇帝腓特烈二世属于哪个王朝？"},
}

FIELDS = ["id", "source", "type", "n_hops", "question", "answer",
          "answers", "non_answers", "hop_seq", "hop_seq_verified",
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


def pack_answers(answers, supporting_indices):
    """Embed sentence-level support annotations in their gold passages."""
    assert len(answers) == len(supporting_indices)
    return [{"title": title,
             "sentences": sentences,
             "supporting_sentence_indices": indices}
            for (title, sentences), indices in zip(answers, supporting_indices)]


def pack_musique_answers(r):
    """Embed MuSiQue's sentence annotations in `answers`.

    MuSiQue marks every sentence of every gold passage as supporting, in answer
    order. Verify that upstream still has that shape before converting it so a
    source-format change cannot silently corrupt the release.
    """
    expected = [[title, j]
                for title, sentences in r["answers"]
                for j in range(len(sentences))]
    assert r["supporting_facts"] == expected, \
        f"{r.get('id', '<unknown>')}: unexpected MuSiQue supporting_facts"
    supporting = [list(range(len(sentences))) for _, sentences in r["answers"]]
    return pack_answers(r["answers"], supporting)


def hotpot_supporting_sentence_indices(r):
    """Group HotpotQA's title-based sentence annotations by gold passage."""
    positions = {}
    for answer_i, (title, _) in enumerate(r["answers"]):
        assert title not in positions, f"{r['id']}: duplicate gold title {title!r}"
        positions[title] = answer_i
    out = [[] for _ in r["answers"]]
    for title, sentence_i in r["supporting_facts"]:
        assert title in positions, f"{r['id']}: supporting title not in answers: {title!r}"
        answer_i = positions[title]
        assert 0 <= sentence_i < len(r["answers"][answer_i][1]), \
            f"{r['id']}: supporting sentence index out of range"
        out[answer_i].append(sentence_i)
    return out


def norm_musique(r, i, n_hops, verified, code):
    record_id = f"musique_{n_hops}hop_{i}"
    r = replace_text(r, TEXT_REPLACEMENTS.get((code, record_id), {}))
    hop_seq = ([1, 0] if n_hops == 2 and i in MUSIQUE_2HOP_REVERSED
               else list(range(n_hops)))
    return {
        "id": record_id,
        "source": "musique",
        "type": r["type"],
        "n_hops": n_hops,
        "question": r["question"],
        "answer": r["answer"],
        "answers": pack_musique_answers(r),
        "non_answers": r["non_answers"],
        "hop_seq": hop_seq,
        "hop_seq_verified": verified,
        # MuSiQue carries no question decomposition. Written explicitly so the
        # schema is uniform across sources and Arrow/parquet inference is clean.
        "sub_q1": None,
        "sub_q2": None,
        "bridge_match": None,
        "chain_ok": None,
    }


def norm_hotpot(r, q1, q2, en_q1, supporting_indices, code):
    """r from {lang}_b.json (translated passages); q1/q2 from {lang}_{1,2}.json
    (questions only -- their passage pools are English and are discarded).

    Three repairs are applied to the raw decomposition:

    1. sub_q2 asks the same thing as the full 2-hop question, so its answer is
       the record's answer by construction (English: 176/176). Independent
       per-language translation broke that -- "Начальник Протокола" vs
       "Начальник протокола". The record's answer is canonical because it is
       what scoring compares against, so sub_q2's answer is set to it and the
       divergent translation kept as `answer_raw` for audit.

    2. Independently translated bridge names that became inconsistent between
       sub_q1 and sub_q2 are replaced with reviewed, grammatical translations.

    3. The resulting bridge entity is classified -- see bridge_match().
    """
    record_id = f"hotpotqa_{r['id']}"
    r = replace_text(r, TEXT_REPLACEMENTS.get((code, record_id), {}))
    r.update(RECORD_OVERRIDES.get((code, r["id"]), {}))
    override = DECOMPOSITION_OVERRIDES.get((code, r["id"]), {})
    q1_question = override.get("q1_question", clean_q(q1["question"]))
    q1_answer = override.get("q1_answer", clean_q(q1["answer"]))
    q2_question = override.get("q2_question", clean_q(q2["question"]))
    q2_answer_raw = q2["answer"] if q2["answer"] != r["answer"] else None
    match = bridge_match(q1_answer, q2_question, en_q1["answer"])
    if r["id"] in NON_EXPLICIT_BRIDGE_IDS:
        match = "absent"
    return {
        "id": record_id,
        "source": "hotpotqa",
        "type": r["type"],
        "n_hops": 2,
        "question": r["question"],
        "answer": r["answer"],
        # Sentence annotations come from the aligned English record. Translated
        # title strings are not reliable identifiers because the passage and
        # annotation titles were sometimes translated differently.
        "answers": pack_answers(r["answers"], supporting_indices),
        "non_answers": r["non_answers"],
        "hop_seq": r["hop_seq"],
        "hop_seq_verified": True,
        "sub_q1": {"question": q1_question,
                   "answer": q1_answer},
        "sub_q2": {"question": q2_question,
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
        recs = [norm_musique(r, i, n_hops, verified, code)
                for i, r in enumerate(raw)]
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
    en_supporting = {
        r["id"]: SUPPORTING_INDEX_OVERRIDES.get(
            r["id"], hotpot_supporting_sentence_indices(r))
        for r in en_b
    }
    ids_ref = None
    for lang, code in LANGS:
        b = load(hot_root / f"{lang}_b.json")
        s1 = {r["id"]: r for r in load(hot_root / f"{lang}_1.json")}
        s2 = {r["id"]: r for r in load(hot_root / f"{lang}_2.json")}
        recs = [norm_hotpot(r, s1[r["id"]], s2[r["id"]], en_s1[r["id"]],
                            en_supporting[r["id"]], code)
                for i, r in enumerate(b) if i not in drop]
        ids = [r["id"] for r in recs]
        if ids_ref is None:
            ids_ref = ids
        elif ids != ids_ref:
            raise SystemExit(f"{name}/{lang}: id sequence diverges from English")
        for r in recs:
            assert len(r["answers"]) == 2, f"{r['id']}: {len(r['answers'])} answers"
            assert sorted(r["hop_seq"]) == [0, 1], f"{r['id']}: bad hop_seq"
            assert all(all(0 <= sentence_i < len(answer["sentences"])
                           for sentence_i in answer["supporting_sentence_indices"])
                       for answer in r["answers"]), \
                f"{r['id']}: supporting sentence index out of range"
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
