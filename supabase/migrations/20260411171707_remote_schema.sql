


SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


COMMENT ON SCHEMA "public" IS 'standard public schema';



CREATE EXTENSION IF NOT EXISTS "pg_graphql" WITH SCHEMA "graphql";






CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "supabase_vault" WITH SCHEMA "vault";






CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "extensions";






CREATE OR REPLACE FUNCTION "public"."rls_auto_enable"() RETURNS "event_trigger"
    LANGUAGE "plpgsql" SECURITY DEFINER
    SET "search_path" TO 'pg_catalog'
    AS $$
DECLARE
  cmd record;
BEGIN
  FOR cmd IN
    SELECT *
    FROM pg_event_trigger_ddl_commands()
    WHERE command_tag IN ('CREATE TABLE', 'CREATE TABLE AS', 'SELECT INTO')
      AND object_type IN ('table','partitioned table')
  LOOP
     IF cmd.schema_name IS NOT NULL AND cmd.schema_name IN ('public') AND cmd.schema_name NOT IN ('pg_catalog','information_schema') AND cmd.schema_name NOT LIKE 'pg_toast%' AND cmd.schema_name NOT LIKE 'pg_temp%' THEN
      BEGIN
        EXECUTE format('alter table if exists %s enable row level security', cmd.object_identity);
        RAISE LOG 'rls_auto_enable: enabled RLS on %', cmd.object_identity;
      EXCEPTION
        WHEN OTHERS THEN
          RAISE LOG 'rls_auto_enable: failed to enable RLS on %', cmd.object_identity;
      END;
     ELSE
        RAISE LOG 'rls_auto_enable: skip % (either system schema or not in enforced list: %.)', cmd.object_identity, cmd.schema_name;
     END IF;
  END LOOP;
END;
$$;


ALTER FUNCTION "public"."rls_auto_enable"() OWNER TO "postgres";

SET default_tablespace = '';

SET default_table_access_method = "heap";


CREATE TABLE IF NOT EXISTS "public"."BibleBook" (
    "id" "text",
    "translationId" "text",
    "name" "text",
    "commonName" "text",
    "title" "text",
    "order" integer,
    "numberOfChapters" integer,
    "sha256" "text",
    "isApocryphal" "text",
    "website" "text",
    "licenseUrl" "text",
    "shortName" "text",
    "englishName" "text",
    "language" "text",
    "textDirection" "text" NOT NULL,
    "licenseNotes" "text",
    "uuid" "uuid" DEFAULT "gen_random_uuid"() NOT NULL
);


ALTER TABLE "public"."BibleBook" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."BibleChapter" (
    "number" integer,
    "bookId" "text",
    "translationId" "text",
    "json" "text",
    "sha256" "text",
    "id" "text",
    "name" "text",
    "website" "text",
    "licenseUrl" "text",
    "shortName" "text",
    "englishName" "text",
    "language" "text",
    "textDirection" "text",
    "licenseNotes" "text",
    "uuid" "uuid" DEFAULT "gen_random_uuid"() NOT NULL
);


ALTER TABLE "public"."BibleChapter" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."BibleChapterAudioUrl" (
    "number" integer,
    "bookId" "text",
    "translationId" "text",
    "reader" "text",
    "url" "text",
    "id" "text",
    "name" "text",
    "website" "text",
    "licenseUrl" "text",
    "shortName" "text",
    "englishName" "text",
    "language" "text",
    "textDirection" "text",
    "sha256" "text",
    "licenseNotes" "text",
    "uuid" "uuid" DEFAULT "gen_random_uuid"() NOT NULL
);


ALTER TABLE "public"."BibleChapterAudioUrl" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."ChapterFootnote" (
    "id" integer,
    "chapterNumber" integer,
    "bookId" "text",
    "translationId" "text",
    "text" "text",
    "verseNumber" integer,
    "sha256" "text",
    "name" "text",
    "website" "text",
    "licenseUrl" "text",
    "shortName" "text",
    "englishName" "text",
    "language" "text",
    "textDirection" "text",
    "licenseNotes" "text",
    "uuid" "uuid" DEFAULT "gen_random_uuid"() NOT NULL
);


