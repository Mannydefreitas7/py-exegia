import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

import strawberry

from exegia_graphql.types.user import (
    Comment,
    CommentsList,
    CommentsFilterInput,
    CreateCommentInput,
    CreateFavoriteInput,
    CreateNoteInput,
    DeleteCommentInput,
    DeleteFavoriteInput,
    DeleteNoteInput,
    Favorite,
    FavoritesList,
    FavoritesFilterInput,
    Note,
    NotesList,
    NotesFilterInput,
    UpdateCommentInput,
    UpdateNoteInput,
    UpdateUserProfileInput,
    User,
    UserDataset,
    UserDatasetsList,
)

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _get_supabase(info: strawberry.Info):
    """Return a Supabase client with the request's bearer token, or None."""
    from src.config import settings
    if not settings.supabase_url or not settings.supabase_anon_key:
        return None

    try:
        request = info.context["request"]
        auth_header = request.headers.get("authorization", "")
        token = auth_header.removeprefix("Bearer ").strip()
        if not token:
            return None

        from supabase import create_client
        client = create_client(settings.supabase_url, settings.supabase_anon_key)
        client.auth.set_session(token, "")
        return client
    except Exception as e:
        logger.debug("Could not build Supabase client: %s", e)
        return None


async def resolve_my_profile(info: strawberry.Info) -> Optional[User]:
    client = _get_supabase(info)
    if client is None:
        return None
    try:
        user = client.auth.get_user()
        if not user or not user.user:
            return None
        u = user.user
        now = _now()
        return User(
            id=UUID(u.id),
            email=u.email or "",
            display_name=u.user_metadata.get("display_name") if u.user_metadata else None,
            created_at=u.created_at or now,
            updated_at=u.updated_at or now,
        )
    except Exception as e:
        logger.debug("resolve_my_profile error: %s", e)
        return None


async def resolve_my_notes(
    info: strawberry.Info,
    filters: Optional[NotesFilterInput],
    limit: int,
    offset: int,
) -> NotesList:
    client = _get_supabase(info)
    if client is None:
        return NotesList(notes=[], total=0)
    try:
        query = client.table("notes").select("*")
        if filters:
            if filters.dataset_id:
                query = query.eq("dataset_id", filters.dataset_id)
            if filters.reference:
                query = query.eq("reference", filters.reference)
            if filters.search:
                query = query.ilike("content", f"%{filters.search}%")
        result = query.range(offset, offset + limit - 1).execute()
        notes = [
            Note(
                id=UUID(r["id"]),
                user_id=UUID(r["user_id"]),
                dataset_id=r["dataset_id"],
                reference=r["reference"],
                content=r["content"],
                tags=r.get("tags"),
                created_at=r["created_at"],
                updated_at=r["updated_at"],
            )
            for r in (result.data or [])
        ]
        return NotesList(notes=notes, total=len(notes))
    except Exception as e:
        logger.error("resolve_my_notes error: %s", e)
        return NotesList(notes=[], total=0)


async def resolve_my_favorites(
    info: strawberry.Info,
    filters: Optional[FavoritesFilterInput],
    limit: int,
    offset: int,
) -> FavoritesList:
    client = _get_supabase(info)
    if client is None:
        return FavoritesList(favorites=[], total=0)
    try:
        query = client.table("favorites").select("*")
        if filters:
            if filters.dataset_id:
                query = query.eq("dataset_id", filters.dataset_id)
            if filters.reference:
                query = query.eq("reference", filters.reference)
        result = query.range(offset, offset + limit - 1).execute()
        favorites = [
            Favorite(
                id=UUID(r["id"]),
                user_id=UUID(r["user_id"]),
                dataset_id=r["dataset_id"],
                reference=r["reference"],
                created_at=r["created_at"],
            )
            for r in (result.data or [])
        ]
        return FavoritesList(favorites=favorites, total=len(favorites))
    except Exception as e:
        logger.error("resolve_my_favorites error: %s", e)
        return FavoritesList(favorites=[], total=0)


