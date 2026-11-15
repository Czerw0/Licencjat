import re

import pandas as pd


def compile_terms(camp_terms):
    """Jeden wzorzec na parę (obóz, typ terminu): całe słowa, bez rozróżniania wielkości liter"""
    patterns = {}
    for camp, types in camp_terms.items():
        for term_type, terms in types.items():
            if terms:
                alternatives = "|".join(re.escape(term) for term in sorted(terms, key=len, reverse=True))
                patterns[(camp, term_type)] = re.compile(rf"\b(?:{alternatives})\b", re.IGNORECASE)
    return patterns


def find_mentions(texts, camp_terms):
    """Komentarze wspominające dokładnie jeden obóz: kolumny mentioned_camp, term (pierwszy w tekście), term_type"""
    patterns = compile_terms(camp_terms)
    rows = []
    for index, text in texts.items():
        found = []
        for (camp, term_type), pattern in patterns.items():
            match = pattern.search(text)
            if match:
                found.append((match.start(), camp, match.group(0).lower(), term_type))
        if len({camp for _, camp, _, _ in found}) == 1:
            _, camp, term, term_type = min(found)
            rows.append((index, camp, term, term_type))
    return pd.DataFrame(rows, columns=["index", "mentioned_camp", "term", "term_type"]).set_index("index")


def mask_terms(texts, camp_terms, token="[MASK]"):
    """Zamienia wszystkie terminy obozów na token"""
    all_terms = [term for types in camp_terms.values() for terms in types.values() for term in terms]
    alternatives = "|".join(re.escape(term) for term in sorted(all_terms, key=len, reverse=True))
    return texts.str.replace(rf"\b(?:{alternatives})\b", token, regex=True, flags=re.IGNORECASE)
