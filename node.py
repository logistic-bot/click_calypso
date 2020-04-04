#!/usr/bin/env python3

"""
This file is part of Calypso

It implements the `Node` class.
"""

import json
from pathlib import Path


class Node:
    """
    Information about the node
    """

    def __init__(self):
        self.data = {}
        self.datapath = Path()
        self.uuid = ""

    def load(self, uuid, datapath):
        """
        Loads a node with a given uuid from the given datapath into the object.
        """
        filepath = datapath / "{}.json".format(uuid)

        self.datapath = filepath

        self.uuid = uuid

        with open(filepath, "r") as data_file:
            self.data = json.load(data_file)

    def fields(self):
        """
        Returns all the top-level fields of the node.
        """
        return self.data.keys()

    def save(self):
        """Saves the node's data to the file.

        WARNING FIXME: may cause data corruption if saved without loading first
        """

        with open(self.datapath, "w") as data_file:
            json.dump(self.data, data_file, sort_keys=True, indent=2)
