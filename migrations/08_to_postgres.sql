ALTER TABLE karma_events ALTER COLUMN date type timestamp with time zone using date::timestamp with time zone;
ALTER TABLE moderator_events ALTER COLUMN date type timestamp with time zone using date::timestamp with time zone;
ALTER TABLE reports ALTER COLUMN created_time type timestamp with time zone using created_time::timestamp with time zone;
ALTER TABLE reports ALTER COLUMN resolution_time type timestamp with time zone using created_time::timestamp with time zone;
