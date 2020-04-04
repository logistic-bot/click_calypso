#!/usr/bin/env python3

from pathlib import Path
from user import User
from node import Node


class Explorer:
    def __init__(self, repo_path, user):
        assert isinstance(repo_path, Path)
        assert isinstance(user, User)

        self.repo_path = repo_path
        self.data_path = repo_path / "data"
        self.user = user

    def __repr__(self):
        return self.__dict__.__repr__()

    def list_all(self):
        all_node_names = []
        all_nodes = []

        for file in self.data_path.iterdir():
            all_node_names.append(file.name.rstrip(".json"))

        for uuid in all_node_names:
            node = Node()
            node.load(uuid, self.data_path)
            all_nodes.append(node)

        return all_nodes
