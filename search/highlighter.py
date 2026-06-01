import re


def highlight_text(text, query_terms, context_chars=100):
    if not text or not query_terms:
        return ""

    terms = [t.lower() for t in query_terms if len(t) > 2]
    if not terms:
        return text[:context_chars * 2] + "..."

    pattern = re.compile("|".join(re.escape(t) for t in terms), re.IGNORECASE)
    matches = list(pattern.finditer(text))

    if not matches:
        return text[:context_chars * 2] + "..." if len(text) > context_chars * 2 else text

    snippets = []
    seen_ranges = set()

    for match in matches:
        start = max(0, match.start() - context_chars // 2)
        end = min(len(text), match.end() + context_chars // 2)

        covered = False
        for s, e in seen_ranges:
            if start >= s and end <= e:
                covered = True
                break
            if start < s and end > s:
                start = min(start, s)
                end = max(end, e)
                seen_ranges.remove((s, e))
                seen_ranges.add((start, end))
                covered = True
                break

        if not covered:
            seen_ranges.add((start, end))

    for start, end in sorted(seen_ranges):
        snippet = text[start:end]
        highlighted = pattern.sub(lambda m: f"[{m.group(0)}]", snippet)
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
        snippets.append(highlighted)

    return "\n".join(snippets)
