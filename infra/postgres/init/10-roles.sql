-- Runs once, when the postgres volume is first created, after 00-databases.sql.
-- The owner, migrator and runtime roles (0.4.2) in both local databases, from
-- the backend's one definition — mounted at /sadara/database-roles.sql from
-- backend/scripts/database-roles.sql, which CI and `just migrations` run too.
-- Its passwords are SADARA_MIGRATOR_PASSWORD and SADARA_APP_PASSWORD (infra/.env).
\connect sadara
\i /sadara/database-roles.sql
\connect sadara_test
\i /sadara/database-roles.sql