async def resolve_my_comments(
    info: strawberry.Info,
    filters: Optional[CommentsFilterInput],
    limit: int,
    offset: int,
) -> CommentsList:
    client = _get_supabase(info)
    if client is None:
        return CommentsList(comments=[], total=0)
    try:
        query = client.table("comments").select("*")
        if filters:
            if filters.dataset_id:
                query = query.eq("dataset_id", filters.dataset_id)
            if filters.reference:
                query = query.eq("reference", filters.reference)
            if filters.parent_id:
                query = query.eq("parent_id", str(filters.parent_id))
        result = query.range(offset, offset + limit - 1).execute()
        comments = [
            Comment(
                id=UUID(r["id"]),
                user_id=UUID(r["user_id"]),
                dataset_id=r["dataset_id"],
                reference=r["reference"],
                content=r["content"],
                parent_id=UUID(r["parent_id"]) if r.get("parent_id") else None,
                created_at=r["created_at"],
                updated_at=r["updated_at"],
            )
            for r in (result.data or [])
        ]
        return CommentsList(comments=comments, total=len(comments))
    except Exception as e:
        logger.error("resolve_my_comments error: %s", e)
        return CommentsList(comments=[], total=0)


async def resolve_my_datasets(info: strawberry.Info) -> UserDatasetsList:
    client = _get_supabase(info)
    if client is None:
        return UserDatasetsList(datasets=[], total=0)
    try:
        result = client.table("user_datasets").select("*").execute()
        datasets = [
            UserDataset(
                id=UUID(r["id"]),
                user_id=UUID(r["user_id"]),
                dataset_id=r["dataset_id"],
                category=r["dataset_type"],
                local_path=r.get("local_path"),
                downloaded_at=r["downloaded_at"],
                last_accessed=r.get("last_accessed"),
            )
            for r in (result.data or [])
        ]
        return UserDatasetsList(datasets=datasets, total=len(datasets))
    except Exception as e:
        logger.error("resolve_my_datasets error: %s", e)
        return UserDatasetsList(datasets=[], total=0)


async def resolve_update_profile(
    info: strawberry.Info, input: UpdateUserProfileInput
) -> User:
    client = _get_supabase(info)
    if client is None:
        raise ValueError("Authentication required")
    try:
        result = client.auth.update_user({"data": {"display_name": input.display_name}})
        u = result.user
        now = _now()
        return User(
            id=UUID(u.id),
            email=u.email or "",
            display_name=input.display_name,
            created_at=u.created_at or now,
            updated_at=now,
        )
    except Exception as e:
        logger.error("resolve_update_profile error: %s", e)
        raise


async def resolve_create_note(info: strawberry.Info, input: CreateNoteInput) -> Note:
    client = _get_supabase(info)
    if client is None:
        raise ValueError("Authentication required")
    try:
        now = _now()
        result = client.table("notes").insert({
            "dataset_id": input.dataset_id,
            "reference": input.reference,
            "content": input.content,
            "tags": input.tags,
        }).execute()
        r = result.data[0]
        return Note(
            id=UUID(r["id"]),
            user_id=UUID(r["user_id"]),
            dataset_id=r["dataset_id"],
            reference=r["reference"],
            content=r["content"],
            tags=r.get("tags"),
            created_at=r.get("created_at", now),
            updated_at=r.get("updated_at", now),
        )
    except Exception as e:
        logger.error("resolve_create_note error: %s", e)
        raise


async def resolve_update_note(info: strawberry.Info, input: UpdateNoteInput) -> Note:
    client = _get_supabase(info)
    if client is None:
        raise ValueError("Authentication required")
    try:
        updates = {}
        if input.content is not None:
            updates["content"] = input.content
        if input.tags is not None:
            updates["tags"] = input.tags
        result = client.table("notes").update(updates).eq("id", str(input.id)).execute()
        r = result.data[0]
        now = _now()
        return Note(
            id=UUID(r["id"]),
            user_id=UUID(r["user_id"]),
            dataset_id=r["dataset_id"],
            reference=r["reference"],
            content=r["content"],
            tags=r.get("tags"),
            created_at=r.get("created_at", now),
            updated_at=r.get("updated_at", now),
        )
    except Exception as e:
        logger.error("resolve_update_note error: %s", e)
        raise


