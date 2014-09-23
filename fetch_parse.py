# [SublimeLinter flake8-max-line-length:135]
from bs4 import BeautifulSoup
import multiprocessing
import urllib2
import re
import copy
import time

from definitions import Player

BR_ROOT = 'http://www.basketball-reference.com'
BR_PLAYERS = 'http://www.basketball-reference.com/players'
BR_SEASONS = 'http://www.basketball-reference.com/players/{0}/{1}/gamelog/{2}'

parser = 'html.parser'

start_year = 1982

epoch_time = time.time
glob_plist = []
glob_player = []
glob_player_season = []


def pos_to_num(poslist):
    num_pos = []
    for pos in poslist:
        if pos == "Center":
            num_pos.append(5)
        elif pos == "Power Forward":
            num_pos.append(4)
        elif pos == "Small Forward":
            num_pos.append(3)
        elif pos == "Shooting Guard":
            num_pos.append(2)
        elif pos == "Point Guard":
            num_pos.append(1)
        else:
            pass
            # Never should hit here honestly

    return num_pos


def num_to_pos(poslist):
    pos_num = []
    for pos in poslist:
        if pos == 5:
            pos_num.append("Center")
        elif pos == 4:
            pos_num.append("Power Forward")
        elif pos == 3:
            pos_num.append("Small Forward")
        elif pos == 2:
            pos_num.append("Shooting Guard")
        elif pos == 1:
            pos_num.append("Point Guard")
        else:
            pass
            # Never should hit here honestly

    return pos_num


def fetch_parse(datatype, playerlist_lastname=None, player=None, season=None):
    """ fetch_parse calls fetch and parse functions consecutively
        datatype can be one of three; playerlist, player, player_season

        * playerlist gets a list of players w/ given first letter of surname
        * player gets the basic player info and season data
        * player season gets all the games played for the player in a given season

        example playerlist page http://www.basketball-reference.com/players/a/
            Uses playerlist_lastname argument

        example player page http://www.basketball-reference.com/players/a/abdelal01.html
            Uses player argument
            Can be passed in three styles
            * /players/a/abdelal01.html
            * abdelal01.html
            * abdelal01

        example player_season page http://www.basketball-reference.com/players/a/abdelal01/gamelog/1991/
            Uses player and season arguments
    """
    defined_datatypes = ['playerlist', 'player', 'player_season']

    # Checking if the fetchtype passed is proper
    if datatype not in defined_datatypes:
        raise Exception('The type you have used is not defined\n Please use playerlist, player or player_season')

    fetch_result = fetch(datatype, playerlist_lastname=playerlist_lastname, player=player, season=season)
    r_arg = parse(datatype, soup=fetch_result[0], url=fetch_result[1])

    return r_arg


def fetch(fetchtype, playerlist_lastname=None, player=None, season=None):
    """ fetch gets the page and readies the soup for data in the specified level
        fetchtype can be one of three, playerlist, player, player_season

        Check fetch_parse function for more details
    """

    defined_fetchtypes = ['playerlist', 'player', 'player_season']

    if fetchtype == defined_fetchtypes[0]:
        return fetch_playerlist(playerlist_lastname=playerlist_lastname)

    elif fetchtype == defined_fetchtypes[1]:
        return fetch_player(player=player)

    elif fetchtype == defined_fetchtypes[2]:
        return fetch_player_season(player=player, season=season)

    else:
        raise Exception('The type you have used is not defined\n Please use playerlist, player or player_season')

        # should never hit here normally


def fetch_playerlist(playerlist_lastname):

    # Fetch Part
    fetch_url = "/".join([BR_PLAYERS, playerlist_lastname, ""])

    soup = BeautifulSoup(urllib2.urlopen(fetch_url).read(), parser)

    return soup, fetch_url


def fetch_player(player):
    # Checking if direct url or playercode is passed
    # Case /players/a/abdelal01.html
    if len(player.split("/")) == 4:
        fetch_url = "".join([BR_ROOT, player, ""])

    # Case abdelal01.html
    elif len(player.split(".")) == 2:
        fetch_url = "/".join([BR_PLAYERS, player[0], player])

    # Case http://www.basketball-reference.com/players/a/abdulta01.html
    elif len(player.split("/")) == 6:
        fetch_url = player

    # Case abdelal01
    else:
        fetch_url = "/".join([BR_PLAYERS, player[0], ".".join([player, "html"])])

    soup = BeautifulSoup(urllib2.urlopen(fetch_url).read(), parser)

    return soup, fetch_url


