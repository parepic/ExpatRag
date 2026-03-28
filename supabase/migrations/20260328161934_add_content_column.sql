alter table "public"."sources" add column "content" text not null;

alter table "public"."sources" alter column "source_url" set not null;

CREATE UNIQUE INDEX sources_source_url_key ON public.sources USING btree (source_url);

alter table "public"."sources" add constraint "sources_source_url_key" UNIQUE using index "sources_source_url_key";


