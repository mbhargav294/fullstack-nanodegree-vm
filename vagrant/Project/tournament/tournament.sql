-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.


-- This table maintains players id and player names
CREATE TABLE players ( player_id SERIAL PRIMARY KEY,
                       player_name VARCHAR(50));

-- This table contains the records for matches
-- Each record contains match id, winner id and looser id
CREATE TABLE matches ( match_id SERIAL PRIMARY KEY,
                       winner INTEGER REFERENCES players(player_id),
                       loser INTEGER REFERENCES players(player_id));

-- This view generates the player standings in the tournament
-- This view queries both the players table and matches table
-- in order to generate the standings
CREATE VIEW standings AS
    SELECT PP.player_id AS id, PP.player_name AS name,
        (SELECT COUNT(P.player_id)
            FROM players P, matches M WHERE
            P.player_id = PP.player_id AND P.player_id = M.winner) AS wins,
            ((SELECT COUNT(P.player_id) AS wins
                FROM players P, matches M WHERE
                P.player_id = PP.player_id AND P.player_id = M.winner) +
             (SELECT COUNT(P.player_id) AS looses
                FROM players P, matches M WHERE
                P.player_id = PP.player_id AND P.player_id = M.loser)) AS matches
    FROM players PP ORDER BY wins DESC, id ASC;

-- This view is used in the countPlayers function in tournament.py
-- to return the number of players
CREATE VIEW no_of_players AS
    SELECT COUNT(*) as num
    FROM players;