def fetch_player_season(player, season):

    # Checking if direct url or playercode is passed
    # Case /players/a/abdelal01.html
    if len(player.split("/")) == 4:
        player_tag = player.split("/")[3].split(".")[0]

    # Case abdelal01.html
    elif len(player.split(".")) == 2:
        player_tag = player.split(".")[0]

    # Case http://www.basketball-reference.com/players/a/abdulta01.html
    elif len(player.split("/")) == 6:
        player_tag = player.split("/")[5].split(".")[0]

    # Case abdelal01
    else:
        player_tag = player

    fetch_url = BR_SEASONS.format(player_tag[0], player_tag, season)

    soup = BeautifulSoup(urllib2.urlopen(fetch_url).read(), parser)

    return soup, fetch_url


def parse(datatype, soup, url=None):
    """ parse gets the soup and returns data in the specified level
        fetchtype can be one of three, playerlist, player, player_season

        Check fetch_parse function for more details
    """
    defined_datatypes = ['playerlist', 'player', 'player_season']

    if datatype == defined_datatypes[0]:
        return parse_playerlist(soup)

    elif datatype == defined_datatypes[1]:
        return parse_player(soup, url)

    elif datatype == defined_datatypes[2]:
        return parse_player_season(soup, url)

    else:
        raise Exception('The type you have used is not defined\n Please use playerlist, player or player_season')


def parse_playerlist(soup, yearfrom=start_year):
    """ Returns a playerlist as URLs from a given playerlist soup"""
    # Search for all "a" tags, get href attributes
    table_container = soup.find("table", id="players").find("tbody")

    # num_of_columns = len(table_container.find("tr").find_all("td"))
    playerlist = []

    for row in table_container.find_all("tr"):
        t = row.find_all("td")
        if int(t[1].text) >= yearfrom:
            playerlist.append(t[0].a["href"].encode("utf8"))

    return playerlist


def parse_player(soup, url=None):

    # INIT DATAPOINTS AS BLANK, THIS IS TO PREVENT ERRORS IF THE PARSE DOESNT HAPPEN
    tempplayer = {'name': None, 'img_url': None, 'pos': None, 'shoots': None,
                  'height': None, 'weight': None, 'birthday': None, 'birthcity': None,
                  'birthcountry': None, 'college': None, 'draftcity': None,
                  'draftteam': None, 'draftround': None, 'draftroundpick': None,
                  'draftpos': None, 'page_url': url, 'seasons': []}

    infobox = soup.find("div", id="info_box")

    draftregex = re.compile(r", (\d).+?(\d{1,3}).+?(\d{1,3}).+")

    # DataPoint
    img_link = infobox.find("div", attrs={'class': "person_image"})
    if img_link is not None:
        tempplayer['img_url'] = infobox.find("div", attrs={'class': "person_image"}).find("img")["src"]

    playerdata = infobox.find("div", attrs={'class': "person_image_offset"})
    if playerdata is None:
        playerdata = infobox

    # DataPoint
    tempplayer['name'] = playerdata.h1.text.encode("utf8")

    for p in playerdata.find_all("span"):
        if p.text == "Position:":
            temp_text = repr(p.next_sibling)
            begin = temp_text.find(" ")+1
            end = temp_text.find("\\")

            # DataPoint
            tempplayer['pos'] = pos_to_num(temp_text[begin:end].split(" and "))

        elif p.text == "Shoots:":
            temp_text = repr(p.next_sibling)
            begin = temp_text.find(" ")+1
            end = temp_text.rfind("\\")

            # DataPoint
            tempplayer['shoots'] = temp_text[begin:end]

        elif p.text == "Height:":
            temp_text = repr(p.next_sibling)
            begin = temp_text.find(" ")+1
            end = temp_text.find("\\")

            # DataPoint
            tempplayer['height'] = int(temp_text[begin:end].split("-")[0]) * 12 + int(
                temp_text[begin:end].split("-")[0])

        elif p.text == "Weight:":
            temp_text = repr(p.next_sibling)
            begin = temp_text.find(" ")+1
            end = temp_text.find(" lbs")

            # DataPoint
            tempplayer['weight'] = int(temp_text[begin:end])

        elif p.has_attr("id"):
            if p['id'] == "necro-birth":
                # DataPoint
                tempplayer['birthday'] = p['data-birth'].encode("utf8")

                temp_text = repr(p.next_sibling)
                temp_text = temp_text.lstrip("u\' in ")
                end = temp_text.find(",")

                try:
                    tempplayer['birthcity'] = temp_text[:end].encode("utf8")
                    tempplayer['birthcountry'] = p.next_sibling.next_sibling.text.encode("utf8")
                except AttributeError:
                    tempplayer['birthcity'] = "Unknown"
                    tempplayer['birthcountry'] = "Unknown"

        elif p.text == "College:":
            # DataPoint
            tempplayer['college'] = p.next_sibling.next_sibling.text.encode("utf8")

        elif p.text == "Draft:":
            draftinfo = p.next_sibling.next_sibling
            # DataPoint
            tempplayer['draftcity'] = draftinfo["href"].split("/")[2].encode("utf8")
            tempplayer['draftteam'] = draftinfo.text.encode("utf8")

            hit = re.match(draftregex, draftinfo.next_sibling)

            # DataPoint
            tempplayer['draftround'] = int(hit.group(1))
            tempplayer['draftroundpick'] = int(hit.group(2))
            tempplayer['draftpos'] = int(hit.group(3))
            break

        else:
            pass

    # Seasonal Data
    seasontable = soup.find("table", id="totals").find("tbody")
    seasonlist = []
    for row in seasontable.find_all("tr"):
        t = row.find_all("td")
        if len(t) <= 3:
            pass
        else:
            seasonlist.append(t[0].a["href"].split("/")[5].encode("utf8"))

    tempplayer['seasons'] = seasonlist

    tmp = Player(**tempplayer)

    return tmp


