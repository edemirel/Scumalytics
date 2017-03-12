# [SublimeLinter flake8-max-line-length:135]
from bs4 import BeautifulSoup
from multiprocessing import Pool
from string import ascii_lowercase
import urllib2
import re
import copy
import time
import csv
import logging
from logging import handlers
import pdb
import httplib
import socket

class TLSSMTPHandler(handlers.SMTPHandler):
    def emit(self, record):
        """
        Emit a record.
 
        Format the record and send it to the specified addressees.
        """
        try:
            import smtplib
            import string # for tls add this line
            try:
                from email.utils import formatdate
            except ImportError:
                formatdate = self.date_time
            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT
            smtp = smtplib.SMTP(self.mailhost, port)
            msg = self.format(record)
            msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
                            self.fromaddr,
                            string.join(self.toaddrs, ","),
                            self.getSubject(record),
                            formatdate(), msg)
            if self.username:
                smtp.ehlo() # for tls add this line
                smtp.starttls() # for tls add this line
                smtp.ehlo() # for tls add this line
                smtp.login(self.username, self.password)
            smtp.sendmail(self.fromaddr, self.toaddrs, msg)
            smtp.quit()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

MAILHOST = ("smtp.gmail.com", 587)
FROM     = 'egedemirel@gmail.com'
TO       = ['egedemirel@gmail.com']
SUBJECT  = 'Test Logging email from Python logging module (scumalytics)'

thisLogger = logging.getLogger("scumalytics")
thisLogger.level=logging.DEBUG

formatting = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

fh = logging.FileHandler('scumalytics.log')
sh = logging.StreamHandler()
# eh = TLSSMTPHandler(MAILHOST, FROM, TO, SUBJECT, ('asd@dsa.com', 'geagohuhegoa'))

fh.setFormatter(formatting)
sh.setFormatter(formatting)
# eh.setFormatter(formatting)
thisLogger.addHandler(fh)
thisLogger.addHandler(sh)
# thisLogger.addHandler(eh)

BR_ROOT = 'http://www.basketball-reference.com'
BR_PLAYERS = 'http://www.basketball-reference.com/players/{lastname_firstletter}/{player_name}'
BR_SEASONS = 'http://www.basketball-reference.com/players/{lastname_firstletter}/{player_name}/gamelog/{season}'

parser = 'html.parser'

start_year = 2010

glob_plist = []
glob_player = []
glob_player_season = []

positions = {'Center': 5, 'Power Forward': 4,
             'Small Forward': 3, 'Shooting Guard': 2, 'Point Guard': 1}
num_to_position = {v: k for k, v in positions.items()}


def pos_to_num(input_pos):
    return [positions[p] for p in input_pos]


def num_to_pos(input_pos):
    return [num_to_position[p] for p in input_pos]

def robot_delay_retry_function(func):
    def wrapper(*args, **kwargs):
        # time.sleep(1.5)
        didComplete = True
        while didComplete:
            try:
                result = func(*args, **kwargs)
                didComplete = False
            except httplib.IncompleteRead, socket.timeout:
                thisLogger.debug("Fetch failed, retrying")
                didComplete=True
        return result
    return wrapper


@robot_delay_retry_function
def fetch_playerlist(playerlist_lastname):

    # Fetch Part
    fetch_url = BR_PLAYERS.format(
        lastname_firstletter=playerlist_lastname, player_name="")

    soup = BeautifulSoup(urllib2.urlopen(fetch_url, timeout=60).read(), parser)

    return soup, fetch_url

@robot_delay_retry_function
def fetch_player(player):
    # Checking if direct url or playercode is passed

    fetch_url = BR_PLAYERS.format(
        lastname_firstletter=player[0], player_name=".".join([player, "html"]))

    soup = BeautifulSoup(urllib2.urlopen(fetch_url, timeout=60).read(), parser)

    return soup, fetch_url

@robot_delay_retry_function
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

    fetch_url = BR_SEASONS.format(
        lastname_firstletter=player_tag[0], player_name=player_tag, season=season)

    soup = BeautifulSoup(urllib2.urlopen(fetch_url, timeout=60).read(), parser)

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
        if int(row.find_all("td")[1].text) >= yearfrom:
            playerlist.append(
                row.find_all("th")[0].a["href"].encode("utf8").split("/")[3].split(".")[0])

    return playerlist


