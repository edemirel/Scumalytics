class Player():
    def __init__(self, name=None, url=None, firstyear=None, lastyear=None, pos=None,
                 height=None, weight=None, birthday=None, college=None):
        self.name = name
        self.url = url
        self.firstyear = firstyear
        self.lastyear = lastyear
        self.height = height
        self.weight = weight
        self.birthday = birthday
        self.college = college
        self.pos = pos
        self.seasons = []
        self.games = []
