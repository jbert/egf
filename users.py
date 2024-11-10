from flask import Flask, request
from typing import Iterator, Optional
from sqlite3 import connect, OperationalError
import uuid

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


@app.route("/user", methods=["GET", "POST"])
def user() -> str:
    if request.method == "GET":
        return list_users()
    elif request.method == "POST":
        return create_user()
    else:
        raise RuntimeError(f"Internal error - method is {request.method}")


@app.route("/user/<user_id>", methods=['GET', 'DELETE'])
def user_user_id(user_id) -> str:
    if request.method == "GET":
        return view_user(user_id)
    elif request.method == "DELETE":
        return delete_user(user_id)
    else:
        raise RuntimeError(f"Internal error - method is {request.method}")


def create_user() -> str:
    f = request.form
    user = User("", f["name"], int(f["age"]), f["favourite_drink"])
    user_id = db.create_user(user)
    return f"<p>Created user {user_id}</p>"


def list_users() -> str:
    users = db.list_users()
    num = 0
    s = [""]  # Save room for preamble
    for user in users:
        num += 1
        s.append(str(user))
    s[0] = f"We have {num} users"
    return "<p>" + "</p><p>".join(s) + "</p>"


def view_user(user_id) -> str:
    user = db.get_user(user_id)
    if user is None:
        return f"<p>Userid {user_id} not found"
    return "<p>" + str(user) + "</p>"


def delete_user(user_id) -> str:
    # TODO - distinguish "user not found" and "user deleted"
    # e.g. return bool from db.delete_user
    db.delete_user(user_id)
    return f"<p>Userid {user_id} deleted</p>"


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

    def delete_user(self, user_id) -> None:
        with self._con() as con:
            con.execute(
                "DELETE FROM users WHERE user_id = ?", [user_id])
            return None

    def create_user(self, user) -> str:
        with self._con() as con:
            user_id = str(uuid.uuid4())
            params = [user_id, user.name, user.age, user.favourite_drink]
            con.execute(
                "INSERT INTO users (user_id, name, age, favourite_drink) VALUES (?, ?, ?, ?)", params)
            return user_id

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