def int_transform_except_none(value):
    try:
        r = int(value)
    except ValueError:
        r = None
    return r


def parse_player_season(soup, url=None):
    player_season_list = []
    temp_game_org = {'game_num': None, 'player_game_num': None, 'game_date': None, 'age_year': None,
                     'team': None, 'is_away': None, 'opponent': None, 'started': None, 'is_playoff': None,
                     'age_days': None,  'is_win': None, 'point_differential': None,
                     'minutes_played': None, 'field_goals_made': None, 'field_goals_att': None, 'three_made': None,
                     'three_att': None, 'free_throw_made': None, 'free_throw_att': None, 'offensive_rebound': None,
                     'defensive_rebound': None, 'total_rebound': None, 'assist': None, 'steal': None,
                     'block': None, 'turnover': None, 'personal_fouls': None, 'points': None}

    season_gametable = soup.find("table", id="pgl_basic").find("tbody")
    temp_game_org['is_playoff'] = 0

    for row in season_gametable.find_all("tr"):
        temp_game = copy.deepcopy(temp_game_org)
        # Check if it's a replicate of the header row or DNP/Inactive Row
        # DNP Rows has 9

        min_active_game_rows = 10
        all_columns_in_row = row.find_all("td")
        if not len(all_columns_in_row) > min_active_game_rows:
            pass

        else:
            for i, col in enumerate(all_columns_in_row):

                if i == 0:
                    temp_game['game_num'] = int_transform_except_none(col.text)

                elif i == 1:
                    temp_game['player_game_num'] = int_transform_except_none(col.text)
                elif i == 2:
                    temp_game['game_date'] = col.text.encode("utf8")
                elif i == 3:
                    temp_game['age_year'] = int_transform_except_none(col.text.split("-")[0])
                    temp_game['age_days'] = int_transform_except_none(col.text.split("-")[1])
                elif i == 4:
                    temp_game['team'] = col.text.encode("utf8")
                elif i == 5:
                    if col.text == "@":
                        temp_game['is_away'] = 1
                    else:
                        temp_game['is_away'] = 0
                elif i == 6:
                    temp_game['opponent'] = col.text.encode("utf8")
                elif i == 7:
                    temp_text = col.text
                    if temp_text.split(" ")[0] == "W":
                        temp_game['is_win'] = 1
                    else:
                        temp_game['is_win'] = 0
                    temp_game['point_differential'] = int_transform_except_none(temp_text.split(" ")[1].split("(")[1].split(")")[0])
                elif i == 8:
                    temp_game['started'] = int_transform_except_none(col.text)
                elif i == 9:
                    temp_game['minutes_played'] = col.text.encode("utf8")
                elif i == 10:
                    temp_game['field_goals_made'] = int_transform_except_none(col.text)
                elif i == 11:
                    temp_game['field_goals_att'] = int_transform_except_none(col.text)
                elif i == 13:
                    temp_game['three_made'] = int_transform_except_none(col.text)
                elif i == 14:
                    temp_game['three_att'] = int_transform_except_none(col.text)
                elif i == 16:
                    temp_game['free_throw_made'] = int_transform_except_none(col.text)
                elif i == 17:
                    temp_game['free_throw_att'] = int_transform_except_none(col.text)
                elif i == 19:
                    temp_game['offensive_rebound'] = int_transform_except_none(col.text)
                elif i == 20:
                    temp_game['defensive_rebound'] = int_transform_except_none(col.text)
                elif i == 21:
                    temp_game['total_rebound'] = int_transform_except_none(col.text)
                elif i == 22:
                    temp_game['assist'] = int_transform_except_none(col.text)
                elif i == 23:
                    temp_game['steal'] = int_transform_except_none(col.text)
                elif i == 24:
                    temp_game['block'] = int_transform_except_none(col.text)
                elif i == 25:
                    temp_game['turnover'] = int_transform_except_none(col.text)
                elif i == 26:
                    temp_game['personal_fouls'] = int_transform_except_none(col.text)
                elif i == 27:
                    temp_game['points'] = int_transform_except_none(col.text)

                player_season_list.append(temp_game)

    return player_season_list


