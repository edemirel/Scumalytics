class Player():
    def __init__(self, name=None, page_url=None, firstyear=None, lastyear=None, pos=None,
                 height=None, weight=None, shoots=None, birthday=None, birthcity=None, birthcountry=None,
                 college=None, img_url=None, draftteam=None, draftcity=None, draftround=None,
                 draftpos=None, draftroundpick=None):
        self.name = name
        self.page_url = page_url
        self.img_url = img_url
        self.firstyear = firstyear
        self.lastyear = lastyear
        self.height = height
        self.weight = weight
        self.birthday = birthday
        self.birthcity = birthcity
        self.birthcountry = birthcountry
        self.college = college
        self.shoots = shoots
        self.draftteam = draftteam
        self.draftcity = draftcity
        self.draftround = draftround
        self.draftpos = draftpos
        self.draftrounpick = draftroundpick
        self.pos = pos
        self.seasons = []
        self.games = []
