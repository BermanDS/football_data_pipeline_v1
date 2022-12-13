#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<-EOSQL
    
    /* -------------------------------- Create rolw ------------------------------------------------*/
    -- Create Role: bot_parser 
    CREATE ROLE bot_parser WITH
    LOGIN
    NOSUPERUSER
    INHERIT
    CREATEDB
    NOCREATEROLE
    NOREPLICATION
    ENCRYPTED PASSWORD 'md5bb28a329be706bc0b8994c783541873d';
    COMMENT ON ROLE bot_parser IS 'for parsing data by Streaming';
    /* -------------------- Create database ------------------------------------------------------------*/
    CREATE DATABASE streamingdb
    WITH 
    OWNER = admin
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;   
    
    /* -------------------------- Create schema ------------------------------------------------------*/
    -- SCHEMA: football_events
    \connect streamingdb;
    CREATE SCHEMA football_events
    AUTHORIZATION admin;
    GRANT ALL ON SCHEMA football_events TO admin;
    GRANT ALL ON SCHEMA football_events TO bot_parser;

    /*------------------------- Create tables ---------------------------------------------------------------*/
    -- Table: football_events.competitions
    CREATE TABLE IF NOT EXISTS football_events.competitions
    (
    competition_id bigint NOT NULL,
    competition_name character varying COLLATE pg_catalog."default",
    competition_gender character varying COLLATE pg_catalog."default",
    CONSTRAINT competitions_pkey PRIMARY KEY (competition_id)
    )
    TABLESPACE pg_default;
    ALTER TABLE football_events.competitions
        OWNER to admin;
    REVOKE ALL ON TABLE football_events.competitions FROM bot_parser;
    GRANT ALL ON TABLE football_events.competitions TO admin;
    GRANT DELETE, INSERT, SELECT, UPDATE ON TABLE football_events.competitions TO bot_parser;
    
    -- Table: football_events.competitions_matches
    CREATE TABLE IF NOT EXISTS football_events.competitions_matches
    (
    event_id bigint NOT NULL,
    start_time timestamp with time zone,
    competition_id bigint,
    CONSTRAINT competitions_matches_pkey PRIMARY KEY (event_id),
    CONSTRAINT competitions_matches_competition_id_fkey FOREIGN KEY (competition_id)
    REFERENCES football_events.competitions (competition_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID
    )
    TABLESPACE pg_default;
    ALTER TABLE football_events.competitions_matches OWNER to admin;
    REVOKE ALL ON TABLE football_events.competitions_matches FROM bot_parser;
    GRANT ALL ON TABLE football_events.competitions_matches TO admin;
    GRANT DELETE, INSERT, SELECT, UPDATE ON TABLE football_events.competitions_matches TO bot_parser;
    
    -- Table: football_events.map_action
    CREATE TABLE IF NOT EXISTS football_events.map_action
    (
    id smallint NOT NULL,
    value character varying COLLATE pg_catalog."default",
    CONSTRAINT map_action_pkey PRIMARY KEY (id)
    )
    TABLESPACE pg_default;
    ALTER TABLE football_events.map_action OWNER to admin;
    REVOKE ALL ON TABLE football_events.map_action FROM bot_parser;
    GRANT ALL ON TABLE football_events.map_action TO admin;
    GRANT DELETE, INSERT, SELECT, UPDATE ON TABLE football_events.map_action TO bot_parser;

    -- Table: football_events.map_period
    CREATE TABLE IF NOT EXISTS football_events.map_period
    (
    id smallint NOT NULL,
    value character varying COLLATE pg_catalog."default",
    CONSTRAINT map_period_pkey PRIMARY KEY (id)
    )
    TABLESPACE pg_default;
    ALTER TABLE football_events.map_period OWNER to admin;
    REVOKE ALL ON TABLE football_events.map_period FROM bot_parser;
    GRANT ALL ON TABLE football_events.map_period TO admin;
    GRANT DELETE, INSERT, SELECT, UPDATE ON TABLE football_events.map_period TO bot_parser;

    -- Table: football_events.map_competitor
    CREATE TABLE IF NOT EXISTS football_events.map_competitor
    (
    id smallint NOT NULL,
    value character varying COLLATE pg_catalog."default",
    CONSTRAINT map_competitor_pkey PRIMARY KEY (id)
    )
    TABLESPACE pg_default;
    ALTER TABLE football_events.map_competitor OWNER to admin;
    REVOKE ALL ON TABLE football_events.map_competitor FROM bot_parser;
    GRANT ALL ON TABLE football_events.map_competitor TO admin;
    GRANT DELETE, INSERT, SELECT, UPDATE ON TABLE football_events.map_competitor TO bot_parser;

    -- Table: football_events.map_breaks
    CREATE TABLE IF NOT EXISTS football_events.map_breaks
    (
    id smallint NOT NULL,
    value character varying COLLATE pg_catalog."default",
    CONSTRAINT map_breaks_pkey PRIMARY KEY (id)
    )
    TABLESPACE pg_default;
    ALTER TABLE football_events.map_breaks OWNER to admin;
    REVOKE ALL ON TABLE football_events.map_breaks FROM bot_parser;
    GRANT ALL ON TABLE football_events.map_breaks TO admin;
    GRANT DELETE, INSERT, SELECT, UPDATE ON TABLE football_events.map_breaks TO bot_parser;

    -- Table: football_events.map_method
    CREATE TABLE IF NOT EXISTS football_events.map_method
    (
    id smallint NOT NULL,
    value character varying COLLATE pg_catalog."default",
    CONSTRAINT map_method_pkey PRIMARY KEY (id)
    )
    TABLESPACE pg_default;
    ALTER TABLE football_events.map_method OWNER to admin;
    REVOKE ALL ON TABLE football_events.map_method FROM bot_parser;
    GRANT ALL ON TABLE football_events.map_method TO admin;
    GRANT DELETE, INSERT, SELECT, UPDATE ON TABLE football_events.map_method TO bot_parser;

    -- Table: football_events.match_actions
    CREATE TABLE IF NOT EXISTS football_events.match_actions
    (
    id bigint NOT NULL,
    event_id bigint NOT NULL,
    map_action smallint,
    datetime timestamp with time zone,
    period smallint,
    map_period smallint,
    match_time real,
    match_clock smallint[],
    map_competitor smallint,
    score smallint[],
    CONSTRAINT match_actions_pkey PRIMARY KEY (id, event_id),
    CONSTRAINT match_actions_event_id_fkey FOREIGN KEY (event_id)
        REFERENCES football_events.competitions_matches (event_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT match_actions_map_action_fkey FOREIGN KEY (map_action)
        REFERENCES football_events.map_action (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT match_actions_map_period_fkey FOREIGN KEY (map_period)
        REFERENCES football_events.map_period (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT match_actions_map_competitor_fkey FOREIGN KEY (map_competitor)
        REFERENCES football_events.map_competitor (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
    )
    TABLESPACE pg_default;
    ALTER TABLE football_events.match_actions OWNER to admin;
    REVOKE ALL ON TABLE football_events.match_actions FROM bot_parser;
    GRANT ALL ON TABLE football_events.match_actions TO admin;
    GRANT DELETE, INSERT, SELECT, UPDATE ON TABLE football_events.match_actions TO bot_parser;

    -- Table: football_events.match_missed_goals
    CREATE TABLE IF NOT EXISTS football_events.match_missed_goals
    (
    id bigint NOT NULL,
    event_id bigint NOT NULL,
    map_action smallint,
    datetime timestamp with time zone,
    period smallint,
    match_time real,
    match_clock smallint[],
    map_competitor smallint,
    score smallint[],
    CONSTRAINT match_missed_goals_pkey PRIMARY KEY (id, event_id),
    CONSTRAINT match_missed_goals_event_id_fkey FOREIGN KEY (event_id)
        REFERENCES football_events.competitions_matches (event_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT match_missed_goals_map_action_fkey FOREIGN KEY (map_action)
        REFERENCES football_events.map_action (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT match_missed_goals_map_competitor_fkey FOREIGN KEY (map_competitor)
        REFERENCES football_events.map_competitor (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
    )
    TABLESPACE pg_default;
    ALTER TABLE football_events.match_missed_goals OWNER to admin;
    REVOKE ALL ON TABLE football_events.match_missed_goals FROM bot_parser;
    GRANT ALL ON TABLE football_events.match_missed_goals TO admin;
    GRANT DELETE, INSERT, SELECT, UPDATE ON TABLE football_events.match_missed_goals TO bot_parser;

    -- Table: football_events.match_goals
    CREATE TABLE IF NOT EXISTS football_events.match_goals
    (
    id bigint NOT NULL,
    event_id bigint NOT NULL,
    map_action smallint,
    datetime timestamp with time zone,
    period smallint,
    match_time real,
    match_clock smallint[],
    map_competitor smallint,
    map_method smallint,
    score smallint[],
    CONSTRAINT match_goals_pkey PRIMARY KEY (id, event_id),
    CONSTRAINT match_goals_event_id_fkey FOREIGN KEY (event_id)
        REFERENCES football_events.competitions_matches (event_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT match_goals_map_action_fkey FOREIGN KEY (map_action)
        REFERENCES football_events.map_action (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT match_goals_map_method_fkey FOREIGN KEY (map_method)
        REFERENCES football_events.map_method (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT match_goals_map_competitor_fkey FOREIGN KEY (map_competitor)
        REFERENCES football_events.map_competitor (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
    )
    TABLESPACE pg_default;
    ALTER TABLE football_events.match_goals OWNER to admin;
    REVOKE ALL ON TABLE football_events.match_goals FROM bot_parser;
    GRANT ALL ON TABLE football_events.match_goals TO admin;
    GRANT DELETE, INSERT, SELECT, UPDATE ON TABLE football_events.match_goals TO bot_parser;

    -- Table: football_events.match_breaks
    CREATE TABLE IF NOT EXISTS football_events.match_breaks
    (
    id bigint NOT NULL,
    event_id bigint NOT NULL,
    map_action smallint,
    datetime timestamp with time zone,
    injury_time_announced real,
    map_period smallint,
    match_time real,
    match_clock smallint[],
    stoppage_time real,
    stoppage_time_clock smallint[],
    map_breaks smallint,
    score smallint[],
    CONSTRAINT match_breaks_pkey PRIMARY KEY (id, event_id),
    CONSTRAINT match_breaks_event_id_fkey FOREIGN KEY (event_id)
        REFERENCES football_events.competitions_matches (event_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT match_breaks_map_action_fkey FOREIGN KEY (map_action)
        REFERENCES football_events.map_action (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT match_breaks_map_period_fkey FOREIGN KEY (map_period)
        REFERENCES football_events.map_period (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT match_breaks_map_breaks_fkey FOREIGN KEY (map_breaks)
        REFERENCES football_events.map_breaks (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
    )
    TABLESPACE pg_default;
    ALTER TABLE football_events.match_breaks OWNER to admin;
    REVOKE ALL ON TABLE football_events.match_breaks FROM bot_parser;
    GRANT ALL ON TABLE football_events.match_breaks TO admin;
    GRANT DELETE, INSERT, SELECT, UPDATE ON TABLE football_events.match_breaks TO bot_parser;

EOSQL