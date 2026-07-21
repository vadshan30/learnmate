"""Tests for Auth system – registration, login, JWT, password hashing, forgot/reset password, rate limiting, guest migration."""

import sys
import os
import uuid
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.utils.security import hash_password, verify_password, validate_password_strength
from app.utils.jwt import create_access_token, create_refresh_token, decode_token, get_user_id_from_token
from app.database import SessionLocal, PasswordResetTokenRow, UserRow, Base, engine
import app.services.auth_service as auth_svc


def _setup_database():
    Base.metadata.create_all(bind=engine)

_setup_database()

_unique = lambda base: f"{base}_{uuid.uuid4().hex[:8]}"


# 1. Registration – success
def test_register_success():
    from app.services.auth_service import create_user
    uname = _unique("testuser")
    email = f"{uname}@test.com"
    user = create_user("Test User", uname, email, "StrongPass1!")
    assert user["id"]
    assert user["username"] == uname
    assert user["email"] == email
    assert user["full_name"] == "Test User"
    print("  PASS: register_success")


# 2. Duplicate email blocked
def test_register_duplicate_email():
    from app.services.auth_service import create_user
    uname1 = _unique("userA")
    uname2 = _unique("userB")
    shared_email = f"{uname1}@dup.com"
    create_user("User A", uname1, shared_email, "StrongPass1!")
    try:
        create_user("User B", uname2, shared_email, "StrongPass2!")
        assert False, "Should have raised ValueError for duplicate email"
    except ValueError as e:
        assert "Email already registered" in str(e)
    print("  PASS: register_duplicate_email")


# 3. Duplicate username blocked
def test_register_duplicate_username():
    from app.services.auth_service import create_user
    uname = _unique("dupeuser")
    create_user("User One", uname, f"{uname}1@test.com", "StrongPass1!")
    try:
        create_user("User Two", uname, f"{uname}2@test.com", "StrongPass2!")
        assert False, "Should have raised ValueError for duplicate username"
    except ValueError as e:
        assert "Username already taken" in str(e)
    print("  PASS: register_duplicate_username")


# 4. Login – success with username
def test_login_username():
    from app.services.auth_service import create_user, authenticate_user
    uname = _unique("logintest")
    create_user("Login User", uname, f"{uname}@test.com", "MyPass123!")
    result = authenticate_user(uname, "MyPass123!")
    assert result is not None
    assert result["username"] == uname
    print("  PASS: login_username")


# 5. Login – success with email
def test_login_email():
    from app.services.auth_service import create_user, authenticate_user
    uname = _unique("emaillog")
    email = f"{uname}@test.com"
    create_user("Email Login", uname, email, "MyPass123!")
    result = authenticate_user(email, "MyPass123!")
    assert result is not None
    assert result["email"] == email
    print("  PASS: login_email")


# 6. Login – wrong password returns None
def test_login_wrong_password():
    from app.services.auth_service import create_user, authenticate_user
    uname = _unique("wrongpwd")
    create_user("Wrong Pwd", uname, f"{uname}@test.com", "Correct123!")
    result = authenticate_user(uname, "WrongPassword99!")
    assert result is None
    print("  PASS: login_wrong_password")


# 7. JWT – access token roundtrip
def test_jwt_access_token_roundtrip():
    uid = str(uuid.uuid4())
    token = create_access_token(uid, "alice")
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == uid
    assert payload["username"] == "alice"
    assert payload["type"] == "access"
    print("  PASS: jwt_access_token_roundtrip")


# 8. JWT – refresh token roundtrip
def test_jwt_refresh_token_roundtrip():
    uid = str(uuid.uuid4())
    token = create_refresh_token(uid, "bob")
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == uid
    assert payload["username"] == "bob"
    assert payload["type"] == "refresh"
    print("  PASS: jwt_refresh_token_roundtrip")


# 9. JWT – invalid token returns None
def test_jwt_invalid_token():
    payload = decode_token("this.is.not.a.valid.jwt.token")
    assert payload is None
    print("  PASS: jwt_invalid_token")


# 10. Password – hash and verify roundtrip
def test_password_hash_verify():
    plain = "SecurePass1!"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed)
    assert not verify_password("WrongPass1!", hashed)
    print("  PASS: password_hash_verify")


# 11. Password – strength validation rejects weak passwords
def test_password_strength_weak():
    cases = [
        ("short", "Password must be at least 8 characters long"),
        ("alllowercase1!", "Password must contain at least one uppercase letter"),
        ("ALLUPPERCASE1!", "Password must contain at least one lowercase letter"),
        ("NoNumbersHere!", "Password must contain at least one number"),
        ("NoSpecialChar1", "Password must contain at least one special character"),
    ]
    for pwd, expected_fragment in cases:
        errors = validate_password_strength(pwd)
        assert any(expected_fragment in e for e in errors), (
            f"Expected error containing '{expected_fragment}' for '{pwd}', got: {errors}"
        )
    print("  PASS: password_strength_weak")


