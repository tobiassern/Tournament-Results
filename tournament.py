#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    DB = connect()
    c = DB.cursor()
    # Just deletes everything from the matches table
    c.execute("DELETE FROM matches")
    DB.commit()
    DB.close()


def deletePlayers():
    """Remove all the player records from the database."""
    DB = connect()
    c = DB.cursor()
    # Just deletes everything from the players table
    c.execute("DELETE FROM players")
    DB.commit()
    DB.close()


def countPlayers():
    """Returns the number of players currently registered."""
    DB = connect()
    c = DB.cursor()
    # Counts all the rows of the players table
    c.execute("SELECT count(*) FROM players")
    count_players = c.fetchone()
    count_players = count_players[0]
    DB.close()
    return count_players


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    DB = connect()
    c = DB.cursor()
    # Inserts the name into the players table
    c.execute("INSERT INTO players (name) VALUES (%s)", (name,))
    DB.commit()
    DB.close()


def playerStandings():
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
    DB = connect()
    c = DB.cursor()
    c.execute(
        """
        SELECT players.player_id, players.name,
        -- Sub query to count the wins for a player
        (SELECT count(matches.winner)
        FROM matches
         WHERE players.player_id = matches.winner) as wins,
        -- Sub query ends
        -- Sub query to count all matches for a player
        (SELECT count(matches.match_id)
        FROM matches
        WHERE players.player_id = matches.winner
        or players.player_id = matches.loser) as matches
        -- Sub query ends
        FROM players
        -- Order by wins primary and mathes secondary
        ORDER BY wins DESC, matches DESC
        """
    )
    result = c.fetchall()
    DB.close()
    return result


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    DB = connect()
    c = DB.cursor()
    # Inserts the winner and loser in a new row of the matches table
    c.execute(
        "INSERT INTO matches (winner, loser) VALUES (%s, %s)",
        (winner, loser,))
    DB.commit()
    DB.close()


def swissPairings():
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
    DB = connect()
    c = DB.cursor()
    c.execute(
        """SELECT players.player_id, players.name,
        -- Sub query to count the wins
        (SELECT count(matches.winner)
        FROM matches
        WHERE players.player_id = matches.winner) as wins
        FROM players LEFT JOIN matches
        ON players.player_id = matches.winner or players.player_id = matches.loser
        GROUP BY players.player_id
        -- Order by wins so the best player comes first
        ORDER BY wins DESC
        """)
    result = c.fetchall()
    result_pairs = []  # Creates a new list to return

    for index, player in enumerate(result):
        # if even number do this, so we only do this once for every pair
        if index % 2 == 0:
            # add the current looped player into result_pair and also the next
            # player
            result_pair = (
                player[0], player[1],
                result[index + 1][0], result[index + 1][1])
            # append the current player in loop and next player into the
            # result_pairs list
            result_pairs.append(result_pair)

    DB.close()
    return result_pairs
