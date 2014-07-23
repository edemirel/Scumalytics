from bs4 import BeautifulSoup
import urllib2
import re
import inspect

from class_definitions import Player

BR_ROOT = 'http://www.basketball-reference.com'
BR_PLAYERS = 'http://www.basketball-reference.com/players'


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


def fetch_playerlist(playerlist_lastname=None):
    # Fetch Part
    fetch_url = "/".join([BR_PLAYERS, playerlist_lastname, ""])

    soup = BeautifulSoup(urllib2.urlopen(fetch_url).read(), 'html.parser')

    return soup, fetch_url


def fetch_player(player=None):

    # Checking if direct url or playercode is passed
    # Case /players/a/abdelal01.html
    if len(player.split("/")) == 4:
        fetch_url = "".join([BR_ROOT, player, ""])

    # Case abdelal01.html
    elif len(player.split(".")) == 2:
        fetch_url = "/".join([BR_PLAYERS, player[0], player])

    # Case abdelal01
    else:
        fetch_url = "/".join([BR_PLAYERS, player[0], ".".join([player, "html"])])

    soup = BeautifulSoup(urllib2.urlopen(fetch_url).read(), 'html.parser')

    return soup, fetch_url


def fetch_player_season(player=None, season=None):
    # fetch_url = "/".join([BR_PLAYERS, player[0], player, season])
    pass


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
        return fetch_player_season(soup, url)

    else:
        raise Exception('The type you have used is not defined\n Please use playerlist, player or player_season')


def parse_playerlist(soup, yearfrom=1996):
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

    # INIT DATAPOINTS AS BLANK
    player_name = None
    img_link = None
    pos = None
    shoots = None
    height = None
    weight = None
    birthday = None
    birthcity = None
    birthcountry = None
    college = None
    draftcity = None
    draftteam = None
    draftround = None
    draftroundpick = None
    draftpos = None

    infobox = soup.find("div", id="info_box")

    draftregex = re.compile(r", (\d).+?(\d{1,3}).+?(\d{1,3}).+")

    # DataPoint
    img_link = infobox.find("div", attrs={'class': "person_image"})
    if img_link is None:
        img_link = ''
    else:
        img_link = infobox.find("div", attrs={'class': "person_image"}).find("img")["src"]

    playerdata = infobox.find("div", attrs={'class': "person_image_offset"})
    if playerdata is None:
        playerdata = infobox

    # DataPoint
    player_name = playerdata.h1.text
    print player_name

    for p in playerdata.find_all("span"):
        if p.text == "Position:":
            temp_text = repr(p.next_sibling)
            begin = temp_text.find(" ")+1
            end = temp_text.find("\\")

            # DataPoint
            pos = pos_to_num(temp_text[begin:end].split(" and "))

        elif p.text == "Shoots:":
            temp_text = repr(p.next_sibling)
            begin = temp_text.find(" ")+1
            end = temp_text.rfind("\\")

            # DataPoint
            shoots = temp_text[begin:end]

        elif p.text == "Height:":
            temp_text = repr(p.next_sibling)
            begin = temp_text.find(" ")+1
            end = temp_text.find("\\")

            # DataPoint
            height = int(temp_text[begin:end].split("-")[0]) * 12 + int(
                temp_text[begin:end].split("-")[0])

        elif p.text == "Weight:":
            temp_text = repr(p.next_sibling)
            begin = temp_text.find(" ")+1
            end = temp_text.find(" lbs")

            # DataPoint
            weight = int(temp_text[begin:end])

        elif p.has_attr("id"):
            if p['id'] == "necro-birth":
                # DataPoint
                birthday = p['data-birth']

                temp_text = repr(p.next_sibling)
                temp_text = temp_text.lstrip("u\' in ")
                end = temp_text.find(",")

                birthcity = temp_text[:end]

                birthcountry = p.next_sibling.next_sibling.text

        elif p.text == "College:":
            college = p.next_sibling.next_sibling.text
            print college

        elif p.text == "Draft:":
            draftinfo = p.next_sibling.next_sibling
            # DataPoint
            draftcity = draftinfo["href"].split("/")[2]
            draftteam = draftinfo.text

            hit = re.match(draftregex, draftinfo.next_sibling)

            # DataPoint
            draftround = int(hit.group(1))
            draftroundpick = int(hit.group(2))
            draftpos = int(hit.group(3))

        else:
            pass

    tempplayer = Player(name=player_name, page_url=url, img_url=img_link, pos=pos, shoots=shoots, height=height,
                        weight=weight, birthday=birthday, birthcity=birthcity, birthcountry=birthcountry,
                        college=college, draftcity=draftcity, draftteam=draftteam, draftround=draftround,
                        draftroundpick=draftroundpick, draftpos=draftpos)

    return tempplayer


def parse_player_season(soup):
    # osmanabimevdemi
    pass


if __name__ == "__main__":
    plist = fetch_parse(datatype="playerlist", playerlist_lastname="a")

    pl1 = fetch_parse(datatype="player", player=plist[11])

    attrs = vars(pl1)

    print ', '.join("%s: %s" % item for item in attrs.items())
