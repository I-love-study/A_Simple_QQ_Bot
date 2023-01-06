from pathlib import Path
import ujson as json

cases = {}

class Group_save:

    def __init__(self, file: Path):
        self.file = file
        self.file.touch()
        b = self.file.read_text(encoding='UTF-8')
        self.data = {} if b == '' else json.loads(b)

    @classmethod
    def get(cls, filepath):
        file = filepath if type(filepath) is Path else Path(filepath)
        if file in cases:
            return cases[file]
        else:
            cases[file] = cls(file)
            return cases[file]

    def commit(self):
        self.file.write_text(
            json.dumps(self.data,
                ensure_ascii=False,
                indent=2),
            encoding='UTF-8')

    def get_item(self, *args, create=None):
        cache = self.data
        if create is None: create={}
        for a in args[:-1]:
            s = str(a)
            cache.setdefault(s, {})
            cache = cache[s]
        last = str(args[-1])
        cache.setdefault(last, create)
        return cache[last]