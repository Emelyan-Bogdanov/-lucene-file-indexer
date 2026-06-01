from whoosh import spelling


class Suggester:
    def __init__(self, ix):
        self.ix = ix
        self.spellers = {}

    def _get_speller(self, fieldname):
        if fieldname not in self.spellers:
            sp = spelling.Speller(self.ix.storage, self.ix.indexname, fieldname=fieldname)
            self.spellers[fieldname] = sp
        return self.spellers[fieldname]

    def suggest(self, text, fieldname="content", limit=10):
        sp = self._get_speller(fieldname)
        return sp.suggest(text, limit=limit)

    def autocorrect(self, text, fieldname="content"):
        sp = self._get_speller(fieldname)
        words = text.split()
        corrected = []
        for w in words:
            suggestions = sp.suggest(w, limit=1)
            if suggestions:
                corrected.append(suggestions[0])
            else:
                corrected.append(w)
        return " ".join(corrected)