def all_main():
    asciilist = range(98, 120)
    for i in range(121, 123):
        asciilist.append(i)

    ln_list = []
    for i in asciilist:
        ln_list.append(str(unichr(i)))

    start_time = epoch_time()

    for ln in ln_list:
        this_player_list = fetch_parse(datatype="playerlist", playerlist_lastname=ln)
        print "Finished parsing Player List for Last Names staring with {0}".format(ln)

        for pl in this_player_list:
            this_player = fetch_parse(datatype="player", player=pl)
            print "Finished parsing Player {0}".format(this_player.name)
            for season in this_player.seasons:
                fetch_parse(datatype="player_season", player=this_player.page_url, season=season)
                end_time = epoch_time()
                gen_text = "Finished Season {0} Player {1}. Running for {2:.2f} min"
                print gen_text.format(season, this_player.name, (end_time-start_time)/60)


def plist_job_creator(ln, start_time):
    this_player_list = fetch_parse(datatype="playerlist", playerlist_lastname=ln)
    end_time = epoch_time()
    print "Finished PList for {0}. Running for {2:.2f} min".format(ln, (end_time-start_time)/60)
    glob_plist.append(this_player_list)
    return this_player_list


def player_job_creator(pl, start_time):
    this_player = fetch_parse(datatype="player", player=pl)
    end_time = epoch_time()
    print "Finished parsing Player {0}. Running for {2:.2f} min".format(this_player.name, (end_time-start_time)/60)
    return this_player


def player_season_job_creator(player, start_time):
    gamelist = []
    for season in player.seasons:
        gamelist.append(fetch_parse(datatype="player_season", player=player.page_url, season=season))
    end_time = epoch_time()
    gen_text = "Finished Season {0} Player {1}. Running for {2:.2f} min"
    print gen_text.format(season, player.name, (end_time-start_time)/60)

    return gamelist


def mp_main():
    asciilist = range(97, 120)
    for i in range(121, 123):
        asciilist.append(i)

    ln_list = []
    start_time = epoch_time()

    for i in asciilist:
        ln_list.append(str(unichr(i)))

    print "starting mp"
    pool = multiprocessing.Pool()

    for i in ln_list:
        pool.apply_async(plist_job_creator, args=(i, start_time))

    print "ending mp"

    pool.close()
    pool.join()

    print glob_plist


def test_main():
    this_player = fetch_parse(datatype="player", player="bagarda01")
    print this_player.birthcountry

    # gen_text.format(season, this_player.name, (end_time-start_time)/60)


if __name__ == "__main__":
    mp_main()
