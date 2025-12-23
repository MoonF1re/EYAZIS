FR_CHARS = set("éèêàçùôîâûëï")
DE_CHARS = set("äöüß")

def detect_alphabetic(text):
    fr_count = sum(c in FR_CHARS for c in text)
    de_count = sum(c in DE_CHARS for c in text)

    if fr_count > de_count:
        return "French"
    elif de_count > fr_count:
        return "German"
    else:
        return "Unknown"
