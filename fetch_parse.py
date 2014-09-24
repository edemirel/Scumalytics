# [SublimeLinter flake8-max-line-length:135]
from bs4 import BeautifulSoup
from multiprocessing import Pool
from string import ascii_lowercase
import urllib2
import re
import copy
import time
import csv


BR_ROOT = 'http://www.basketball-reference.com'
BR_PLAYERS = 'http://www.basketball-reference.com/players'
BR_SEASONS = 'http://www.basketball-reference.com/players/{0}/{1}/gamelog/{2}'

parser = 'html.parser'

start_year = 1982

glob_plist = []
glob_player = []
glob_player_season = []

positions = {'Center': 5, 'Power Forward': 4, 'Small Forward': 3, 'Shooting Guard': 2, 'Point Guard': 1}
num_to_position = {v: k for k, v in positions.items()}


def pos_to_num(input_pos):
        return [positions[p] for p in input_pos]


def num_to_pos(input_pos):
        return [num_to_position[p] for p in input_pos]


def fetch_playerlist(playerlist_lastname):

    # Fetch Part
    fetch_url = "/".join([BR_PLAYERS, playerlist_lastname, ""])

    soup = BeautifulSoup(urllib2.urlopen(fetch_url).read(), parser)

    return soup, fetch_url


def fetch_player(player):
    # Checking if direct url or playercode is passed

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


def parse_playerlist(soup, yearfrom=start_year):
    """ Returns a playerlist as URLs from a given playerlist soup"""
    # Search for all "a" tags, get href attributes
    try:
        table_container = soup.find("table", id="players").find("tbody")
    except AttributeError:
        return None

    playerlist = []

    for row in table_container.find_all("tr"):
        t = row.find_all("td")
        if int(t[1].text) >= yearfrom:
            playerlist.append(t[0].a["href"].encode("utf8").split("/")[3].split(".")[0])

    return playerlist


def parse_player(soup, url):

    # INIT DATAPOINTS AS BLANK, THIS IS TO PREVENT ERRORS IF THE PARSE DOESNT HAPPEN
    tempplayer = {'page_url': url}

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

    return tempplayer


def parse_player_season(player, soup):
    player_season_list = []
    temp_game = {'player': player['name']}

    season_gametable = soup.find("table", id="pgl_basic").find("tbody")

    temp_game['is_playoff'] = 0

    for row in season_gametable.find_all("tr"):
        # Check if it's a replicate of the header row or DNP/Inactive Row
        # DNP Rows has 9

        min_active_game_rows = 10
        all_columns_in_row = row.find_all("td")
        if not len(all_columns_in_row) > min_active_game_rows:
            pass

        else:
            for i, col in enumerate(all_columns_in_row):

                if i == 0:
                    temp_game['game_num'] = maybe_int(col.text)

                elif i == 1:
                    temp_game['player_game_num'] = maybe_int(col.text)
                elif i == 2:
                    temp_game['game_date'] = col.text.encode("utf8")
                elif i == 3:
                    temp_game['age_year'] = maybe_int(col.text.split("-")[0])
                    temp_game['age_days'] = maybe_int(col.text.split("-")[1])
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
                    temp_game['point_differential'] = maybe_int(temp_text.split(" ")[1].split("(")[1].split(")")[0])
                elif i == 8:
                    temp_game['started'] = maybe_int(col.text)
                elif i == 9:
                    temp_game['minutes_played'] = col.text.encode("utf8")
                elif i == 10:
                    temp_game['field_goals_made'] = maybe_int(col.text)
                elif i == 11:
                    temp_game['field_goals_att'] = maybe_int(col.text)
                elif i == 13:
                    temp_game['three_made'] = maybe_int(col.text)
                elif i == 14:
                    temp_game['three_att'] = maybe_int(col.text)
                elif i == 16:
                    temp_game['free_throw_made'] = maybe_int(col.text)
                elif i == 17:
                    temp_game['free_throw_att'] = maybe_int(col.text)
                elif i == 19:
                    temp_game['offensive_rebound'] = maybe_int(col.text)
                elif i == 20:
                    temp_game['defensive_rebound'] = maybe_int(col.text)
                elif i == 21:
                    temp_game['total_rebound'] = maybe_int(col.text)
                elif i == 22:
                    temp_game['assist'] = maybe_int(col.text)
                elif i == 23:
                    temp_game['steal'] = maybe_int(col.text)
                elif i == 24:
                    temp_game['block'] = maybe_int(col.text)
                elif i == 25:
                    temp_game['turnover'] = maybe_int(col.text)
                elif i == 26:
                    temp_game['personal_fouls'] = maybe_int(col.text)
                elif i == 27:
                    temp_game['points'] = maybe_int(col.text)

            player_season_list.append(copy.deepcopy(temp_game))
            for key in temp_game.keys():
                if (key != 'player' and key != 'is_playoff'):
                    temp_game[key] = None

    return player_season_list


