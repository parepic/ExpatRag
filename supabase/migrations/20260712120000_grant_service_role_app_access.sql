-- Grant the service_role (used by the backend and the data pipeline) full DML access
-- to application tables. The initial schema created tables without these grants, so
-- service_role hit "permission denied for table ..." (SQLSTATE 42501) on insert/select.
--
-- service_role bypasses RLS, so these grants are what actually gate its access.

grant select, insert, update, delete on all tables in schema public to service_role;
grant usage, select on all sequences in schema public to service_role;

-- Cover tables/sequences created by future migrations too.
alter default privileges in schema public
  grant select, insert, update, delete on tables to service_role;
alter default privileges in schema public
  grant usage, select on sequences to service_role;
