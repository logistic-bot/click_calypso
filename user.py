"""User"""

from hashlib import sha1
import json


class User:
    """User"""

    def __init__(self, name, email, user_dir):
        self.name = name
        self.email = email
        self.user_dir = user_dir
        self.pretty_name = name

        self.uuid = sha1(
            "{}{}".format(self.name, self.email).encode("utf-8")
        ).hexdigest()

        self.datapath = user_dir / "{}.json".format(self.uuid)

    def __repr__(self):
        return self.__dict__.__repr__()

    def login(self):
        """
        Logins the user, asking for new user creation if the user does not
        already exist.
        """

        if self.exist():
            self.load()
        else:
            self.new_user_setup()

    def exist(self):
        """Checks is the user exist. Return True if it does, False otherwise."""
        return self.datapath.is_file() and self.datapath.exists()

    def save(self):
        """Saves the user to the disk"""
        data = {
            "name": self.name,
            "email": self.email,
            "pretty_name": self.pretty_name,
            "uuid": self.uuid,
        }

        with open(self.datapath, "w") as data_file:
            json.dump(data, data_file)

    def new_user_setup(self):
        """Setups a new user.

        Defines its pretty_name and save it for the first time
        """
        print("NEW USER SETUP")
        self.pretty_name = input("By what name should you be called? ")

        self.save()

    def load(self):
        """Loads user data from file"""
        with open(self.datapath, "r") as data_file:
            data = json.load(data_file)

        self.pretty_name = data["pretty_name"]
