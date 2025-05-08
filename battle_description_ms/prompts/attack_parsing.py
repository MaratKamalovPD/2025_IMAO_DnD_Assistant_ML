import json

def parse_action_json_prompt(json_data):
    escaped_json = json.dumps(json_data, ensure_ascii=False)

    prompt = f"""
    Parse the following text into a JSON structure using the rules below:

        1. Use English keys, but keep values in Russian.
        2. For damage, split it into four fields:
        - "dice": use the format "dX" (e.g., "d10").
        - "count": number of dice (e.g., 2 for "2к10").
        - "type": damage type (e.g., "колющий").
        - "bonus": bonus to damage (e.g., 4 for "+4").
        3. For multiattacks, include a "multiattack" field that lists the types of attacks and their counts.
        4. For saving throws, use "save_dc" (just the number) and "save_type" (e.g., "Телосложение").
        5. For attack types, use "melee" or "ranged".
        6. For reach or range, use "reach" or "range" respectively.
        7. For damage on a failed or successful save, use "on_fail" and "on_success".
        8. Ignore any descriptive text that does not contain numerical values or game mechanics (e.g., flavor text, behavior descriptions).
        9. Make conditions and effects atomic. For example, "схвачена (Сл высвобождения 19)" should be split into:
        - "condition": "схвачена",
        - "escape_dc": 19.
        10. Do not include fields like "description" or "restriction" unless they contain critical game mechanics.

        Example JSON structure for an attack:
        {{
        "name": "Укус",
        "type": "melee",
        "attack_bonus": "+7",
        "reach": "10 фт.",
        "target": "одна цель",
        "damage": {{
            "dice": "d10",
            "count": 2,
            "type": "колющий",
            "bonus": 4
        }},
        "additional_effects": [
            {{
            "damage": {{
                "dice": "d8",
                "count": 1,
                "type": "кислота",
                "bonus": 0
            }}
            }}
        ]
        }}

        Example JSON structure for a multiattack:
        {{
        "name": "Мультиатака",
        "attacks": [
            {{
            "type": "Укус",
            "count": 1
        }},
            {{
            "type": "Коготь",
            "count": 2
            }}
        ]
        }}

        Example JSON structure for a breath weapon:
        {{
        "name": "Кислотное дыхание",
        "type": "area",
        "shape": "30-футовая линия, шириной 5 футов",
        "save_dc": 14,
        "save_type": "Ловкость",
        "damage": {{
            "dice": "d8",
            "count": 11,
            "type": "кислота",
            "bonus": 0
        }},
        "on_fail": "полный урон",
        "on_success": "половина урона"
        }}


                Now, parse the following text into JSON:
                {escaped_json}
    """
    return prompt.strip()