def parse_player(soup, url):

    # INIT DATAPOINTS AS BLANK, THIS IS TO PREVENT ERRORS IF THE PARSE DOESNT
    # HAPPEN
    tempplayer = {'page_url': url}

    infobox = soup.find("div", id="info")

    draftregex = re.compile(r", (\d).+?(\d{1,3}).+?(\d{1,3}).+")

    # DataPoint
    img_link = infobox.find("div", attrs={'class': "media-item"})
    if img_link is not None:
        tempplayer['img_url'] = infobox.find(
            "div", attrs={'class': "media-item"}).find("img")["src"]

    playerdata = infobox.find("div", attrs={'itemtype': "http://schema.org/Person"})
    # if playerdata is None:
    # playerdata = infobox

    # DataPoint
    tempplayer['name'] = playerdata.h1.text.encode("utf8")

    # Seasonal Data
    seasontable = soup.find("table", id="per_game").find("tbody")
    seasonlist = []
    for row in seasontable.find_all("tr"):
        t = row.find_all("th")
        if t != []: # skip empty seasons
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
            for q, col in enumerate(all_columns_in_row):
                i = q+1 # This is an extremely dirty hack because basketball reference changed first columns w/ th tag instead of td
                if i == 0:
                    temp_game['game_num'] = maybe_int(row.find_all("th")[0].text)

                elif i == 1:
                    temp_game['player_game_num'] = maybe_int(col.text)
                elif i == 2:
                    temp_game['game_date'] = col.text.encode("utf8")
                elif i == 3:
                    # pdb.set_trace()
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
                    temp_game['point_differential'] = maybe_int(
                        temp_text.split(" ")[1].split("(")[1].split(")")[0])
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
    last_names_list = ascii_lowercase.replace('x', '')

    for ln in last_names_list[0:2]:
        thisLogger.debug("Fetching playerlist for last names starting with  ""{playerlist_lastname}""".format(playerlist_lastname=ln))
        player_list = fetch_playerlist(playerlist_lastname=ln)[0]
        thisLogger.debug("Parsing playerlist for last names starting with  ""{playerlist_lastname}""".format(playerlist_lastname=ln))
        this_player_list = parse_playerlist(player_list)
        thisLogger.debug("Got playerlist \t""{0}"" \tContains {1}".format(ln.upper(), len(this_player_list)))
        glob_plist.extend(this_player_list)

    for pl in glob_plist[0:3]:
        thisLogger.debug("Fetching player {player}".format(player=pl))
        fetch_result = fetch_player(player=pl)
        thisLogger.debug("Parsing player {player}".format(player=pl))
        this_player = parse_player(
            soup=fetch_result[0], url=fetch_result[1])
        glob_player.append(this_player)
        thisLogger.debug("Finished parsing Player {name} for general information. His seasons are {seasons}".format(name=this_player['name'], seasons=", ".join(this_player['seasons'])))

        for season in this_player['seasons']:
            soup, fetched_url = fetch_player_season(
                this_player['page_url'], season)
            glob_player_season.extend(
                parse_player_season(player=this_player, soup=soup))
            end_time = time.time()
            gen_text = "Finished Season {0} Player {1}. Running for {2:.2f} min"
            thisLogger.debug(gen_text.format(season, this_player['name'], (end_time - start_time) / 60))

    # dump_games_to_csv(glob_player_season)

    thisLogger.debug("RUN TIME {0:.2f}".format((time.time() - start_time) / 60))


def plist_job_creator(ln):
    this_player_list = parse_playerlist(
        fetch_playerlist(playerlist_lastname=ln)[0])
    thisLogger.debug(
        "Finished PList {0} Length {1}".format(ln, len(this_player_list)))
    return this_player_list


def player_job_creator(pl):
    fetch_result = fetch_player(player=pl)
    this_player = parse_player(soup=fetch_result[0], url=fetch_result[1])
    thisLogger.debug("Finished parsing Player {0}".format(this_player['name']))
    return this_player


def player_season_job_creator(player):
    gamelist = []
    for season in player['seasons']:
        soup, fetched_url = fetch_player_season(player['page_url'], season)
        gamelist.extend(parse_player_season(player=player, soup=soup))
        thisLogger.debug(
            "Finished Season {0} Player {1}".format(season, player['name']))

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
        pool.apply_async(
            player_season_job_creator, args=(i,), callback=log_player_season)

    pool.close()
    pool.join()
    pool.terminate()

    # Finish Multiprocessing for Player-Seasons

    thisLogger.debug("RUN TIME {0:.2f}".format((time.time() - start_time) / 60))


def test():
    t = fetch_playerlist('x')
    a = parse_playerlist(t[0])

    thisLogger.debug(a)

if __name__ == "__main__":
    linear_main()
    dump_games_to_csv(glob_player_season)
    # pass
