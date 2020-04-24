#!/usr/bin/env python

#####################################################
#    mmm    mm   m     m     m mmmmm   mmmm   mmmm  #
#  m"   "   ##   #      "m m"  #   "# #"   " m"  "m #
#  #       #  #  #       "#"   #mmm#" "#mmm  #    # #
#  #       #mm#  #        #    #          "# #    # #
#   "mmm" #    # #mmmmm   #    #      "mmm#"  #mm#  #
#####################################################

"""
This is the main file from Calypso.
This is where everything is launched.
"""

import json
import subprocess
from pathlib import Path
from pprint import pformat
from pprint import pprint as print  # pylint:disable=W0611,W0622 # noqa

import click
import prompt_toolkit
import structlog

from explorer import Explorer
from prompt import build_prompt, build_right_prompt, build_completer
from user import User

logger = structlog.get_logger()

logger.debug("Calypso Started!!")


@click.group()
@click.option(
    "--repo",
    type=str,
    envvar="CALYPSO_REPO",
    show_default="~/.config/calypso",
    default="~/.config/calypso",
    help="Path to repository.",
)
@click.option(
    "--user",
    type=str,
    envvar="CALYPSO_USER",
    help="Username. Will prompt if not provided.",
    prompt=True,
)
@click.option(
    "--email",
    type=str,
    envvar="CALYPSO_EMAIL",
    help="Email. Will prompt if not provided.",
    prompt=True,
)
@click.pass_context
def cli(context, repo, user, email):
    """Allows interactions with the REPO Calypso repository.

    An user consists of an username and an associated email. It is used to help
    denote who did what, but is in NO WAY secure, as-in it has NO PASSWORD, not
    even plain-text stored.
    """

    log = logger.new(command="cli", context=context.obj, repo=repo, user=user, email=email)

    # setup vars
    repo = Path(repo).expanduser().resolve()
    userpath = repo / "user"
    current_user = User(user, email, userpath)
    explorer = Explorer(repo, current_user)

    log.debug("Setting Repo Path", repopath=repo)
    log.debug("setting user path", userpath=userpath)

    # login user
    log.info("Logging in")
    current_user.login()

    # ensure the context object is a dict
    context.ensure_object(dict)

    # setup context
    context.obj["repo"] = repo
    context.obj["user"] = current_user
    context.obj["explorer"] = explorer


@cli.command("list")  # avoid redefining builtin list
@click.pass_context
@click.option("--name", type=bool, help="Show node names", default=False, is_flag=True)
@click.option(
    "--uuid/--no-uuid", type=bool, help="Show node uuids", default=True, is_flag=True
)
@click.option(
    "--separator", type=str, help="Separator between attributes", default=" - "
)
@click.option(
    "--format-string",
    type=str,
    help="Format string. If specified, --name, --uuid and --separator are ignored. NOT IMPLEMENTED",
    default=None,
)
def list_all(context, name, uuid, separator, format_string):
    """List all the nodes."""

    # setup vars
    explorer = context.obj["explorer"]
    nodes = explorer.list_all()

    log = logger.new(name=name, uuid=uuid, separator=separator,
                     format_string=format_string, command="list")

    log.debug("Nodes", nodes=nodes)

    if format_string is None:
        log.info("Using default format options -- no format string was provided")
        formats = []

        if uuid:
            log.debug("Adding uuid info")
            formats.append("{node.uuid}")
        if name:
            log.debug("Adding name info")
            formats.append("{node.data[name]}")

        format_string = ""
        for format_str in formats:
            format_string += format_str

            if not formats.index(format_str) == len(formats) - 1:
                format_string += separator
    else:
        log.critical("This feature is not implemented!")
        raise NotImplementedError("Sorry about that")  # TODO

    # run
    log.debug("Starting output")
    for node in nodes:
        output = format_string.format(node=node)

        log.debug("printing node", node=node, output=output)

        click.echo(output)


