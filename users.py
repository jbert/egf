from flask import Flask
from typing import Iterator, Optional
from sqlite3 import connect, OperationalError

app = Flask(__name__)


class User:
    def __init__(self, id: str, name: str, age: int, favourite_drink: str):
        self.id = id
        self.name = name
        self.age = age
        self.favourite_drink = favourite_drink

    def __str__(self):
        return f"{self.name} age {self.age} who likes {self.favourite_drink}"


@app.route("/")
def home_page():
    user = User("1234", "John", 55, "Beer")
    return f"<p>Why Hello There, {user}</p>"


@app.route("/user")
def list_users() -> str:
    users = db.list_users()
    num = 0
    s = [""]  # Save room for preamble
    for user in users:
        num += 1
        s.append(str(user))
    s[0] = f"We have {num} users"
    return "<p>" + "</p><p>".join(s) + "</p>"


@app.route("/user/<user_id>")
def view_user(user_id) -> str:
    user = db.get_user(user_id)
    if user is None:
        return f"<p>Userid {user_id} not found"
    return "<p>" + str(user) + "</p>"


# Data model to allow us to migrate db and/or ORM without changing application code
class SqliteDB:
    @classmethod
    def record_to_user(cls, record) -> User:
        return User(record[0], record[1], record[2], record[3])

    def __init__(self, fname: str):
        self.fname = fname
        self._create_schema()

    def _con(self):
        return connect(self.fname)

    def list_users(self) -> Iterator[User]:
        with self._con() as con:
            res = con.execute(
                "SELECT user_id, name, age, favourite_drink FROM users")
            records = res.fetchall()
            return map(SqliteDB.record_to_user, records)

    def get_user(self, user_id) -> Optional[User]:
        with self._con() as con:
            res = con.execute(
                "SELECT user_id, name, age, favourite_drink FROM users WHERE user_id = ?", [user_id])
            records = res.fetchall()
            if len(records) < 1:
                return None
            return SqliteDB.record_to_user(records[0])

    def _create_schema(self):
        with self._con() as con:
            try:
                con.execute(
                    "CREATE TABLE users(user_id, name, age, favourite_drink)")
            except OperationalError as e:
                if "table users already exists" in str(e):
                    app.logger.info(f"Caught exception: {e}")
                else:
                    raise e


db = SqliteDB("users.db")
