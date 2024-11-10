from flask import Flask

app = Flask(__name__)


class User:
    def __init__(self, name: str, age: int, favourite_drink: str):
        self.name = name
        self.age = age
        self.favourite_drink = favourite_drink

    def __str__(self):
        return f"{self.name} age {self.age} who likes {self.favourite_drink}"


@app.route("/")
def home_page():
    user = User("John", 55, "Beer")
    return f"<p>Why Hello There, {user}</p>"
