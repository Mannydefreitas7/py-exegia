-- -----------------------------------------------------------------------
-- Generic library book tables
-- -----------------------------------------------------------------------

create type public.book_category as enum (
  'bible', 'commentary', 'lexicon', 'dictionary',
  'devotional', 'theology', 'history', 'philosophy',
  'fiction', 'other'
);

create type public.book_source_type as enum (
  'epub', 'pdf', 'url', 'manual'
);

create type public.book_section_type as enum (
  'part', 'chapter', 'section', 'article', 'entry',
  'appendix', 'introduction', 'preface', 'foreword',
  'index', 'glossary', 'other'
);

-- -----------------------------------------------------------------------
-- library_books
-- -----------------------------------------------------------------------
create table if not exists public.library_books (
  uuid            text                     primary key default gen_random_uuid()::text,
  slug            text                     not null unique,

  -- identity
  title           varchar(500)             not null,
  subtitle        varchar(500),
  authors         jsonb,
  publisher       varchar(255),
  published_date  varchar(50),
  language        varchar(10)              not null default 'en',
  text_direction  varchar(3)               not null default 'ltr',

  -- classification
  category        public.book_category     not null default 'other',
  subjects        jsonb,

  -- origin
  source_type     public.book_source_type  not null default 'manual',
  source_uri      text,

  -- assets & rights
  cover_url       text,
  description     text,
  website         text,
  license         varchar(100),
  license_url     text,

  -- denormalised counters
  total_sections  integer                  not null default 0,
  total_pages     integer                  not null default 0,

  -- escape hatch
  extra           jsonb,

  -- timestamps
  created_at      timestamptz              not null default now(),
  updated_at      timestamptz              not null default now()
);

create index if not exists ix_library_books_category on public.library_books (category);
create index if not exists ix_library_books_language on public.library_books (language);

-- -----------------------------------------------------------------------
-- book_sections  (self-referential hierarchy)
-- -----------------------------------------------------------------------
create table if not exists public.book_sections (
  uuid          text                       primary key default gen_random_uuid()::text,
  book_uuid     text                       not null references public.library_books (uuid) on delete cascade,
  parent_uuid   text                       references public.book_sections (uuid) on delete cascade,

  title         varchar(500),
  section_type  public.book_section_type   not null default 'chapter',
  level         integer                    not null default 0,
  "order"       integer                    not null default 0,

  total_pages   integer                    not null default 0,
  extra         jsonb
);

create index if not exists ix_book_sections_book_uuid   on public.book_sections (book_uuid);
create index if not exists ix_book_sections_parent_uuid on public.book_sections (parent_uuid);

-- -----------------------------------------------------------------------
-- book_pages
-- -----------------------------------------------------------------------
create table if not exists public.book_pages (
  uuid           text        primary key default gen_random_uuid()::text,
  book_uuid      text        not null references public.library_books (uuid) on delete cascade,
  section_uuid   text        references public.book_sections (uuid) on delete set null,

  title          varchar(500),
  book_index     integer     not null default 0,
  section_index  integer     not null default 0,

  html           text,
  text           text,
  extra          jsonb
);

create index if not exists ix_book_pages_book_uuid     on public.book_pages (book_uuid);
create index if not exists ix_book_pages_section_uuid  on public.book_pages (section_uuid);
create index if not exists ix_book_pages_book_index    on public.book_pages (book_uuid, book_index);

-- -----------------------------------------------------------------------
-- Auto-update updated_at on library_books
-- -----------------------------------------------------------------------
create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger trg_library_books_updated_at
  before update on public.library_books
  for each row execute function public.set_updated_at();