ALTER TABLE "public"."ChapterFootnote" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."ChapterVerse" (
    "number" integer,
    "chapterNumber" integer,
    "bookId" "text",
    "translationId" "text",
    "text" "text",
    "contentJson" "text",
    "sha256" "text",
    "id" "text",
    "name" "text",
    "website" "text",
    "licenseUrl" "text",
    "shortName" "text",
    "englishName" "text",
    "language" "text",
    "textDirection" "text",
    "licenseNotes" "text",
    "uuid" "uuid" DEFAULT "gen_random_uuid"() NOT NULL
);


ALTER TABLE "public"."ChapterVerse" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."Commentary" (
    "id" "text" NOT NULL,
    "name" "text",
    "website" "text",
    "licenseUrl" "text",
    "englishName" "text",
    "language" "text",
    "textDirection" "text",
    "sha256" "text",
    "licenseNotes" "text",
    "uuid" "uuid" DEFAULT "gen_random_uuid"() NOT NULL
);


ALTER TABLE "public"."Commentary" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."CommentaryBook" (
    "id" "text" NOT NULL,
    "commentaryId" "text",
    "name" "text",
    "commonName" "text",
    "introduction" "text",
    "order" integer,
    "numberOfChapters" integer,
    "sha256" "text",
    "introductionSummary" "text",
    "website" "text",
    "licenseUrl" "text",
    "englishName" "text",
    "language" "text",
    "textDirection" "text",
    "licenseNotes" "text",
    "uuid" "uuid" DEFAULT "gen_random_uuid"() NOT NULL
);


ALTER TABLE "public"."CommentaryBook" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."CommentaryChapter" (
    "number" integer,
    "bookId" "text",
    "commentaryId" "text",
    "introduction" "text",
    "json" "text",
    "sha256" "text",
    "id" "text" NOT NULL,
    "name" "text",
    "website" "text",
    "licenseUrl" "text",
    "englishName" "text",
    "language" "text",
    "textDirection" "text",
    "licenseNotes" "text",
    "uuid" "uuid" DEFAULT "gen_random_uuid"() NOT NULL
);


ALTER TABLE "public"."CommentaryChapter" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."CommentaryChapterVerse" (
    "number" integer,
    "chapterNumber" integer,
    "bookId" "text",
    "commentaryId" "text",
    "text" "text",
    "contentJson" "text",
    "sha256" "text",
    "id" "text",
    "name" "text",
    "website" "text",
    "licenseUrl" "text",
    "englishName" "text",
    "language" "text",
    "textDirection" "text",
    "licenseNotes" "text",
    "uuid" "uuid" DEFAULT "gen_random_uuid"() NOT NULL
);


ALTER TABLE "public"."CommentaryChapterVerse" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."CommentaryProfile" (
    "uuid_old" integer NOT NULL,
    "referenceid" integer,
    "subject" "text",
    "uuid" "uuid" DEFAULT "gen_random_uuid"() NOT NULL
);


ALTER TABLE "public"."CommentaryProfile" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."CommentaryProfileContent" (
    "commentaryid" integer,
    "profileid" bigint,
    "content" "text",
    "uuid_old" integer NOT NULL,
    "uuid" "uuid" DEFAULT "gen_random_uuid"() NOT NULL
);


ALTER TABLE "public"."CommentaryProfileContent" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."CommentaryProfileContent_uuid_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."CommentaryProfileContent_uuid_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."CommentaryProfileContent_uuid_seq" OWNED BY "public"."CommentaryProfileContent"."uuid_old";



CREATE SEQUENCE IF NOT EXISTS "public"."CommentaryProfile_uuid_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."CommentaryProfile_uuid_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."CommentaryProfile_uuid_seq" OWNED BY "public"."CommentaryProfile"."uuid_old";



CREATE TABLE IF NOT EXISTS "public"."CrossReference" (
    "book" integer,
    "chapter" integer,
    "verse" integer,
    "verse_end" integer,
    "book_to" integer,
    "chapter_to" integer,
    "verse_to_start" integer,
    "verse_to_end" "text",
    "votes" "text",
    "uuid" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "verseId" bigint
);


ALTER TABLE "public"."CrossReference" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."Dataset" (
    "id" "text" NOT NULL,
    "name" "text",
    "website" "text",
    "licenseUrl" "text",
    "licenseNotes" "text",
    "englishName" "text",
    "language" "text",
    "textDirection" "text",
    "sha256" "text",
    "uuid" "uuid" DEFAULT "gen_random_uuid"() NOT NULL
);


