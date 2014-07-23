class Player():
    # def __init__(self, name=None, page_url=None, firstyear=None, lastyear=None, pos=None,
    #              height=None, weight=None, shoots=None, birthday=None, birthcity=None, birthcountry=None,
    #              college=None, img_url=None, draftteam=None, draftcity=None, draftround=None,
    #              draftpos=None, draftroundpick=None):
        # self.name = name
        # self.page_url = page_url
        # self.img_url = img_url
        # self.firstyear = firstyear
        # self.lastyear = lastyear
        # self.height = height
        # self.weight = weight
        # self.birthday = birthday
        # self.birthcity = birthcity
        # self.birthcountry = birthcountry
        # self.college = college
        # self.shoots = shoots
        # self.draftteam = draftteam
        # self.draftcity = draftcity
        # self.draftround = draftround
        # self.draftpos = draftpos
        # self.draftrounpick = draftroundpick
        # self.pos = pos
        # self.seasons = []
        # self.games = []

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', None)
        self.page_url = kwargs.get('page_url', None)
        self.img_url = kwargs.get('img_url', None)
        self.firstyear = kwargs.get('firstyear', None)
        self.lastyear = kwargs.get('lastyear', None)
        self.height = kwargs.get('height', None)
        self.weight = kwargs.get('weight', None)
        self.birthday = kwargs.get('birthday', None)
        self.birthcity = kwargs.get('birthcity', None)
        self.birthcountry = kwargs.get('birthcountry', None)
        self.college = kwargs.get('college', None)
        self.shoots = kwargs.get('shoots', None)
        self.draftteam = kwargs.get('draftteam', None)
        self.draftcity = kwargs.get('draftcity', None)
        self.draftround = kwargs.get('draftround', None)
        self.draftpos = kwargs.get('draftpos', None)
        self.draftrounpick = kwargs.get('draftroundpick', None)
        self.pos = kwargs.get('pos', None)
        self.season = kwargs.get('season', None)
        self.games = kwargs.get('games', None)


class Game():
    def __init__(self, age=None, team=None, opponent=None, started=None, isplayoff=None):
        pass