def maybe_int(value):
    try:
        r = int(value)
    except ValueError:
        r = None
    return r


def linear_main():
    start_time = time.time()
    last_names_list = ascii_lowercase

    for ln in last_names_list:
        this_player_list = parse_playerlist(fetch_playerlist(playerlist_lastname=ln)[0])
        print "Finished PList {0} Length {1}".format(ln, len(this_player_list))
        glob_plist.extend(this_player_list)

        for pl in glob_plist:
            fetch_result = fetch_player(player=pl)
            this_player = parse_player(soup=fetch_result[0], url=fetch_result[1])
            glob_player.append(this_player)
            print "Finished parsing Player {0}".format(this_player['name'])
            for season in this_player['seasons']:
                soup, fetched_url = fetch_player_season(this_player['page_url'], season)
                glob_player_season.extend(parse_player_season(player=this_player, soup=soup))
                end_time = time.time()
                gen_text = "Finished Season {0} Player {1}. Running for {2:.2f} min"
                print gen_text.format(season, this_player['name'], (end_time-start_time)/60)

    dump_games_to_csv(glob_player_season)

    print "RUN TIME {0:.2f}".format((time.time()-start_time)/60)


def plist_job_creator(ln):
    this_player_list = parse_playerlist(fetch_playerlist(playerlist_lastname=ln)[0])
    print "Finished PList {0} Length {1}".format(ln, len(this_player_list))
    return this_player_list


def player_job_creator(pl):
    fetch_result = fetch_player(player=pl)
    this_player = parse_player(soup=fetch_result[0], url=fetch_result[1])
    print "Finished parsing Player {0}".format(this_player['name'])
    return this_player


def player_season_job_creator(player):
    gamelist = []
    for season in player['seasons']:
        soup, fetched_url = fetch_player_season(player['page_url'], season)
        gamelist.extend(parse_player_season(player=player, soup=soup))
        print "Finished Season {0} Player {1}".format(season, player['name'])

    return gamelist


def log_plist(result):
    glob_plist.extend(result)


def log_player(result):
    glob_player.append(result)


def log_player_season(result):
    glob_player_season.extend(result)


def dump_games_to_csv(all_games):
    f = open('output/time_{0}.csv'.format(int(time.time())), 'wb')
    writer = csv.writer(f)
    writer.writerow(all_games[0].keys())
    for i in all_games:
        writer.writerow(i.values())


def mp_main():
    # Set ASCII list for all last names
    last_names_list = ascii_lowercase

    start_time = time.time()

    # Start Multiprocessing for Player Lists
    pool = Pool()

    for i in last_names_list:
        pool.apply_async(plist_job_creator, args=(i,), callback=log_plist)

    pool.close()
    pool.join()
    pool.terminate()
    # Finish Multiprocessing for Player Lists

    # Start Multiprocessing for Players
    pool = Pool()
    for i in glob_plist:
        pool.apply_async(player_job_creator, args=(i,), callback=log_player)

    pool.close()
    pool.join()
    pool.terminate()

    # Finish Multiprocessing for Players

    # Start Multiprocessing for Player-Seasons
    pool = Pool()
    for i in glob_player:
        pool.apply_async(player_season_job_creator, args=(i,), callback=log_player_season)

    pool.close()
    pool.join()
    pool.terminate()

    # Finish Multiprocessing for Player-Seasons

    print "RUN TIME {0:.2f}".format((time.time()-start_time)/60)


def test():
    t = fetch_playerlist('x')
    a = parse_playerlist(t[0])

    print a

if __name__ == "__main__":
    mp_main()
    dump_games_to_csv(glob_player_season)
