-- DDL script for STEAM data direct access in exasol

-- create table for import
create schema STEAM;

create or replace table STEAM.reviews (
  review_id integer identity,
  game_id decimal(36,0),
  review varchar(200000),
  sentiment decimal(1,0),
  helpful decimal(36,0)
);


import into STEAM.reviews (game_id, review, sentiment, helpful)
  from local csv file '/Users/mor/Projects/areto/exasol-showcase/data/steam.csv'
    column separator = ','
    column delimiter = '"'
    skip = 0;

create or replace table STEAM.test as (
  select *
  from STEAM.reviews
  order by random()
  limit 10
);