async def resolve_delete_note(info: strawberry.Info, input: DeleteNoteInput) -> bool:
    client = _get_supabase(info)
    if client is None:
        raise ValueError("Authentication required")
    try:
        client.table("notes").delete().eq("id", str(input.id)).execute()
        return True
    except Exception as e:
        logger.error("resolve_delete_note error: %s", e)
        return False


async def resolve_create_favorite(
    info: strawberry.Info, input: CreateFavoriteInput
) -> Favorite:
    client = _get_supabase(info)
    if client is None:
        raise ValueError("Authentication required")
    try:
        now = _now()
        result = client.table("favorites").insert({
            "dataset_id": input.dataset_id,
            "reference": input.reference,
        }).execute()
        r = result.data[0]
        return Favorite(
            id=UUID(r["id"]),
            user_id=UUID(r["user_id"]),
            dataset_id=r["dataset_id"],
            reference=r["reference"],
            created_at=r.get("created_at", now),
        )
    except Exception as e:
        logger.error("resolve_create_favorite error: %s", e)
        raise


async def resolve_delete_favorite(
    info: strawberry.Info, input: DeleteFavoriteInput
) -> bool:
    client = _get_supabase(info)
    if client is None:
        raise ValueError("Authentication required")
    try:
        client.table("favorites").delete().eq("id", str(input.id)).execute()
        return True
    except Exception as e:
        logger.error("resolve_delete_favorite error: %s", e)
        return False


async def resolve_create_comment(
    info: strawberry.Info, input: CreateCommentInput
) -> Comment:
    client = _get_supabase(info)
    if client is None:
        raise ValueError("Authentication required")
    try:
        now = _now()
        result = client.table("comments").insert({
            "dataset_id": input.dataset_id,
            "reference": input.reference,
            "content": input.content,
            "parent_id": str(input.parent_id) if input.parent_id else None,
        }).execute()
        r = result.data[0]
        return Comment(
            id=UUID(r["id"]),
            user_id=UUID(r["user_id"]),
            dataset_id=r["dataset_id"],
            reference=r["reference"],
            content=r["content"],
            parent_id=UUID(r["parent_id"]) if r.get("parent_id") else None,
            created_at=r.get("created_at", now),
            updated_at=r.get("updated_at", now),
        )
    except Exception as e:
        logger.error("resolve_create_comment error: %s", e)
        raise


async def resolve_update_comment(
    info: strawberry.Info, input: UpdateCommentInput
) -> Comment:
    client = _get_supabase(info)
    if client is None:
        raise ValueError("Authentication required")
    try:
        now = _now()
        result = client.table("comments").update({"content": input.content}).eq("id", str(input.id)).execute()
        r = result.data[0]
        return Comment(
            id=UUID(r["id"]),
            user_id=UUID(r["user_id"]),
            dataset_id=r["dataset_id"],
            reference=r["reference"],
            content=r["content"],
            parent_id=UUID(r["parent_id"]) if r.get("parent_id") else None,
            created_at=r.get("created_at", now),
            updated_at=r.get("updated_at", now),
        )
    except Exception as e:
        logger.error("resolve_update_comment error: %s", e)
        raise


async def resolve_delete_comment(
    info: strawberry.Info, input: DeleteCommentInput
) -> bool:
    client = _get_supabase(info)
    if client is None:
        raise ValueError("Authentication required")
    try:
        client.table("comments").delete().eq("id", str(input.id)).execute()
        return True
    except Exception as e:
        logger.error("resolve_delete_comment error: %s", e)
        return False
