-- Runs once, when the postgres volume is first created (docker-entrypoint-initdb.d).
-- POSTGRES_DB creates the development database, sadara. The test harness (0.2.3)
-- gets its own, so test schemas never share a database with local data.
-- The owner, migrator and runtime roles arrive with 0.4.2, in 10-roles.sql.
CREATE DATABASE sadara_test;
