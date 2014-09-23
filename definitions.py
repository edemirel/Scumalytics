# [SublimeLinter flake8-max-line-length:130]
class Player():

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
        self.seasons = kwargs.get('seasons', [])
        self.games = kwargs.get('games', None)


class Game():
    def __init__(self, **kwargs):
        self.game_num = kwargs.get('game_num', None)
        self.player_game_num = kwargs.get('player_game_num', None)
        self.game_date = kwargs.get('game_date', None)
        self.age_year = kwargs.get('age_year', None)
        self.team = kwargs.get('team', None)
        self.is_away = kwargs.get('is_away', None)
        self.opponent = kwargs.get('opponent', None)
        self.started = kwargs.get('started', None)
        self.is_playoff = kwargs.get('is_playoff', None)
        self.age_days = kwargs.get('age_days', None)
        self.is_win = kwargs.get('is_win', None)
        self.point_differential = kwargs.get('point_differential', None)
        self.minutes_played = kwargs.get('minutes_played', None)
        self.field_goals_made = kwargs.get('field_goals_made', None)
        self.field_goals_att = kwargs.get('field_goals_att', None)
        self.three_made = kwargs.get('three_made', None)
        self.three_att = kwargs.get('three_att', None)
        self.free_throw_made = kwargs.get('free_throw_made', None)
        self.free_throw_att = kwargs.get('free_throw_att', None)
        self.offensive_rebound = kwargs.get('offensive_rebound', None)
        self.defensive_rebound = kwargs.get('defensive_rebound', None)
        self.total_rebound = kwargs.get('total_rebound', None)
        self.assist = kwargs.get('assist', None)
        self.steal = kwargs.get('steal', None)
        self.block = kwargs.get('block', None)
        self.turnover = kwargs.get('turnover', None)
        self.personal_fouls = kwargs.get('personal_fouls', None)
        self.points = kwargs.get('points', None)

    def calc_field_goals_percent():
        pass

    def calc_three_percent():
        pass

    def calc_free_throw_percent():
        pass
