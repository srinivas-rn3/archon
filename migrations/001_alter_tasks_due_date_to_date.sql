-- Migration: convert tasks.due_date from timestamp to date
-- Postgres example: casts existing timestamps to date
BEGIN;
ALTER TABLE tasks ALTER COLUMN due_date TYPE date USING (due_date::date);
COMMIT;

-- If you're using SQLite, use a manual table rebuild; Alembic recommended for production.