ALTER TABLE "public"."Dataset" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."DatasetBook" (
    "id" "text" NOT NULL,
    "datasetId" "text",
    "order" integer,
    "numberOfChapters" integer,
    "sha256" "text",
    "name" "text",
    "website" "text",
    "licenseUrl" "text",
    "licenseNotes" "text",
    "englishName" "text",
    "language" "text",
    "textDirection" "text",
    "uuid" "uuid" DEFAULT "gen_random_uuid"() NOT NULL
);


ALTER TABLE "public"."DatasetBook" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."DatasetChapter" (
    "number" integer,
    "bookId" "text",
    "datasetId" "text",
    "json" "text",
    "sha256" "text",
    "id" "text" NOT NULL,
    "name" "text",
    "website" "text",
    "licenseUrl" "text",
    "licenseNotes" "text",
    "englishName" "text",
    "language" "text",
    "textDirection" "text",
    "uuid" "uuid" DEFAULT "gen_random_uuid"() NOT NULL
);


ALTER TABLE "public"."DatasetChapter" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."DatasetChapterVerse" (
    "number" integer,
    "chapterNumber" integer,
    "bookId" "text",
    "datasetId" "text",
    "contentJson" "text",
    "sha256" "text",
    "id" "text" NOT NULL,
    "name" "text",
    "website" "text",
    "licenseUrl" "text",
    "licenseNotes" "text",
    "englishName" "text",
    "language" "text",
    "textDirection" "text",
    "uuid" "uuid" DEFAULT "gen_random_uuid"() NOT NULL
);


ALTER TABLE "public"."DatasetChapterVerse" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."DatasetReference" (
    "id" integer NOT NULL,
    "datasetId" "text",
    "bookId" "text",
    "chapterNumber" integer,
    "verseNumber" integer,
    "referenceBookId" "text",
    "referenceChapter" integer,
    "referenceVerse" integer,
    "endVerseNumber" integer,
    "score" integer,
    "name" "text",
    "website" "text",
    "licenseUrl" "text",
    "licenseNotes" "text",
    "englishName" "text",
    "language" "text",
    "textDirection" "text",
    "sha256" "text",
    "uuid" "uuid" DEFAULT "gen_random_uuid"() NOT NULL
);


ALTER TABLE "public"."DatasetReference" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."Dictionary" (
    "topic" "text",
    "definition" "text",
    "lexeme" "text",
    "transliteration" "text",
    "pronunciation" "text",
    "short_definition" "text",
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "uuid" "uuid" DEFAULT "gen_random_uuid"() NOT NULL
);


ALTER TABLE "public"."Dictionary" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."Translation" (
    "id" "text" NOT NULL,
    "name" "text",
    "website" "text",
    "licenseUrl" "text",
    "shortName" "text",
    "englishName" "text",
    "language" "text",
    "textDirection" "text",
    "sha256" "text",
    "licenseNotes" "text",
    "uuid" "uuid" DEFAULT "gen_random_uuid"() NOT NULL
);


ALTER TABLE "public"."Translation" OWNER TO "postgres";


ALTER TABLE ONLY "public"."CommentaryProfile" ALTER COLUMN "uuid_old" SET DEFAULT "nextval"('"public"."CommentaryProfile_uuid_seq"'::"regclass");



ALTER TABLE ONLY "public"."CommentaryProfileContent" ALTER COLUMN "uuid_old" SET DEFAULT "nextval"('"public"."CommentaryProfileContent_uuid_seq"'::"regclass");



ALTER TABLE ONLY "public"."BibleBook"
    ADD CONSTRAINT "BibleBook_pkey" PRIMARY KEY ("uuid");



ALTER TABLE ONLY "public"."BibleChapterAudioUrl"
    ADD CONSTRAINT "BibleChapterAudioUrl_pkey" PRIMARY KEY ("uuid");



ALTER TABLE ONLY "public"."ChapterFootnote"
    ADD CONSTRAINT "ChapterFootnote_pkey" PRIMARY KEY ("uuid");



ALTER TABLE ONLY "public"."ChapterVerse"
    ADD CONSTRAINT "ChapterVerse_pkey" PRIMARY KEY ("uuid");



