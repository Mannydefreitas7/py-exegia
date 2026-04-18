-- Extend book_category enum with religious-text categories not covered by the initial set.
alter type public.book_category add value if not exists 'quran';
alter type public.book_category add value if not exists 'tanakh';
