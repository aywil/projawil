from app.auth import utils as auth_utils
from app.db.models import UserSchema

john = UserSchema(
    username="john",
    password=auth_utils.hash_password("qwerty"),
    email="john@example.com",
)
sam = UserSchema(
    username="sam",
    password=auth_utils.hash_password("secret"),
)
users_db: dict[str, UserSchema] = {
    john.username: john,
    sam.username: sam,
}