@cli.command()
@click.argument("node", type=str, envvar="CALYPSO_NODE")
@click.argument("key", type=str, envvar="CALYPSO_KEY", default=None, required=False)
@click.option(
    "--indent",
    type=int,
    default=1,
    help="Indentation to use for showing nested values",
)
@click.option("--width", type=int, default=80, help="Max line width")
@click.option(
    "--depth",
    type=int,
    default=5,
    help="Max depth to print. Default 5. Set to -1 for infinite.",
)
@click.option(
    "--sort-keys/--no-sort-keys",
    type=bool,
    default=False,
    help="Do not sort keys in output",
    is_flag=True,  # pylint:disable=R0913
)  # pylint:disable=R0913
@click.pass_obj
def read(context, node, key, indent, width, sort_keys, depth):
    """Either reads the whole NODE or the KEY from the NODE.

    NODE is the uuid of the node to read from. Example:
    353430d7-a043-4c2a-bd1c-57d816a65787

    KEY is the name of a top-level key or a path relative to the NODE root in
    the form `creator/email`. A trailing or leading `/` is also accepted, but
    considered non-standard. Using multiple `/` in between keys
    (`creator////email`) also works, but is considered ugly.

    """
    log = logger.new(node=node, key=key,
                     command="read")
    log.debug("indent", indent=indent)
    log.debug("width", width=width)
    log.debug("sort_keys", sort_keys=sort_keys)
    log.debug("depth", depth=depth)

    explorer = context["explorer"]

    if depth == -1:
        log.debug("Infinite depth")
        depth = None

    log.debug("Going to specified node and key")
    explorer.go_to(node, key)

    log.debug("Echoing data")
    click.echo(
        pformat(
            explorer.get_path_data(),
            indent=indent,
            width=width,
            sort_dicts=sort_keys,
            depth=depth,
        )
    )

    log.debug("Done with reading data")


@cli.command()
@click.pass_obj
@click.argument("node", type=str, envvar="CALYPSO_NODE")
@click.argument("key", type=str, envvar="CALYPSO_KEY", default=None, required=False)
@click.option(
    "--editor", type=str, envvar="CALYPSO_EDITOR", default="nano", required=False,
)
def edit(context, node, key, editor):
    """Edits a key in a node."""

    log = logger.new(node=node, key=key, command="edit")
    log.debug("editor", editor=editor)

    log.info("Going to specified node and key")
    explorer = context["explorer"]
    explorer.go_to(node, key)

    filepath = context[
                   "repo"
               ] / "DATA-EDIT-IN-PROGRESS-BY-{}-ON-NODE-{}--DO-NOT-DELETE.json".format(
        context["user"].name, node
    )
    log.info("Creating temp file", filepath=filepath)
    log.info("Writing to temp file")

    with open(filepath, "w") as tmp_file:
        tmp_file.write(json.dumps(explorer.get_path_data(), indent=2, sort_keys=True))
        tmp_file.flush()

    log.info("launching editor")
    proc = subprocess.Popen("{} {}".format(editor, tmp_file.name), shell=True)
    proc.communicate()
    proc.wait()

    log.debug("Editor exited, reading data")
    with open(filepath, "r") as tmp_file:
        data = json.load(tmp_file)

        log.debug("Writing read data to node")
        explorer.change_data(data)

    log.info("Deleting file")
    # delete the file
    filepath.unlink()

    log.info("Editing done")


@cli.command()
@click.pass_context
def repl(context):
    """
    Starts an interactive read-eval-print loop.
    """

    log = logger.new(command="repl")
    log.info("Invoking version command")

    context.invoke(version)
    click.echo()
    click.echo("Type `exit` to quit.")

    explorer = context.obj["explorer"]
    action = ""

    history_path = (
            explorer.repo_path / "user" / "HISTORY-{}".format(context.obj["user"].uuid)
    )
    log.debug("history_path", history_path=history_path)

    log.info("Starting loop")

    while action != "exit":
        log.debug("Waiting for input...")
        action = prompt_toolkit.prompt(
            build_prompt(context),
            history=prompt_toolkit.history.FileHistory(history_path),
            auto_suggest=prompt_toolkit.auto_suggest.AutoSuggestFromHistory(),
            mouse_support=True,
            complete_while_typing=True,
            completer=build_completer(context),
            rprompt=build_right_prompt(context),
        )
        log.debug("Got input", input=action)

        print(action)

    log.info("Exited loop")
    log.info("Exited repl command")


@cli.command()
def version():
    """Prints version and copyright information"""

    log = logger.new(command="version")
    log.debug("Giving version info")

    click.echo("You are using CALYPSO, originally coded by Khaïs COLIN.")
    click.echo("Copyright: GNU GPL 3.0")
    click.echo("Calypso v2.3.0 `Scatter`")

    log.debug("End of version command")


if __name__ == "__main__":
    cli()  # pylint:disable=E1120
