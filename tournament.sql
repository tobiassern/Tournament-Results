-- Creating table for players with name and player_id
-- Putting this first as the matches table references back to this
CREATE TABLE players ( name TEXT, player_id SERIAL primary key);

-- Creating tables for matches which contains the winner and loser,
-- which is referenced to the player_id in players table,
-- and also a match-id
CREATE TABLE matches (
	winner INTEGER REFERENCES players (player_id),
	loser INTEGER REFERENCES players (player_id),
	match_id SERIAL PRIMARY KEY
	);