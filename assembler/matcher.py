class Matcher:
    def __init__(self):
        self.matchers = []

    def add(self, matcher):
        self.matchers.append(matcher)

    def match(self, expression):
        for matcher in self.matchers:
            if matcher.match(expression):
                return matcher
        return None
