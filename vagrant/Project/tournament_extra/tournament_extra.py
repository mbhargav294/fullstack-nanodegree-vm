#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import bleach
import hashlib
import random
import string


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament_extra")


def make_salt():
    return ''.join(random.sample(string.ascii_letters, 5))


def createNewTournament(name):
    """Creates a new tournament in the database and returns the ID of this
    new Tournament. This function will generate a unique id for each tournament
    and return this unique id when ever a new id is created.

    Returns id for created tournament

    Args:
        name: tournament's name (Need not be unique)
    """
    if name:
        conn = connect()
        cur = conn.cursor()
        t_id = name.lower().replace(" ", "_")
        cur.execute("SELECT COUNT(*) FROM tournaments WHERE tournament_id LIKE %s",
                    ('%' + bleach.clean(t_id) + '%',))
        c = cur.fetchall()
        t_id = t_id + "_" + str(c[0][0])
        cur.close()

        cur = conn.cursor()
        cur.execute("INSERT INTO tournaments VALUES(%s, %s)",
                    (bleach.clean(t_id), bleach.clean(name),))
        conn.commit()
        cur.close()
        conn.close()
        return t_id
        # return t_id


def deleteTournaments():
    """Remove all the tournament records from the database."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM tournaments;")
    conn.commit()
    cur.close()
    conn.close()


def deleteMatches(TOUR_ID):
    """Remove all the match records from the database."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM matches where tournament_id = %s;",
                (bleach.clean(TOUR_ID),))
    conn.commit()
    cur.close()
    conn.close()


def deletePlayers(TOUR_ID):
    """Remove all the player records from the database."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM players where tournament_id = %s;",
                (bleach.clean(TOUR_ID),))
    conn.commit()
    cur.close()
    conn.close()


def countPlayers(TOUR_ID):
    """Returns the number of players currently registered."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM no_of_players where tournament_id = %s;",
                (bleach.clean(TOUR_ID),))
    num = cur.fetchall()
    cur.close()
    conn.close()
    if num:
        return num[0][1]


def registerPlayer(TOUR_ID, name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    cur = conn.cursor()
    if name:
        cur.execute(
            "INSERT INTO players (tournament_id, player_name) VALUES(%s, %s)",
            (bleach.clean(TOUR_ID), bleach.clean(name),))
    conn.commit()
    cur.close()
    conn.close()


def playerStandings(TOUR_ID):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * from standings WHERE tournament=%s;",
                (bleach.clean(TOUR_ID),))
    standings = cur.fetchall()
    cur.close()
    conn.close()
    if standings:
        return standings


def reportMatch(TOUR_ID, winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    cur = conn.cursor()
    if winner and loser:
        cur.execute("INSERT INTO matches (tournament_id, winner, loser) VALUES(%s, %s, %s)",
                    (bleach.clean(TOUR_ID), bleach.clean(winner), bleach.clean(loser),))
    conn.commit()
    cur.close()
    conn.close()


def swissPairings(TOUR_ID):
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings(TOUR_ID)
    pairs = []
    if standings and len(standings) % 2 == 0:
        for i in range(len(standings)):
            if i % 2 == 0:
                pairs.append([standings[i][1], standings[i][2],
                              standings[i + 1][1], standings[i + 1][2]])
    return pairs