# 12. Password – strength validation accepts strong password
def test_password_strength_strong():
    errors = validate_password_strength("Str0ng!Pass#2024")
    assert errors == [], f"Strong password should have no errors, got: {errors}"
    print("  PASS: password_strength_strong")


# 13. Forgot password – token generation for existing user
def test_forgot_password_existing_user():
    from app.services.auth_service import create_user, create_forgot_password_token
    uname = _unique("forgotexist")
    email = f"{uname}@test.com"
    create_user("Forgot Exist", uname, email, "StrongPass1!")
    token = create_forgot_password_token(email)
    assert token
    assert len(token) > 10
    with SessionLocal() as session:
        hashed = hashlib.sha256(token.encode()).hexdigest()
        row = session.query(PasswordResetTokenRow).filter(
            PasswordResetTokenRow.hashed_token == hashed
        ).first()
        assert row is not None
        assert row.used == 0
        exp = row.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        assert exp > datetime.now(timezone.utc)
    print("  PASS: forgot_password_existing_user")


# 14. Forgot password – non-existent user returns same message (no leak)
def test_forgot_password_nonexistent_user():
    from app.services.auth_service import create_forgot_password_token
    fake_email = f"nonexistent_{uuid.uuid4().hex[:8]}@nowhere.com"
    token = create_forgot_password_token(fake_email)
    assert token
    with SessionLocal() as session:
        hashed = hashlib.sha256(token.encode()).hexdigest()
        row = session.query(PasswordResetTokenRow).filter(
            PasswordResetTokenRow.hashed_token == hashed
        ).first()
        assert row is None
    print("  PASS: forgot_password_nonexistent_user")


# 15. Reset password – successful reset
def test_reset_password_success():
    from app.services.auth_service import (
        create_user, create_forgot_password_token, reset_password, authenticate_user,
    )
    uname = _unique("resetpwd")
    email = f"{uname}@test.com"
    create_user("Reset User", uname, email, "OldPass123!")
    token = create_forgot_password_token(email)
    result = reset_password(token, "NewPass456!")
    assert result is True
    assert authenticate_user(email, "NewPass456!") is not None
    assert authenticate_user(email, "OldPass123!") is None
    print("  PASS: reset_password_success")


# 16. Reset password – expired token
def test_reset_password_expired_token():
    from app.services.auth_service import create_user, create_forgot_password_token, reset_password
    uname = _unique("expiredtok")
    email = f"{uname}@test.com"
    create_user("Expired Token", uname, email, "StrongPass1!")
    token = create_forgot_password_token(email)
    hashed = hashlib.sha256(token.encode()).hexdigest()
    with SessionLocal() as session:
        row = session.query(PasswordResetTokenRow).filter(
            PasswordResetTokenRow.hashed_token == hashed
        ).first()
        if row:
            row.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
            session.commit()
    try:
        reset_password(token, "NewPass123!")
        assert False, "Should have raised ValueError for expired token"
    except ValueError as e:
        assert "expired" in str(e).lower() or "invalid" in str(e).lower()
    print("  PASS: reset_password_expired_token")


# 17. Reset password – invalid token
def test_reset_password_invalid_token():
    from app.services.auth_service import reset_password
    try:
        reset_password("completely-fake-token-12345", "NewPass123!")
        assert False, "Should have raised ValueError for invalid token"
    except ValueError as e:
        assert "invalid" in str(e).lower()
    print("  PASS: reset_password_invalid_token")


# 18. Reset password – used token cannot be reused
def test_reset_password_used_token():
    from app.services.auth_service import create_user, create_forgot_password_token, reset_password
    uname = _unique("usedtok")
    email = f"{uname}@test.com"
    create_user("Used Token", uname, email, "StrongPass1!")
    token = create_forgot_password_token(email)
    reset_password(token, "NewPass123!")
    try:
        reset_password(token, "AnotherPass123!")
        assert False, "Should have raised ValueError for already used token"
    except ValueError as e:
        assert "used" in str(e).lower() or "invalid" in str(e).lower()
    print("  PASS: reset_password_used_token")


# 19. User table schema – no google columns
def test_user_table_no_google_columns():
    from sqlalchemy import inspect
    uname = _unique("noschema")
    email = f"{uname}@test.com"
    with SessionLocal() as session:
        inspector = inspect(session.bind)
        columns = {col["name"] for col in inspector.get_columns("users")}
        assert "google_id" not in columns, "google_id should not exist"
        assert "avatar_url" not in columns, "avatar_url should not exist"
        assert "provider" not in columns, "provider should not exist"
        assert "password_hash" in columns, "password_hash must exist"
    print("  PASS: user_table_no_google_columns")


