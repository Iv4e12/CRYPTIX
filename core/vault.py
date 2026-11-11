
import json
import sqlite3
import uuid

from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidTag

import secrets


DATABASE = (
    Path(__file__).resolve().parent.parent
    / "database"
    / "vault.db"
)

VERIFICATION_TEXT = b"CRYPTIX_VAULT_VERIFIED"


def get_connection():
    DATABASE.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value BLOB NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id TEXT PRIMARY KEY,
            nonce BLOB NOT NULL,
            ciphertext BLOB NOT NULL
        )
    """)

    return connection


def derive_key(password, salt):
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1
    )

    return kdf.derive(password.encode("utf-8"))


def vault_exists():
    if not DATABASE.exists():
        return False

    with get_connection() as connection:
        result = connection.execute(
            "SELECT value FROM metadata WHERE key = ?",
            ("salt",)
        ).fetchone()

    return result is not None


def create_vault(password):
    if len(password) < 10:
        raise ValueError(
            "Master password must be at least 10 characters."
        )

    if vault_exists():
        raise ValueError("A vault already exists.")

    salt = secrets.token_bytes(16)
    key = derive_key(password, salt)

    nonce = secrets.token_bytes(12)
    encrypted = AESGCM(key).encrypt(
        nonce,
        VERIFICATION_TEXT,
        None
    )

    with get_connection() as connection:
        connection.execute(
            "INSERT INTO metadata (key, value) VALUES (?, ?)",
            ("salt", salt)
        )

        connection.execute(
            "INSERT INTO metadata (key, value) VALUES (?, ?)",
            ("verification_nonce", nonce)
        )

        connection.execute(
            "INSERT INTO metadata (key, value) VALUES (?, ?)",
            ("verification_data", encrypted)
        )

    return key


def unlock_vault(password):
    if not vault_exists():
        raise ValueError("No vault has been created yet.")

    with get_connection() as connection:
        metadata = dict(
            connection.execute(
                "SELECT key, value FROM metadata"
            ).fetchall()
        )

    salt = metadata["salt"]
    nonce = metadata["verification_nonce"]
    encrypted = metadata["verification_data"]

    key = derive_key(password, salt)

    try:
        result = AESGCM(key).decrypt(
            nonce,
            encrypted,
            None
        )
    except InvalidTag:
        raise ValueError("Incorrect master password.")

    if result != VERIFICATION_TEXT:
        raise ValueError("Vault verification failed.")

    return key


def add_entry(key, title, username, secret, notes=""):
    if not title.strip():
        raise ValueError("Entry title cannot be empty.")

    entry_id = str(uuid.uuid4())

    data = {
        "title": title,
        "username": username,
        "secret": secret,
        "notes": notes
    }

    plaintext = json.dumps(data).encode("utf-8")

    nonce = secrets.token_bytes(12)

    ciphertext = AESGCM(key).encrypt(
        nonce,
        plaintext,
        entry_id.encode("utf-8")
    )

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO entries (id, nonce, ciphertext)
            VALUES (?, ?, ?)
            """,
            (entry_id, nonce, ciphertext)
        )

    return entry_id


def get_entries(key):
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, nonce, ciphertext FROM entries"
        ).fetchall()

    entries = []

    for entry_id, nonce, ciphertext in rows:
        plaintext = AESGCM(key).decrypt(
            nonce,
            ciphertext,
            entry_id.encode("utf-8")
        )

        data = json.loads(plaintext.decode("utf-8"))
        data["id"] = entry_id

        entries.append(data)

    return entries


def delete_entry(entry_id):
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM entries WHERE id = ?",
            (entry_id,)
        )
