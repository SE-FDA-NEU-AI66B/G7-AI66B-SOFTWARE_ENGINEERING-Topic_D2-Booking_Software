"""Profiles: list the account's profiles, select one, read the active one."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import (
    get_conn,
    get_current_account,
    get_current_profile,
    profile_belongs_to_account,
)

router = APIRouter(prefix="/api/v1/profiles", tags=["profiles"])


class SelectRequest(BaseModel):
    profile_id: int | None = None


@router.get("")
def list_profiles(account_id: int = Depends(get_current_account)):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT id, name, avatar_color FROM profile WHERE account_id = ? ORDER BY id",
            (account_id,),
        ).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]


@router.post("/select")
def select_profile(body: SelectRequest, account_id: int = Depends(get_current_account)):
    if body.profile_id is None:
        raise HTTPException(status_code=400, detail="Choose a profile.")
    conn = get_conn()
    try:
        if not profile_belongs_to_account(conn, account_id, body.profile_id):
            raise HTTPException(
                status_code=404, detail="Profile not found in this account."
            )
        row = conn.execute(
            "SELECT id, name, avatar_color FROM profile WHERE id = ?",
            (body.profile_id,),
        ).fetchone()
    finally:
        conn.close()
    return dict(row)


@router.get("/me")
def current_profile(profile_id: int = Depends(get_current_profile)):
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT id, name, avatar_color FROM profile WHERE id = ?", (profile_id,)
        ).fetchone()
    finally:
        conn.close()
    return dict(row)