#!/usr/bin/env python3
"""Implements Explorer"""

from pathlib import Path
from user import User
from node import Node


class Explorer:
    """
    Functions for interacting with a Calypso repository
    """

    def __init__(self, repo_path, user):
        assert isinstance(repo_path, Path)
        assert isinstance(user, User)

        self.repo_path = repo_path
        self.data_path = repo_path / "data"
        self.user = user

        self.current_node = Node()
        self.path = []

    def __repr__(self):
        return self.__dict__.__repr__()

    def view(self):
        data = self.get_path_data()

        return data

    def go_to(self, node, key):
        self.change_node(node)

        if key is not None:
            self.change_path_relative(key)

    def get_path_data(self):
        data = self.current_node.data

        for key in self.path:
            data = data[key]

        return data

    def possible_keys(self):
        data = self.get_path_data()
        keys = []

        if isinstance(data, dict):
            for key in data.keys():
                keys.append(key)

        return keys

    def change_path_relative(self, path):
        path_keys = path.split("/")

        for path_key in path_keys:
            if path_key in self.possible_keys():
                self.path.append(path_key)

            elif path_key == "..":
                try:
                    del self.path[-1]
                except IndexError:
                    pass  # same behaviour in linux

            elif path_key == ".":
                pass  # same behaviour in linux

            elif path_key == "":
                pass  # ignore empty path specs.

            else:
                raise KeyError(
                    "Nodepath {} has no key {}".format(
                        "{}/{}".format(self.current_node.uuid, self.path), path_key,
                    )
                )

    def change_node(self, uuid):
        """
        Set the current node to the node with the given uuid
        """
        self.current_node.load(uuid, self.data_path)

    def list_all(self):
        """
        Returns a list of all nodes in the repository,
        by creating a node.Node object for each
        """
        all_node_names = []
        all_nodes = []

        for file in self.data_path.iterdir():
            all_node_names.append(file.name.rstrip(".json"))

        for uuid in all_node_names:
            node = Node()
            node.load(uuid, self.data_path)
            all_nodes.append(node)

        return all_nodes
