"""Build a starter VariMitra intent dataset (mr / hi / en).

Examples are templates. They must not teach the model facility or Wari facts.
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).with_name("intents.jsonl")

# language, style, utterance, action object
ROWS: list[tuple[str, str, str, dict]] = []


def add(language: str, style: str, utterance: str, action: str, parameters: dict) -> None:
    ROWS.append((language, style, utterance, {"action": action, "parameters": parameters}))


CATEGORIES = {
    "WATER": {
        "en": ["water", "drinking water"],
        "hi": ["पानी", "पीने का पानी"],
        "mr": ["पाणी", "पिण्याचे पाणी"],
    },
    "FOOD": {
        "en": ["food", "a meal"],
        "hi": ["खाना", "भोजन"],
        "mr": ["जेवण", "खाणे"],
    },
    "MEDICAL": {
        "en": ["medical help", "a doctor"],
        "hi": ["डॉक्टर", "मेडिकल मदद"],
        "mr": ["वैद्यकीय मदत", "डॉक्टर"],
    },
    "TOILET": {
        "en": ["a toilet", "a washroom"],
        "hi": ["शौचालय", "टॉयलेट"],
        "mr": ["स्वच्छतागृह", "टॉयलेट"],
    },
    "ACCOMMODATION": {
        "en": ["a place to stay", "accommodation"],
        "hi": ["रुकने की जगह", "आवास"],
        "mr": ["राहण्याची जागा", "निवास"],
    },
    "TRANSPORT": {
        "en": ["transport", "a bus"],
        "hi": ["यातायात", "बस"],
        "mr": ["वाहतूक", "बस"],
    },
    "WOMEN": {
        "en": ["women help", "a women help point"],
        "hi": ["महिला सहायता", "महिला हेल्प पॉइंट"],
        "mr": ["महिला मदत", "महिला हेल्प पॉइंट"],
    },
}

OPEN_PHRASES = {
    "en": {"direct": "Open {label}", "indirect": "I want to see {label}", "short": "{label}", "noisy": "uh open {label} please"},
    "hi": {"direct": "{label} खोलो", "indirect": "मुझे {label} दिखाइए", "short": "{label}", "noisy": "अरे {label} खोलो"},
    "mr": {"direct": "{label} उघडा", "indirect": "मला {label} दाखवा", "short": "{label}", "noisy": "ए {label} उघडा"},
}

NEAREST_PHRASES = {
    "en": {"direct": "Find nearest {label}", "indirect": "Where is the closest {label}?", "short": "nearest {label}", "noisy": "find uh nearest {label}"},
    "hi": {"direct": "सबसे नजदीक {label} ढूंढो", "indirect": "सबसे पास {label} कहाँ है?", "short": "नजदीक {label}", "noisy": "पास वाला {label} बताओ"},
    "mr": {"direct": "सर्वात जवळचे {label} शोधा", "indirect": "सर्वात जवळ {label} कुठे आहे?", "short": "जवळचे {label}", "noisy": "जवळचं {label} सांगा"},
}

for category, labels in CATEGORIES.items():
    for lang, phrases in OPEN_PHRASES.items():
        label = labels[lang][0]
        for style, template in phrases.items():
            add(lang, style, template.format(label=label), "OPEN_SECTION", {"category": category})
    for lang, phrases in NEAREST_PHRASES.items():
        label = labels[lang][0]
        for style, template in phrases.items():
            add(lang, style, template.format(label=label), "FIND_NEAREST", {"category": category})

NAV = [
    ("en", "direct", "Go back", "GO_BACK", {}),
    ("en", "short", "back", "GO_BACK", {}),
    ("en", "noisy", "uh go back", "GO_BACK", {}),
    ("hi", "direct", "पीछे जाओ", "GO_BACK", {}),
    ("hi", "short", "वापस", "GO_BACK", {}),
    ("mr", "direct", "मागे जा", "GO_BACK", {}),
    ("mr", "short", "परत", "GO_BACK", {}),
    ("en", "direct", "Close this section", "CLOSE_SECTION", {}),
    ("en", "short", "close", "CLOSE_SECTION", {}),
    ("hi", "direct", "यह सेक्शन बंद करो", "CLOSE_SECTION", {}),
    ("mr", "direct", "हा भाग बंद करा", "CLOSE_SECTION", {}),
    ("en", "direct", "Stop", "STOP", {}),
    ("en", "short", "stop listening", "STOP", {}),
    ("hi", "direct", "रुको", "STOP", {}),
    ("mr", "direct", "थांबा", "STOP", {}),
]
for row in NAV:
    add(*row)

ROUTE = [
    ("en", "direct", "Show route to the selected place", "SHOW_ROUTE", {"destination": "selected"}),
    ("en", "indirect", "How do I walk there?", "SHOW_ROUTE", {"destination": "selected"}),
    ("hi", "direct", "वहाँ का रास्ता दिखाओ", "SHOW_ROUTE", {"destination": "selected"}),
    ("mr", "direct", "तिथला मार्ग दाखवा", "SHOW_ROUTE", {"destination": "selected"}),
    ("en", "direct", "How far is the selected place?", "GET_DISTANCE", {"location": "selected"}),
    ("hi", "direct", "कितनी दूर है?", "GET_DISTANCE", {"location": "selected"}),
    ("mr", "direct", "किती दूर आहे?", "GET_DISTANCE", {"location": "selected"}),
    ("en", "direct", "Select the first result", "SELECT_LOCATION", {"location_id": "result_1"}),
    ("en", "followup", "the nearest one", "SELECT_LOCATION", {"location_id": "nearest"}),
    ("hi", "followup", "सबसे पास वाला", "SELECT_LOCATION", {"location_id": "nearest"}),
    ("mr", "followup", "सर्वात जवळचे", "SELECT_LOCATION", {"location_id": "nearest"}),
]
for row in ROUTE:
    add(*row)

INFO = [
    ("en", "direct", "Read the SOS help", "READ_INFORMATION", {"info_key": "how_to_sos"}),
    ("en", "indirect", "How does the voice button work?", "READ_INFORMATION", {"info_key": "how_to_voice"}),
    ("hi", "direct", "SOS की जानकारी पढ़ो", "READ_INFORMATION", {"info_key": "how_to_sos"}),
    ("mr", "direct", "आवाज कसा वापरायचा ते सांगा", "READ_INFORMATION", {"info_key": "how_to_voice"}),
]
for row in INFO:
    add(*row)

GENERAL = [
    ("en", "direct", "What is Wari?", "GENERAL_QUESTION", {"text": "What is Wari?"}),
    ("en", "noisy", "um what is this app for", "GENERAL_QUESTION", {"text": "what is this app for"}),
    ("hi", "direct", "वारी क्या है?", "GENERAL_QUESTION", {"text": "वारी क्या है?"}),
    ("mr", "direct", "वारी म्हणजे काय?", "GENERAL_QUESTION", {"text": "वारी म्हणजे काय?"}),
]
for row in GENERAL:
    add(*row)

WARI = [
    ("en", "direct", "Where will the Wari be on 2026-06-15?", "GET_WARI_STATUS", {"date": "2026-06-15"}),
    ("en", "indirect", "On 15 June 2026 at 5 pm where is the Wari scheduled?", "GET_WARI_STATUS", {"date": "2026-06-15", "time": "17:00"}),
    ("en", "direct", "Where is Dnyaneshwar palkhi scheduled on 2026-06-16?", "GET_WARI_STATUS", {"date": "2026-06-16", "palkhi": "dnyaneshwar"}),
    ("hi", "direct", "15 जून 2026 को वारी कहाँ होगी?", "GET_WARI_STATUS", {"date": "2026-06-15"}),
    ("hi", "indirect", "आज वारी का मुकाम कहाँ निर्धारित है, तारीख 2026-06-15", "GET_WARI_STATUS", {"date": "2026-06-15"}),
    ("mr", "direct", "2026-06-15 रोजी वारी कुठे असेल?", "GET_WARI_STATUS", {"date": "2026-06-15"}),
    ("mr", "indirect", "उद्या पालखी कुठून निघणार आहे 2026-06-16", "GET_WARI_STATUS", {"date": "2026-06-16"}),
    ("mr", "noisy", "संध्याकाळी ५ वाजता 2026-06-15 वारी कुठे", "GET_WARI_STATUS", {"date": "2026-06-15", "time": "17:00"}),
]
for row in WARI:
    add(*row)

LOST = [
    ("en", "direct", "Report a lost person wearing a red shirt", "LOST_PERSON_REPORT", {"description": "red shirt"}),
    ("en", "indirect", "Someone is missing near the halt", "LOST_PERSON_REPORT", {"description": "missing person", "location": "halt"}),
    ("hi", "direct", "लाल कमीज वाला व्यक्ति गुम है", "LOST_PERSON_REPORT", {"description": "लाल कमीज"}),
    ("mr", "direct", "हरवलेल्या व्यक्तीचा अहवाल नोंदवा, निळी साडी", "LOST_PERSON_REPORT", {"description": "निळी साडी"}),
]
for row in LOST:
    add(*row)

FAMILY = [
    ("en", "direct", "What is my family link status?", "FAMILY_STATUS", {}),
    ("en", "followup", "did my family get the report", "FAMILY_STATUS", {}),
    ("hi", "direct", "परिवार लिंक की स्थिति बताओ", "FAMILY_STATUS", {}),
    ("mr", "direct", "कुटुंब जोडणीची स्थिती सांगा", "FAMILY_STATUS", {}),
]
for row in FAMILY:
    add(*row)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as handle:
        for index, (language, style, utterance, action) in enumerate(ROWS, start=1):
            record = {
                "id": f"vm-{index:04d}",
                "language": language,
                "style": style,
                "utterance": utterance,
                "action": action,
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"wrote {len(ROWS)} rows to {OUT}")


if __name__ == "__main__":
    main()
