# Zedu API Automation Test Suite

An automated API test suite for the [Zedu Chat API](https://api.zedu.chat/swagger/#/), built with Python and pytest. The suite covers authentication and user management with a focus on positive scenarios, negative scenarios, and edge cases.

---

## Project Overview

This project tests the Zedu Chat REST API across two endpoint groups:

- **Auth** — registration, login, logout, and onboard status
- **User** — retrieving and updating user profile

Every test validates five layers of the response:

1. HTTP status code
2. Field presence
3. Data types
4. Field values
5. Schema validation

The test suite is designed to be **idempotent** — it can be run repeatedly without manual cleanup, using `Faker` to generate fresh data on every run. Token handling is fully programmatic and centralized; no credentials or tokens are hardcoded anywhere.

---

## Prerequisites

Python 3.13.7
Pip 25.2

### Dependencies

All dependencies are listed in `requirements.txt`:

```
pytest
requests
jsonschema
python-dotenv
faker
```

Install them all with:

```bash
pip install -r requirements.txt
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd zedu_api_tests
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the `.env` file

Create a file named `.env` in the **project root** — the same folder that contains `conftest.py` and `pytest.ini`. This is important; if the file is placed anywhere else, the credentials will not be loaded.

```
zedu_api_tests/
├── .env          ← must be here
├── conftest.py
├── pytest.ini
```

The `.env` file must contain these three values:

```env
BASE_URL=
TEST_EMAIL=
TEST_PASSWORD=
```

---

## Running the Tests

### Run the full test suite

```bash
pytest
```

### Run a specific test file

```bash
pytest tests/test_auth.py
pytest tests/test_user.py
```

### Run only negative tests

```bash
pytest -k "Negative"
```

### Run only edge case tests

```bash
pytest -k "Edge"
```

### Run a single test by name

```bash
pytest tests/test_auth.py::TestValidLogin::test_valid_login

```

### Generate an HTML report

```bash
pytest --html=report.html --self-contained-html
```

---

## Test File Descriptions

### `tests/test_auth.py`

Covers the full authentication lifecycle for the `/auth` endpoint group.

- **Positive** — valid registration of a new unique user, valid login returning a token and user object, onboard status returning the correct boolean flags and authenticated logout using a dedicated fresh token (not the shared session token), validating the success response
- **Negative** — login with wrong password, login with unregistered email, login with empty email or password, login with malformed email format, registering a duplicate email, registering with missing required fields, accessing a protected route with no token,and with a malformed token
- **Edge cases** — SQL injection in the email field, extremely long passwords, Unicode characters in name fields, empty request body, and sending credentials with the wrong content type

### `tests/test_user.py`

Covers the `/user/{userId}` endpoint for retrieving and updating the authenticated user's profile.

- **Positive** — retrieving own profile and validating all core fields and types, updating `id`, `username`, `firstName`, and `lastName` in a single request.
- **Negative** — retrieving profile without a token, retrieving a non-existent user ID, updating profile without a token, and updating a profile without token
- **Edge cases** — empty string for `lastName`, an extremely long value for `firstName` and submitting unknown extra fields in the payload


---

## Key Design Decisions

**Centralized login** — `raw_login()` in `conftest.py` is the only place login logic lives. All fixtures and tests that need a token use this function. It reads credentials from `.env` and never has them hardcoded.

**Session-scoped token** — the `auth_token` fixture runs login once per test session and shares the resulting token with every test that needs it via the `api` fixture.

**Logout isolation** — the logout test uses a fresh one-off token rather than the shared session token, preventing it from breaking subsequent tests.

**Idempotent data** — `Faker` generates unique emails, names, and channel names on every run so tests never depend on or pollute each other's data.

**`additionalProperties: True` in schemas** — schemas validate only the fields the application cares about. Extra fields in the response (such as deeply nested organisation or plan data) are allowed without failing the schema check, making the suite resilient to non-breaking API additions.