ALTER TABLE ONLY "public"."BibleChapter"
    ADD CONSTRAINT "Chapter_pkey" PRIMARY KEY ("uuid");



ALTER TABLE ONLY "public"."CommentaryBook"
    ADD CONSTRAINT "CommentaryBook_pkey" PRIMARY KEY ("uuid");



ALTER TABLE ONLY "public"."CommentaryChapterVerse"
    ADD CONSTRAINT "CommentaryChapterVerse_pkey" PRIMARY KEY ("uuid");



ALTER TABLE ONLY "public"."CommentaryChapter"
    ADD CONSTRAINT "CommentaryChapter_pkey" PRIMARY KEY ("uuid");



ALTER TABLE ONLY "public"."CommentaryProfileContent"
    ADD CONSTRAINT "CommentaryProfileContent_pkey" PRIMARY KEY ("uuid");



ALTER TABLE ONLY "public"."CommentaryProfile"
    ADD CONSTRAINT "CommentaryProfile_pkey" PRIMARY KEY ("uuid");



ALTER TABLE ONLY "public"."Commentary"
    ADD CONSTRAINT "Commentary_pkey" PRIMARY KEY ("uuid");



ALTER TABLE ONLY "public"."CrossReference"
    ADD CONSTRAINT "CrossReference_pkey" PRIMARY KEY ("uuid");



ALTER TABLE ONLY "public"."DatasetBook"
    ADD CONSTRAINT "DatasetBook_pkey" PRIMARY KEY ("uuid");



ALTER TABLE ONLY "public"."DatasetChapterVerse"
    ADD CONSTRAINT "DatasetChapterVerse_pkey" PRIMARY KEY ("uuid");



ALTER TABLE ONLY "public"."DatasetChapter"
    ADD CONSTRAINT "DatasetChapter_pkey" PRIMARY KEY ("uuid");



ALTER TABLE ONLY "public"."DatasetReference"
    ADD CONSTRAINT "DatasetReference_pkey" PRIMARY KEY ("uuid");



ALTER TABLE ONLY "public"."Dataset"
    ADD CONSTRAINT "Dataset_pkey" PRIMARY KEY ("uuid");



ALTER TABLE ONLY "public"."Dictionary"
    ADD CONSTRAINT "Dictionary_pkey" PRIMARY KEY ("uuid");



ALTER TABLE ONLY "public"."Translation"
    ADD CONSTRAINT "Translation_pkey" PRIMARY KEY ("uuid");



ALTER TABLE "public"."BibleBook" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."BibleChapter" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."BibleChapterAudioUrl" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."ChapterFootnote" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."ChapterVerse" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."Commentary" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."CommentaryBook" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."CommentaryChapter" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."CommentaryChapterVerse" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."CommentaryProfile" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."CommentaryProfileContent" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."CrossReference" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."Dataset" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."DatasetBook" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."DatasetChapter" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."DatasetChapterVerse" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."DatasetReference" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."Dictionary" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."Translation" ENABLE ROW LEVEL SECURITY;




ALTER PUBLICATION "supabase_realtime" OWNER TO "postgres";


GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";

























































































































































GRANT ALL ON FUNCTION "public"."rls_auto_enable"() TO "anon";
GRANT ALL ON FUNCTION "public"."rls_auto_enable"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."rls_auto_enable"() TO "service_role";


















GRANT ALL ON TABLE "public"."BibleBook" TO "anon";
GRANT ALL ON TABLE "public"."BibleBook" TO "authenticated";
GRANT ALL ON TABLE "public"."BibleBook" TO "service_role";



GRANT ALL ON TABLE "public"."BibleChapter" TO "anon";
GRANT ALL ON TABLE "public"."BibleChapter" TO "authenticated";
GRANT ALL ON TABLE "public"."BibleChapter" TO "service_role";



GRANT ALL ON TABLE "public"."BibleChapterAudioUrl" TO "anon";
GRANT ALL ON TABLE "public"."BibleChapterAudioUrl" TO "authenticated";
GRANT ALL ON TABLE "public"."BibleChapterAudioUrl" TO "service_role";



GRANT ALL ON TABLE "public"."ChapterFootnote" TO "anon";
GRANT ALL ON TABLE "public"."ChapterFootnote" TO "authenticated";
GRANT ALL ON TABLE "public"."ChapterFootnote" TO "service_role";



