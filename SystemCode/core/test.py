
encodings = [
    "ASCII",
    "UTF-8",
    "UTF-16",
    "UTF-32",
    "ISO-8859-1",  # Latin-1
    "ISO-8859-2",  # Latin-2
    "ISO-8859-3",  # Latin-3
    "ISO-8859-4",  # Latin-4
    "ISO-8859-5",  # Cyrillic
    "ISO-8859-6",  # Arabic
    "ISO-8859-7",  # Greek
    "ISO-8859-8",  # Hebrew
    "ISO-8859-9",  # Latin-5
    "ISO-8859-10",  # Latin-6
    "ISO-8859-11",  # Thai
    "ISO-8859-13",  # Latin-7
    "ISO-8859-14",  # Latin-8
    "ISO-8859-15",  # Latin-9
    "ISO-8859-16",  # Latin-10
    "Windows-1250",
    "Windows-1251",
    "Windows-1252",
    "Windows-1253",
    "Windows-1254",
    "Windows-1255",
    "Windows-1256",
    "Windows-1257",
    "Windows-1258",
    "MacRoman",
    "MacCentralEurope",
    "MacIceland",
    "MacCroatian",
    "MacRomania",
    "MacCyrillic",
    "MacUkraine",
    "MacGreek",
    "MacTurkish",
    "MacHebrew",
    "MacArabic",
    "MacThai",
    "MacJapanese",
    "MacChineseSimp",  # GB 2312
    "MacChineseTrad",  # Big5
    "MacKorean",
    "MacVietnamese",
    "KOI8-R",  # Russian
    "KOI8-U",  # Ukrainian
    "Big5",  # Traditional Chinese
    "GB2312",  # Simplified Chinese
    "GB18030",  # Simplified Chinese
    "HZ",  # Simplified Chinese
    "EUC-JP",  # Japanese
    "SHIFT_JIS",  # Japanese
    "ISO-2022-JP",  # Japanese
    "EUC-KR",  # Korean
    "ISO-2022-KR",  # Korean
    "TIS-620"  # Thai
]

for encode in encodings:
    try:
        with open('q.txt', 'r', encoding='GB18030') as f:
            content = f.read()

        with open('q.txt', 'w', encoding='utf-8') as f:
            f.write(content)

        break

    except:
        print(f"Error: {encode}")