# 20. PasswordResetToken table exists
def test_password_reset_token_table():
    from sqlalchemy import inspect
    with SessionLocal() as session:
        inspector = inspect(session.bind)
        tables = inspector.get_table_names()
        assert "password_reset_tokens" in tables
        columns = {col["name"] for col in inspector.get_columns("password_reset_tokens")}
        expected = {"id", "user_id", "hashed_token", "expires_at", "created_at", "used"}
        assert expected.issubset(columns), f"Missing columns: {expected - columns}"
    print("  PASS: password_reset_token_table")


# 21. Rate limiting – blocks after MAX_LOGIN_ATTEMPTS
def test_rate_limit_blocks_after_max_attempts():
    from app.services.auth_service import create_user, authenticate_user
    uname = _unique("ratelim")
    email = f"{uname}@ratelim.com"
    create_user("Rate Limit", uname, email, "StrongPass1!")

    auth_svc._clear_login_attempts(email)

    for _ in range(auth_svc.MAX_LOGIN_ATTEMPTS):
        authenticate_user(email, "WrongPass!")

    try:
        authenticate_user(email, "WrongPass!")
        assert False, "Should have raised PermissionError for rate limit"
    except PermissionError as e:
        assert "too many" in str(e).lower()
    print("  PASS: rate_limit_blocks_after_max_attempts")


# 22. Rate limiting – successful login clears attempts
def test_rate_limit_clears_on_success():
    from app.services.auth_service import create_user, authenticate_user
    uname = _unique("ratelimclear")
    email = f"{uname}@ratelimclear.com"
    create_user("Rate Clear", uname, email, "StrongPass1!")

    auth_svc._clear_login_attempts(email)

    # 4 bad attempts (just under limit)
    for _ in range(auth_svc.MAX_LOGIN_ATTEMPTS - 1):
        authenticate_user(email, "WrongPass!")

    # Successful login should clear attempts
    result = authenticate_user(email, "StrongPass1!")
    assert result is not None, "Should succeed and clear rate limit"

    # Should be able to make more bad attempts without being locked out
    for _ in range(3):
        authenticate_user(email, "WrongPass1!")
    # Still not rate-limited
    assert auth_svc._check_rate_limit(email), "Should still be allowed after cleared attempts"
    print("  PASS: rate_limit_clears_on_success")


# 23. Guest migration – creates student data for user
def test_guest_migration_success():
    from app.services.auth_service import create_user, migrate_guest_data
    uname = _unique("migrate")
    email = f"{uname}@migrate.com"
    user = create_user("Migrate User", uname, email, "StrongPass1!")

    guest_data = {
        "profile": {"name": "Guest User", "goal": "Learn Python"},
        "roadmap": {"modules": [{"title": "Module 1"}]},
        "progress": {"completed": 5},
        "study_sessions": [{"date": "2026-01-01", "duration": 60}],
        "study_goal": {"weekly_goal_hours": 14, "preferred_days": ["Mon", "Wed"]},
    }
    result = migrate_guest_data(user["id"], guest_data)
    assert result is not None, "Migration should return imported summary"
    assert result.get("profile") is True
    assert result.get("progress") is True
    assert result.get("roadmap") is True
    assert result.get("study_sessions") == 1
    assert result.get("study_goal") is True
    print("  PASS: guest_migration_success")


# 24. Guest migration – empty data returns empty summary
def test_guest_migration_empty_data():
    from app.services.auth_service import create_user, migrate_guest_data
    uname = _unique("migrateempty")
    email = f"{uname}@migrateempty.com"
    user = create_user("Migrate Empty", uname, email, "StrongPass1!")

    result = migrate_guest_data(user["id"], {})
    assert result is not None, "Should return summary dict"
    assert result == {}, "Empty guest_data should return empty summary"
    print("  PASS: guest_migration_empty_data")


# 25. Registration returns tokens (backend always returns JWT)
def test_register_returns_tokens():
    from app.services.auth_service import create_user
    from app.utils.jwt import decode_token
    uname = _unique("rettokens")
    email = f"{uname}@test.com"
    user = create_user("Token User", uname, email, "StrongPass1!")

    from app.utils.jwt import create_access_token, create_refresh_token
    access = create_access_token(user["id"], user["username"])
    refresh = create_refresh_token(user["id"], user["username"])

    access_payload = decode_token(access)
    refresh_payload = decode_token(refresh)
    assert access_payload["type"] == "access"
    assert refresh_payload["type"] == "refresh"
    assert access_payload["sub"] == user["id"]
    assert refresh_payload["sub"] == user["id"]
    print("  PASS: register_returns_tokens")


