#!/usr/bin/env python3
"""
The Daily Commit — automated proofreader.

Scans Markdown files for common grammar and punctuation slips.
No third-party packages needed. Run from the repo root:

    python3 scripts/proofread.py              # check README.md + newsroom/
    python3 scripts/proofread.py path.md ...  # check specific files

Exit code 0 = clean, 1 = problems found (so CI turns red).
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# ---------- rules: (name, regex, message) ----------
# Each regex is applied per line. Anything inside code, tables, links, or
# HTML is skipped first (see `strip_noise`).
RULES = [
    ("double-space", r"\S  +\S", "double space between words"),
    ("space-before-punct", r"\s[,.;:!?](?!\S*\|)", "space before punctuation mark"),
    ("no-space-after-punct", r"[,;:!?][A-Za-z]", "missing space after punctuation"),
    ("no-space-after-period", r"[a-z]\.[A-Z][a-z]", "missing space after full stop"),
    ("double-punct", r"(?<![A-Z])(?<!\.)([,.;:!?])(?!\.\.)[,.;:!?]", "repeated punctuation mark"),
    ("lowercase-i", r"\bi\b(?!')", "the pronoun 'I' should be capitalised"),
    ("lowercase-sentence", r"[.!?]\s+[a-z]", "sentence should start with a capital letter"),
    ("repeated-word", r"\b(\w+)\s+\1\b", "repeated word"),
    ("a-vs-an", r"\ba\s+[aeiouAEIOU]\w|\ban\s+[b-df-hj-np-tv-zB-DF-HJ-NP-TV-Z]\w", "check 'a' vs 'an'"),
    ("unbalanced-quotes", r'^(?:[^"]*"[^"]*")*[^"]*"[^"]*$', "unbalanced quotation marks"),
    ("unbalanced-parens", None, "unbalanced parentheses"),  # handled specially
    ("trailing-space", r"[ \t]+$", "trailing whitespace"),
]

# Common misspellings (word -> suggestion).
MISSPELLINGS = {
    "teh": "the", "recieve": "receive", "recieved": "received", "seperate": "separate",
    "definately": "definitely", "occured": "occurred", "untill": "until", "wich": "which",
    "thier": "their", "beleive": "believe", "alot": "a lot", "goverment": "government",
    "tommorow": "tomorrow", "tommorrow": "tomorrow", "enviroment": "environment",
    "publically": "publicly", "accomodate": "accommodate", "acheive": "achieve",
    "adress": "address", "begining": "beginning", "calender": "calendar",
    "comittee": "committee", "commitee": "committee", "existance": "existence",
    "grammer": "grammar", "independant": "independent", "neccessary": "necessary",
    "occassion": "occasion", "posession": "possession", "succesful": "successful",
    "wierd": "weird", "writting": "writing", "dont": "don't", "doesnt": "doesn't",
    "didnt": "didn't", "cant": "can't", "wont": "won't", "isnt": "isn't", "im": "I'm",
    "youre": "you're", "theyre": "they're", "wasnt": "wasn't", "havent": "haven't",
}

# Confusable pairs that are wrong in a specific context.
CONFUSABLES = [
    (r"\byour\s+(?:welcome|going|not|the|a|an)\b", "'your' → did you mean 'you're'?"),
    (r"\bits\s+(?:a|an|the|not|very|been|going)\b", "'its' → did you mean 'it's'?"),
    (r"\bit's\s+(?:own|way|place|name|orbit)\b", "'it's' → did you mean 'its'?"),
    (r"\bthere\s+(?:own|car|house|team|work)\b", "'there' → did you mean 'their'?"),
    (r"\bshould\s+of\b|\bcould\s+of\b|\bwould\s+of\b", "'should of' → 'should have'"),
    (r"\bthen\b\s+(?:me|him|her|us|them)\b", "'then' → did you mean 'than'?"),
    (r"\bless\s+(?:people|things|items|cars|words)\b", "'less' → 'fewer' for countable nouns"),
]

CODE_FENCE = re.compile(r"^\s*(```|~~~)")


def strip_noise(line: str) -> str:
    """Remove pieces we should not proofread: inline code, links/URLs, HTML tags, badges."""
    line = re.sub(r"`[^`]*`", "CODE", line)             # inline code
    line = re.sub(r"<[^>]+>", "", line)                 # HTML tags
    line = re.sub(r"!\[[^\]]*\]\([^)]*\)", "IMG", line)  # images
    line = re.sub(r"\]\([^)]*\)", "]", line)            # link targets
    line = re.sub(r"https?://\S+", "URL", line)         # bare URLs
    line = re.sub(r"^\s*[-*+]\s+", "", line)            # list bullets
    line = re.sub(r"^\s*#+\s*", "", line)               # heading hashes
    line = re.sub(r"^\s*>\s*", "", line)                # blockquote marker
    line = line.replace("**", "").replace("*", "")      # emphasis markers
    return line


def is_table_or_rule(line: str) -> bool:
    s = line.strip()
    return s.startswith("|") or re.fullmatch(r"-{3,}|\*{3,}|_{3,}", s) is not None


def check_file(path: Path):
    problems = []
    in_fence = False
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if CODE_FENCE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence or is_table_or_rule(raw) or not raw.strip():
            continue

        # trailing whitespace is checked on the raw line
        if re.search(r"[ \t]+$", raw):
            problems.append((n, "trailing-space", "trailing whitespace", raw.rstrip()))

        line = strip_noise(raw)

        for name, pattern, msg in RULES:
            if name in ("trailing-space",):
                continue
            if name == "unbalanced-parens":
                if line.count("(") != line.count(")"):
                    problems.append((n, name, msg, raw.strip()))
                continue
            if name == "lowercase-sentence":
                # allow e.g. "a.m." / "p.m." / "vs." / "Dr." / "e.g."
                cleaned = re.sub(r"\b(?:a\.m|p\.m|vs|Dr|Mr|Mrs|Ms|St|e\.g|i\.e|No|Vol|[A-Z])\.", "", line)
                if re.search(pattern, cleaned):
                    problems.append((n, name, msg, raw.strip()))
                continue
            if name == "unbalanced-quotes":
                if line.count('"') % 2 == 1:
                    problems.append((n, name, msg, raw.strip()))
                continue
            if pattern and re.search(pattern, line):
                problems.append((n, name, msg, raw.strip()))

        for word in re.findall(r"[A-Za-z']+", line):
            fix = MISSPELLINGS.get(word.lower())
            if fix:
                problems.append((n, "spelling", f"'{word}' → '{fix}'", raw.strip()))

        for pattern, msg in CONFUSABLES:
            if re.search(pattern, line, re.IGNORECASE):
                problems.append((n, "confusable", msg, raw.strip()))

        # paragraph should end with terminal punctuation (skip headings, bylines, captions)
        s = line.strip()
        if (
            s and not raw.lstrip().startswith(("#", "*", "<", "|", "!", "[", "-"))
            and len(s.split()) > 6
            and not re.search(r"""[.!?:"')\]]$""", s)
        ):
            problems.append((n, "missing-end-punct", "paragraph does not end with punctuation", raw.strip()))

    return problems


def main(argv):
    if argv:
        files = [Path(a) for a in argv]
    else:
        files = [REPO / "README.md"] + sorted((REPO / "newsroom").glob("*.md"))

    total = 0
    for f in files:
        if not f.exists():
            print(f"!! {f} not found")
            total += 1
            continue
        probs = check_file(f)
        rel = f.relative_to(REPO) if f.is_relative_to(REPO) else f
        if not probs:
            print(f"✅ {rel}: clean")
            continue
        print(f"❌ {rel}: {len(probs)} issue(s)")
        for n, name, msg, text in probs:
            print(f"   line {n:>4} [{name}] {msg}")
            print(f"             › {text[:110]}{'…' if len(text) > 110 else ''}")
        total += len(probs)

    print()
    if total:
        print(f"🛑 {total} problem(s). Fix them, commit, and push again — the PR will re-check itself.")
        return 1
    print("🎉 Everything is fit to print.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