GRANT ALL ON TABLE "public"."ChapterVerse" TO "anon";
GRANT ALL ON TABLE "public"."ChapterVerse" TO "authenticated";
GRANT ALL ON TABLE "public"."ChapterVerse" TO "service_role";



GRANT ALL ON TABLE "public"."Commentary" TO "anon";
GRANT ALL ON TABLE "public"."Commentary" TO "authenticated";
GRANT ALL ON TABLE "public"."Commentary" TO "service_role";



GRANT ALL ON TABLE "public"."CommentaryBook" TO "anon";
GRANT ALL ON TABLE "public"."CommentaryBook" TO "authenticated";
GRANT ALL ON TABLE "public"."CommentaryBook" TO "service_role";



GRANT ALL ON TABLE "public"."CommentaryChapter" TO "anon";
GRANT ALL ON TABLE "public"."CommentaryChapter" TO "authenticated";
GRANT ALL ON TABLE "public"."CommentaryChapter" TO "service_role";



GRANT ALL ON TABLE "public"."CommentaryChapterVerse" TO "anon";
GRANT ALL ON TABLE "public"."CommentaryChapterVerse" TO "authenticated";
GRANT ALL ON TABLE "public"."CommentaryChapterVerse" TO "service_role";



GRANT ALL ON TABLE "public"."CommentaryProfile" TO "anon";
GRANT ALL ON TABLE "public"."CommentaryProfile" TO "authenticated";
GRANT ALL ON TABLE "public"."CommentaryProfile" TO "service_role";



GRANT ALL ON TABLE "public"."CommentaryProfileContent" TO "anon";
GRANT ALL ON TABLE "public"."CommentaryProfileContent" TO "authenticated";
GRANT ALL ON TABLE "public"."CommentaryProfileContent" TO "service_role";



GRANT ALL ON SEQUENCE "public"."CommentaryProfileContent_uuid_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."CommentaryProfileContent_uuid_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."CommentaryProfileContent_uuid_seq" TO "service_role";



GRANT ALL ON SEQUENCE "public"."CommentaryProfile_uuid_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."CommentaryProfile_uuid_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."CommentaryProfile_uuid_seq" TO "service_role";



GRANT ALL ON TABLE "public"."CrossReference" TO "anon";
GRANT ALL ON TABLE "public"."CrossReference" TO "authenticated";
GRANT ALL ON TABLE "public"."CrossReference" TO "service_role";



GRANT ALL ON TABLE "public"."Dataset" TO "anon";
GRANT ALL ON TABLE "public"."Dataset" TO "authenticated";
GRANT ALL ON TABLE "public"."Dataset" TO "service_role";



GRANT ALL ON TABLE "public"."DatasetBook" TO "anon";
GRANT ALL ON TABLE "public"."DatasetBook" TO "authenticated";
GRANT ALL ON TABLE "public"."DatasetBook" TO "service_role";



GRANT ALL ON TABLE "public"."DatasetChapter" TO "anon";
GRANT ALL ON TABLE "public"."DatasetChapter" TO "authenticated";
GRANT ALL ON TABLE "public"."DatasetChapter" TO "service_role";



GRANT ALL ON TABLE "public"."DatasetChapterVerse" TO "anon";
GRANT ALL ON TABLE "public"."DatasetChapterVerse" TO "authenticated";
GRANT ALL ON TABLE "public"."DatasetChapterVerse" TO "service_role";



GRANT ALL ON TABLE "public"."DatasetReference" TO "anon";
GRANT ALL ON TABLE "public"."DatasetReference" TO "authenticated";
GRANT ALL ON TABLE "public"."DatasetReference" TO "service_role";



GRANT ALL ON TABLE "public"."Dictionary" TO "anon";
GRANT ALL ON TABLE "public"."Dictionary" TO "authenticated";
GRANT ALL ON TABLE "public"."Dictionary" TO "service_role";



GRANT ALL ON TABLE "public"."Translation" TO "anon";
GRANT ALL ON TABLE "public"."Translation" TO "authenticated";
GRANT ALL ON TABLE "public"."Translation" TO "service_role";









ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "service_role";



































drop extension if exists "pg_net";


