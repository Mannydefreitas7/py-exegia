"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
	# -----------------------------------------------------------------------
	# Translations
	# -----------------------------------------------------------------------
	op.create_table(
		"translations",
		sa.Column("id", sa.String(50), primary_key=True),
		sa.Column("name", sa.String(255), nullable=False),
		sa.Column("english_name", sa.String(255), nullable=False),
		sa.Column("website", sa.Text(), nullable=True),
		sa.Column("license_url", sa.Text(), nullable=True),
		sa.Column("short_name", sa.String(50), nullable=True),
		sa.Column("language", sa.String(10), nullable=False),
		sa.Column("language_name", sa.String(100), nullable=False),
		sa.Column("language_english_name", sa.String(100), nullable=False),
		sa.Column("text_direction", sa.String(10), nullable=False, server_default="ltr"),
		sa.Column("available_formats", postgresql.JSONB(), nullable=True),
		sa.Column("number_of_books", sa.Integer(), nullable=False, server_default="0"),
		sa.Column("total_chapters", sa.Integer(), nullable=False, server_default="0"),
		sa.Column("total_verses", sa.Integer(), nullable=False, server_default="0"),
	)

	op.create_table(
		"books",
		sa.Column("id", sa.String(100), primary_key=True),
		sa.Column(
			"translation_id",
			sa.String(50),
			sa.ForeignKey("translations.id", ondelete="CASCADE"),
			nullable=False,
		),
		sa.Column("name", sa.String(255), nullable=False),
		sa.Column("common_name", sa.String(255), nullable=False),
		sa.Column("title", sa.String(255), nullable=True),
		sa.Column("order", sa.Integer(), nullable=False),
		sa.Column("number_of_chapters", sa.Integer(), nullable=False, server_default="0"),
		sa.Column("first_chapter_number", sa.Integer(), nullable=False, server_default="1"),
		sa.Column("last_chapter_number", sa.Integer(), nullable=False, server_default="1"),
		sa.Column("total_verses", sa.Integer(), nullable=False, server_default="0"),
		sa.Column("is_apocryphal", sa.Boolean(), nullable=False, server_default="false"),
	)
	op.create_index("ix_books_translation_id", "books", ["translation_id"])

	op.create_table(
		"chapters",
		sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
		sa.Column(
			"book_id",
			sa.String(100),
			sa.ForeignKey("books.id", ondelete="CASCADE"),
			nullable=False,
		),
		sa.Column(
			"translation_id",
			sa.String(50),
			sa.ForeignKey("translations.id", ondelete="CASCADE"),
			nullable=False,
		),
		sa.Column("chapter_number", sa.Integer(), nullable=False),
		sa.Column("number_of_verses", sa.Integer(), nullable=False, server_default="0"),
		sa.Column("content", postgresql.JSONB(), nullable=True),
		sa.Column("audio_links", postgresql.JSONB(), nullable=True),
	)
	op.create_index("ix_chapters_book_id", "chapters", ["book_id"])
	op.create_index("ix_chapters_translation_id", "chapters", ["translation_id"])

	# -----------------------------------------------------------------------
	# Commentaries
	# -----------------------------------------------------------------------
	op.create_table(
		"commentaries",
		sa.Column("id", sa.String(50), primary_key=True),
		sa.Column("name", sa.String(255), nullable=False),
		sa.Column("english_name", sa.String(255), nullable=False),
		sa.Column("website", sa.Text(), nullable=True),
		sa.Column("license_url", sa.Text(), nullable=True),
		sa.Column("short_name", sa.String(50), nullable=True),
		sa.Column("language", sa.String(10), nullable=False),
		sa.Column("language_name", sa.String(100), nullable=False),
		sa.Column("language_english_name", sa.String(100), nullable=False),
		sa.Column("text_direction", sa.String(10), nullable=False, server_default="ltr"),
		sa.Column("introduction", sa.Text(), nullable=True),
		sa.Column("number_of_books", sa.Integer(), nullable=False, server_default="0"),
		sa.Column("total_chapters", sa.Integer(), nullable=False, server_default="0"),
	)

	op.create_table(
		"commentary_books",
		sa.Column("id", sa.String(100), primary_key=True),
		sa.Column(
			"commentary_id",
			sa.String(50),
			sa.ForeignKey("commentaries.id", ondelete="CASCADE"),
			nullable=False,
		),
		sa.Column("name", sa.String(255), nullable=False),
		sa.Column("common_name", sa.String(255), nullable=False),
		sa.Column("title", sa.String(255), nullable=True),
		sa.Column("order", sa.Integer(), nullable=False),
		sa.Column("number_of_chapters", sa.Integer(), nullable=False, server_default="0"),
		sa.Column("first_chapter_number", sa.Integer(), nullable=False, server_default="1"),
		sa.Column("last_chapter_number", sa.Integer(), nullable=False, server_default="1"),
		sa.Column("is_apocryphal", sa.Boolean(), nullable=False, server_default="false"),
	)
	op.create_index("ix_commentary_books_commentary_id", "commentary_books", ["commentary_id"])

	op.create_table(
		"commentary_chapters",
		sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
		sa.Column(
			"book_id",
			sa.String(100),
			sa.ForeignKey("commentary_books.id", ondelete="CASCADE"),
			nullable=False,
		),
		sa.Column(
			"commentary_id",
			sa.String(50),
			sa.ForeignKey("commentaries.id", ondelete="CASCADE"),
			nullable=False,
		),
		sa.Column("chapter_number", sa.Integer(), nullable=False),
		sa.Column("content", postgresql.JSONB(), nullable=True),
	)
	op.create_index("ix_commentary_chapters_book_id", "commentary_chapters", ["book_id"])
	op.create_index(
		"ix_commentary_chapters_commentary_id", "commentary_chapters", ["commentary_id"]
	)

	op.create_table(
		"commentary_profiles",
		sa.Column("id", sa.String(100), primary_key=True),
		sa.Column(
			"commentary_id",
			sa.String(50),
			sa.ForeignKey("commentaries.id", ondelete="CASCADE"),
			nullable=False,
		),
		sa.Column("name", sa.String(255), nullable=False),
		sa.Column("introduction", sa.Text(), nullable=True),
		sa.Column("content", postgresql.JSONB(), nullable=True),
	)
	op.create_index(
		"ix_commentary_profiles_commentary_id", "commentary_profiles", ["commentary_id"]
	)

	# -----------------------------------------------------------------------
	# Datasets
	# -----------------------------------------------------------------------
	op.create_table(
		"datasets",
		sa.Column("id", sa.String(50), primary_key=True),
		sa.Column("name", sa.String(255), nullable=False),
		sa.Column("english_name", sa.String(255), nullable=False),
		sa.Column("website", sa.Text(), nullable=True),
		sa.Column("license_url", sa.Text(), nullable=True),
		sa.Column("short_name", sa.String(50), nullable=True),
		sa.Column("language", sa.String(10), nullable=False),
		sa.Column("language_name", sa.String(100), nullable=False),
		sa.Column("language_english_name", sa.String(100), nullable=False),
		sa.Column("text_direction", sa.String(10), nullable=False, server_default="ltr"),
		sa.Column("number_of_books", sa.Integer(), nullable=False, server_default="0"),
		sa.Column("total_chapters", sa.Integer(), nullable=False, server_default="0"),
	)

	op.create_table(
		"dataset_books",
		sa.Column("id", sa.String(100), primary_key=True),
		sa.Column(
			"dataset_id",
			sa.String(50),
			sa.ForeignKey("datasets.id", ondelete="CASCADE"),
			nullable=False,
		),
		sa.Column("name", sa.String(255), nullable=False),
		sa.Column("common_name", sa.String(255), nullable=False),
		sa.Column("title", sa.String(255), nullable=True),
		sa.Column("order", sa.Integer(), nullable=False),
		sa.Column("number_of_chapters", sa.Integer(), nullable=False, server_default="0"),
		sa.Column("first_chapter_number", sa.Integer(), nullable=False, server_default="1"),
		sa.Column("last_chapter_number", sa.Integer(), nullable=False, server_default="1"),
		sa.Column("is_apocryphal", sa.Boolean(), nullable=False, server_default="false"),
	)
	op.create_index("ix_dataset_books_dataset_id", "dataset_books", ["dataset_id"])

	op.create_table(
		"dataset_chapters",
		sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
		sa.Column(
			"book_id",
			sa.String(100),
			sa.ForeignKey("dataset_books.id", ondelete="CASCADE"),
			nullable=False,
		),
		sa.Column(
			"dataset_id",
			sa.String(50),
			sa.ForeignKey("datasets.id", ondelete="CASCADE"),
			nullable=False,
		),
		sa.Column("chapter_number", sa.Integer(), nullable=False),
		sa.Column("content", postgresql.JSONB(), nullable=True),
	)
	op.create_index("ix_dataset_chapters_book_id", "dataset_chapters", ["book_id"])
	op.create_index("ix_dataset_chapters_dataset_id", "dataset_chapters", ["dataset_id"])


def downgrade() -> None:
	op.drop_index("ix_dataset_chapters_dataset_id", table_name="dataset_chapters")
	op.drop_index("ix_dataset_chapters_book_id", table_name="dataset_chapters")
	op.drop_table("dataset_chapters")
	op.drop_index("ix_dataset_books_dataset_id", table_name="dataset_books")
	op.drop_table("dataset_books")
	op.drop_table("datasets")

	op.drop_index("ix_commentary_profiles_commentary_id", table_name="commentary_profiles")
	op.drop_table("commentary_profiles")
	op.drop_index("ix_commentary_chapters_commentary_id", table_name="commentary_chapters")
	op.drop_index("ix_commentary_chapters_book_id", table_name="commentary_chapters")
	op.drop_table("commentary_chapters")
	op.drop_index("ix_commentary_books_commentary_id", table_name="commentary_books")
	op.drop_table("commentary_books")
	op.drop_table("commentaries")

	op.drop_index("ix_chapters_translation_id", table_name="chapters")
	op.drop_index("ix_chapters_book_id", table_name="chapters")
	op.drop_table("chapters")
	op.drop_index("ix_books_translation_id", table_name="books")
	op.drop_table("books")
	op.drop_table("translations")