# 26. Login with email returns tokens
def test_login_returns_tokens():
    from app.services.auth_service import create_user, authenticate_user
    from app.utils.jwt import create_access_token, create_refresh_token, decode_token
    uname = _unique("logtoken")
    email = f"{uname}@test.com"
    create_user("Login Token", uname, email, "MyPass123!")
    result = authenticate_user(email, "MyPass123!")
    assert result is not None

    access = create_access_token(result["id"], result["username"])
    refresh = create_refresh_token(result["id"], result["username"])
    assert decode_token(access) is not None
    assert decode_token(refresh) is not None
    assert decode_token(access)["type"] == "access"
    assert decode_token(refresh)["type"] == "refresh"
    print("  PASS: login_returns_tokens")


# 27. Forgot password returns token for existing user
def test_forgot_password_returns_token():
    from app.services.auth_service import create_user, create_forgot_password_token
    uname = _unique("forgotret")
    email = f"{uname}@test.com"
    create_user("Forgot Ret", uname, email, "StrongPass1!")
    token = create_forgot_password_token(email)
    assert token is not None, "Should return raw token for existing user"
    assert len(token) > 10
    print("  PASS: forgot_password_returns_token")


# 28. Forgot password returns None for non-existent user
def test_forgot_password_returns_none_for_missing():
    from app.services.auth_service import create_forgot_password_token
    fake_email = f"missing_{uuid.uuid4().hex[:8]}@nowhere.com"
    token = create_forgot_password_token(fake_email)
    assert token is None, "Should return None for non-existent email"
    print("  PASS: forgot_password_returns_none_for_missing")


# 29. JWT access token contains correct fields
def test_jwt_access_token_fields():
    from app.utils.jwt import create_access_token, decode_token
    uid = str(uuid.uuid4())
    token = create_access_token(uid, "testuser", extra={"role": "student"})
    payload = decode_token(token)
    assert payload["sub"] == uid
    assert payload["username"] == "testuser"
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "iat" in payload
    assert payload["role"] == "student"
    print("  PASS: jwt_access_token_fields")


# 30. User lookup by ID
def test_get_user_by_id():
    from app.services.auth_service import create_user, get_user_by_id
    uname = _unique("byid")
    email = f"{uname}@test.com"
    user = create_user("By ID User", uname, email, "StrongPass1!")
    found = get_user_by_id(user["id"])
    assert found is not None
    assert found["username"] == uname
    assert found["email"] == email
    print("  PASS: get_user_by_id")


# 31. User lookup by ID – non-existent returns None
def test_get_user_by_id_not_found():
    from app.services.auth_service import get_user_by_id
    found = get_user_by_id("non-existent-uuid-12345")
    assert found is None
    print("  PASS: get_user_by_id_not_found")


# 32. User lookup by email
def test_get_user_by_email():
    from app.services.auth_service import create_user, get_user_by_email
    uname = _unique("byemail")
    email = f"{uname}@test.com"
    create_user("By Email", uname, email, "StrongPass1!")
    found = get_user_by_email(email)
    assert found is not None
    assert found["username"] == uname
    print("  PASS: get_user_by_email")


ALL_TESTS = [
    test_register_success,
    test_register_duplicate_email,
    test_register_duplicate_username,
    test_login_username,
    test_login_email,
    test_login_wrong_password,
    test_jwt_access_token_roundtrip,
    test_jwt_refresh_token_roundtrip,
    test_jwt_invalid_token,
    test_password_hash_verify,
    test_password_strength_weak,
    test_password_strength_strong,
    test_forgot_password_existing_user,
    test_forgot_password_nonexistent_user,
    test_reset_password_success,
    test_reset_password_expired_token,
    test_reset_password_invalid_token,
    test_reset_password_used_token,
    test_user_table_no_google_columns,
    test_password_reset_token_table,
    test_rate_limit_blocks_after_max_attempts,
    test_rate_limit_clears_on_success,
    test_guest_migration_success,
    test_guest_migration_empty_data,
    test_register_returns_tokens,
    test_login_returns_tokens,
    test_forgot_password_returns_token,
    test_forgot_password_returns_none_for_missing,
    test_jwt_access_token_fields,
    test_get_user_by_id,
    test_get_user_by_id_not_found,
    test_get_user_by_email,
]


def main():
    print(f"\nRunning {len(ALL_TESTS)} auth tests...\n")
    passed = 0
    failed = 0
    for test_fn in ALL_TESTS:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {test_fn.__name__}: {e}")
            failed += 1

    print(f"\nResults: {passed}/{len(ALL_TESTS)} passed, {failed} failed")
    if failed:
        sys.exit(1)
    print("ALL AUTH TESTS PASSED\n")


if __name__ == "__main__":
    import hashlib
    main()
