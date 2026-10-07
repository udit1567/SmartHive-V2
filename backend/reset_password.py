"""Dev-only: reset a local user's password.

Usage (from backend/, with the venv active):

    python reset_password.py uditmaurya2003@gmail.com "the-new-password"

Uses the same hash_password helper as signup, so login will accept the
new password. Passwords are stored one-way hashed; this sets a new one,
it does not recover the old one.
"""

import sys

from app import create_app
from app.auth import hash_password
from app.extensions import db
from app.models import User


def main():
    if len(sys.argv) != 3:
        print('Usage: python reset_password.py <email> "<new password>"')
        raise SystemExit(1)

    email, new_password = sys.argv[1], sys.argv[2]

    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"No user with email {email!r}")
            raise SystemExit(1)

        user.password = hash_password(new_password)
        db.session.commit()
        print(f"Password reset for {user.email} (id={user.id}).")


if __name__ == "__main__":
    main()
