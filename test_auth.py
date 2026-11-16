from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from repomind_api.auth import verify_cognito_user
from repomind_api.config import Settings


def test_verify_cognito_user_accepts_access_token_client_id(monkeypatch: pytest.MonkeyPatch) -> None:
    # Given: Cognito returned access-token claims with client_id instead of aud.
    import jwt

    claims = {
        "client_id": "client-one",
        "custom:public_tag": "SCNU_20224254",
        "name": "Gayeon",
        "sub": "user-sub",
    }

    class FakeJwksClient:
        def __init__(self, url: str) -> None:
            self.url = url

        def get_signing_key_from_jwt(self, token: str) -> SimpleNamespace:
            return SimpleNamespace(key="public-key")

    def fake_decode(
        token: str,
        key: str,
        algorithms: list[str],
        issuer: str,
        options: dict[str, bool],
    ) -> dict[str, str]:
        assert token == "token"
        assert key == "public-key"
        assert algorithms == ["RS256"]
        assert issuer == "https://cognito-idp.ap-south-1.amazonaws.com/ap-south-1_pool"
        assert options == {"verify_aud": False}
        return claims

    monkeypatch.setattr(jwt, "PyJWKClient", FakeJwksClient)
    monkeypatch.setattr(jwt, "decode", fake_decode)

    # When: the backend verifies the frontend access token.
    user = verify_cognito_user("token", cognito_settings())

    # Then: client_id satisfies the configured Cognito audience.
    assert user.subject == "user-sub"
    assert user.public_tag == "SCNU_20224254"
    assert user.display_name == "Gayeon"


def test_verify_cognito_user_rejects_wrong_access_token_client_id(monkeypatch: pytest.MonkeyPatch) -> None:
    # Given: Cognito returned an access token for another app client.
    import jwt

    class FakeJwksClient:
        def __init__(self, url: str) -> None:
            self.url = url

        def get_signing_key_from_jwt(self, token: str) -> SimpleNamespace:
            return SimpleNamespace(key="public-key")

    def fake_decode(
        token: str,
        key: str,
        algorithms: list[str],
        issuer: str,
        options: dict[str, bool],
    ) -> dict[str, str]:
        assert token == "token"
        assert key == "public-key"
        assert algorithms == ["RS256"]
        assert issuer == "https://cognito-idp.ap-south-1.amazonaws.com/ap-south-1_pool"
        assert options == {"verify_aud": False}
        return {"client_id": "other-client", "sub": "user-sub"}

    monkeypatch.setattr(jwt, "PyJWKClient", FakeJwksClient)
    monkeypatch.setattr(jwt, "decode", fake_decode)

    # When / Then: the backend rejects the mismatched client id as an auth error.
    with pytest.raises(HTTPException) as exc_info:
        verify_cognito_user("token", cognito_settings())

    assert exc_info.value.status_code == 401


def cognito_settings() -> Settings:
    return Settings(
        auth_mode="cognito",
        cognito_audience="client-one",
        cognito_region="ap-south-1",
        cognito_user_pool_id="ap-south-1_pool",
    )
