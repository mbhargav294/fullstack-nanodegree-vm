-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

CREATE TABLE tournaments( tournament_id TEXT PRIMARY KEY,
                          tournament_name VARCHAR(50));

-- This table maintains players id and player names
CREATE TABLE players ( tournament_id TEXT REFERENCES tournaments(tournament_id) ON DELETE CASCADE,
                       player_id SERIAL,
                       player_name VARCHAR(50),
                       PRIMARY KEY (tournament_id, player_id));

-- This table contains the records for matches
-- Each record contains match id, winner id and looser id
CREATE TABLE matches ( tournament_id TEXT REFERENCES tournaments(tournament_id) ON DELETE CASCADE,
                       match_id SERIAL,
                       winner INTEGER,
                       loser INTEGER,
                       PRIMARY KEY (tournament_id, match_id),
                       FOREIGN KEY (tournament_id, winner) REFERENCES players(tournament_id, player_id) ON DELETE CASCADE,
                       FOREIGN KEY (tournament_id, loser) REFERENCES players(tournament_id, player_id) ON DELETE CASCADE);

-- This view generates the player standings in the tournament
-- This view queries both the players table and matches table
-- in order to generate the standings
CREATE VIEW standings AS
    SELECT PP.tournament_id as tournament, PP.player_id AS id, PP.player_name AS name,
        (SELECT COUNT(P.player_id)
            FROM players P, matches M WHERE
            P.player_id = PP.player_id AND P.tournament_id = PP.tournament_id AND P.player_id = M.winner) AS wins,
            ((SELECT COUNT(P.player_id) AS wins
                FROM players P, matches M WHERE
                P.player_id = PP.player_id AND P.tournament_id = PP.tournament_id AND P.player_id = M.winner) +
             (SELECT COUNT(P.player_id) AS looses
                FROM players P, matches M WHERE
                P.player_id = PP.player_id AND P.tournament_id = PP.tournament_id AND P.player_id = M.loser)) AS matches
    FROM players PP ORDER BY tournament, wins DESC;

-- This view is used in the countPlayers function in tournament.py
-- to return the number of players
CREATE VIEW no_of_players AS
    SELECT T.tournament_id, COUNT(P.player_id) as num
    FROM tournaments T LEFT JOIN players P ON T.tournament_id = P.tournament_id
    GROUP BY T.tournament_id;
