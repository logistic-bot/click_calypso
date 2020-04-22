"""This file implements a number of utility functions for the repl command, such as prompt
creation and auto completion."""

import prompt_toolkit


def build_prompt(context):
    """Build the left prompt acording to the current context, and returns the string.

    TODO: Add color support"""
    formats = []
    formats.append("\n")

    formats.append("╭─ ")

    try:
        _ = context.obj["explorer"].current_node.data["name"]
        formats.append("{context.obj[explorer].current_node.data[name]}")

    except KeyError:
        formats.append("(No name)")

    formats.append(" | ")

    try:
        uuid = context.obj["explorer"].current_node.uuid
        if uuid == "":
            formats.append("(Empty uuid)")
        else:
            formats.append("{context.obj[explorer].current_node.uuid}")
    except KeyError:
        formats.append("(No uuid)")

    formats.append("\n")
    formats.append("╰─❯ ")

    format_string = "".join(formats)

    return format_string.format(context=context)


def build_right_prompt(context):
    """Build the right prompt acording to the context, and return the string.

    TODO: Color support"""
    formats = []

    formats.append("\n")

    formats.append(" ")
    formats.append("{context.obj[user].name}")

    formats.append(" | ")
    formats.append("{context.obj[user].email}")

    formats.append(" | ")
    formats.append("{context.obj[user].uuid}")

    formats.append(" ─╮")

    formats.append("\n")

    path = context.obj["explorer"].path
    path = "/".join(path)

    if path != "":
        formats.append(" ")
        formats.append(path)
        formats.append(" ")

    formats.append("─╯")

    format_string = "".join(formats)

    return format_string.format(context=context)


def build_completer(context):
    """Build the completer for the current context, and returns it"""
    possible_keys = context.obj["explorer"].possible_keys()
    possible_keys = {i: None for i in possible_keys}

    possible_nodes_as_nodes = context.obj["explorer"].list_all()

    possible_nodes = {}
    for node in possible_nodes_as_nodes:
        possible_nodes[node.uuid] = node.fields_dict

    possible_places = {}
    possible_places.update(possible_keys)
    possible_places.update(possible_nodes)

    possible_places_keys = {}
    possible_nodes_keys = {}
    possible_keys_keys = {}

    for key in possible_places:
        possible_places_keys[key] = None
    for key in possible_nodes:
        possible_nodes_keys[key] = None
    for key in possible_keys:
        possible_keys_keys[key] = None

    nested_dict = {
        "exit": None,  # exit
        "help": {  # summary help, or help for specified command
            "": None,
            "exit": None,
            "help": None,
            "ls": None,
            "cd": None,
            "cn": None,
            "ck": None,
            "e": None,
            "edit": None,
            "touch": None,
            "mknode": None,
        },
        "ls": possible_places_keys,  # list all nodes, or top level keys from specified path
        "cd": possible_places_keys,  # change into node, or key from specified path
        "cn": possible_nodes_keys,  # change into node
        "ck": possible_keys_keys,  # change into key
        "e": None,  # edit current, or key from specified path
        "edit": None,  # edit current, or key from specified path
        "touch": None,  # create key with specified name
        "mknode": None,  # create node with specified name, and print uuid
    }

    command_completer = prompt_toolkit.completion.NestedCompleter.from_nested_dict(
        nested_dict
    )

    return command_completer
