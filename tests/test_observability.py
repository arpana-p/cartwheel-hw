from __future__ import annotations

import pytest
from fastapi import HTTPException

from server import app as server_app


@pytest.fixture(autouse=True)
def clear_sessions() -> None:
    server_app._SESSIONS.clear()


def test_create_session_rejects_role_mismatch(world: dict) -> None:
    with pytest.raises(HTTPException) as exc_info:
        server_app.create_session(
            server_app.SessionCreate(user_id=1, role="merchant")
        )

    assert exc_info.value.status_code == 403
    assert server_app._SESSIONS == {}


def test_token_cannot_authorize_another_session(world: dict) -> None:
    first = server_app.create_session(
        server_app.SessionCreate(user_id=1, role="shopper")
    )
    second = server_app.create_session(
        server_app.SessionCreate(user_id=2, role="shopper")
    )

    with pytest.raises(HTTPException) as exc_info:
        server_app._authorize(
            second["session_id"],
            f"Bearer {first['token']}",
        )

    assert exc_info.value.status_code == 403
