from bs4 import BeautifulSoup
import urllib2

# from class_definitions import Player

BR_ROOT = 'http://www.basketball-reference.com'
BR_PLAYERS = 'http://www.basketball-reference.com/players'


def fetch_parse(datatype, playerlist_lastname=None, player=None, season=None):
    """ fetch_parse calls fetch and parse functions consecutively
        datatype can be one of three, playerlist, player, player_season

        * playerlist gets a list of players w/ given surname
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
        return None

    soup = fetch(datatype, playerlist_lastname=playerlist_lastname, player=player, season=season)
    r_arg = parse(datatype, soup)

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
        pass
        # should never hit here normally


def fetch_playerlist(playerlist_lastname=None):
    # Fetch Part
    fetch_url = "/".join([BR_PLAYERS, playerlist_lastname, ""])

    soup = BeautifulSoup(urllib2.urlopen(fetch_url).read(), 'html5lib')

    return soup


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

    soup = BeautifulSoup(urllib2.urlopen(fetch_url).read(), 'html5lib')

    return soup


def fetch_player_season(player=None, season=None):
    # fetch_url = "/".join([BR_PLAYERS, player[0], player, season])
    pass


def parse(datatype, soup):
    """ parse gets the soup and returns data in the specified level
        fetchtype can be one of three, playerlist, player, player_season

        Check fetch_parse function for more details
    """
    defined_datatypes = ['playerlist', 'player', 'player_season']

    if datatype == defined_datatypes[0]:
        return parse_playerlist(soup)

    elif datatype == defined_datatypes[1]:
        return parse_player(soup)

    elif datatype == defined_datatypes[2]:
        return fetch_player_season(soup)

    else:
        pass
        # should never hit here normally


def parse_playerlist(soup):
    # Parse Part
    # Search for all "a" tags, get href attributes
    table_container = soup.find("table", id="players").find("tbody")

    # num_of_columns = len(table_container.find("tr").find_all("td"))
    playerlist = []

    for i, rows in enumerate(table_container.find_all("tr")):
        t = rows.find_all("td")
        playerlist.append(t[0].a["href"].encode("utf8"))
        # tempplayer = Player(name=t[0].a.text.encode("utf8"), url="".join([BR_ROOT, t[0].a["href"]]),
        #                     firstyear=t[1].text.encode("utf8"), lastyear=t[2].text.encode("utf8"),
        #                     pos=t[3].text.encode("utf8").split("-"), height=int(t[4].text.
        #                     encode("utf8").split("-")[0]) * 12 + int(t[4].text.encode("utf8").
        #                     split("-")[1]), weight=int(t[5].text.encode("utf8")),
        #                     birthday=t[6].text.encode("utf8"), college=t[7].text.encode("utf8"))
    return playerlist


def parse_player(soup):
    # table_container = soup.find("table", id="players").find("tbody")
    pass


def parse_player_season():
    pass


if __name__ == "__main__":
    plist = fetch_parse("playerlist", playerlist_lastname="a")
    print plist[1]
    pl1 = fetch_parse("player", player=plist[0])

    print pl1
