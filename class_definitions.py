class Player():
    def __init__(self, name=None, page_url=None, firstyear=None, lastyear=None, pos=None,
                 height=None, weight=None, shoots=None, birthday=None, college=None, img_url=None):
        self.name = name
        self.page_url = page_url
        self.img_url = img_url
        self.firstyear = firstyear
        self.lastyear = lastyear
        self.height = height
        self.weight = weight
        self.birthday = birthday
        self.college = college
        self.shoots = shoots
        self.pos = pos
        self.seasons = []
        self.games = []
