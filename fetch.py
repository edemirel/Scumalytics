from bs4 import BeautifulSoup
import urllib2

from class_definitions import Player

BR_ROOT = 'http://www.basketball-reference.com'
BR_PLAYERS = 'http://www.basketball-reference.com/players'


def fetch(fetchtype, playerlist_lastname=None, player=None, season=None):
    """ fetchtype can be one of three, playerlist, player, player_season
        playerlist = http://www.basketball-reference.com/players/a/
            Uses playlist argument

        player = http://www.basketball-reference.com/players/a/abdelal01.html
            Uses player argument
            Can be passed in three styles
            */players/a/abdelal01.html
            *abdelal01.html
            *abdelal01

        player_season = http://www.basketball-reference.com/players/a/abdelal01/gamelog/1991/
            Uses player and season argument
    """

    defined_fetchtypes = ['playerlist', 'player', 'player_season']

    # Checking if the fetchtype passed is proper
    if fetchtype not in defined_fetchtypes:
        raise Exception('The fetchtype you have used is not defined\n Please use playerlist, player or player_season')
        return None

    if fetchtype == defined_fetchtypes[0]:
        fetch_url = "/".join([BR_PLAYERS, playerlist_lastname, ""])

        soup = BeautifulSoup(urllib2.urlopen(fetch_url).read(), 'html5lib')

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

    elif fetchtype == defined_fetchtypes[1]:

        # Checking if direct url or playercode is passed
        if len(player.split("/")) == 4:
            fetch_url = "".join([BR_ROOT, player, ""])

        elif len(player.split(".")) == 2:
            fetch_url = "/".join([BR_PLAYERS, player[0], player])

        else:
            fetch_url = "/".join([BR_PLAYERS, player[0], ".".join([player, "html"])])

    elif fetchtype == defined_fetchtypes[2]:
        fetch_url = "/".join([BR_PLAYERS, player[0], player, season])
    else:
        pass
        # should never hit here normally

if __name__ == "__main__":
    plist = fetch("playerlist", playerlist_lastname="a")
    print plist[0]
    pl1 = fetch("player", player=plist[0])
