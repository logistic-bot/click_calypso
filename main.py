#!/usr/bin/python

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

Nameing convention: all names wich start with CALYPSO_ are global.
"""

from pathlib import Path
from pprint import pprint as print  # pylint:disable=W0611,W0622 # noqa
from pprint import pformat

import subprocess
import json
import click

from user import User
from explorer import Explorer


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

    An user consits of an username and an associated email. It is used to help
    denote who did what, but is in NO WAY secure, as-in it has NO PASSWORD, not
    even plain-text stored.
    """

    # setup primary vars
    repo = Path(repo).expanduser().resolve()

    # setup secondary vars
    userpath = repo / "user"

    # setup tretary vars
    current_user = User(user, email, userpath)

    # setup quadrenary vars
    explorer = Explorer(repo, current_user)

    # login user
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
@click.option("--no-uuid", type=bool, help="Show node uuids", default=True, is_flag=True)
@click.option("--separator", type=str, help="Separator between atributes", default=" - ")
@click.option(
    "--format-string",
    type=str,
    help="Format string. If specified, --name, --uuid and --separator are ignored. NOT IMPLEMENTED",
    default=None,
)
def list_all(context, name, no_uuid, separator, format_string):
    """List all the nodes."""
    # setup vars
    explorer = context.obj["explorer"]
    nodes = explorer.list_all()

    if format_string is None:
        formats = []

        if no_uuid:
            formats.append("{node.uuid}")
        if name:
            formats.append("{node.data[name]}")

        format_string = ""
        for formet_str in formats:
            format_string += formet_str

            if not formats.index(formet_str) == len(formats) - 1:
                format_string += separator
    else:
        raise NotImplementedError("Sorry about that")

    # run
    for node in nodes:
        click.echo(format_string.format(node=node))


@cli.command()
@click.argument("node", type=str, envvar="CALYPSO_NODE")
@click.argument("key", type=str, envvar="CALYPSO_KEY", default=None, required=False)
@click.option(
    "--indent", type=int, default=1, help="Indentation to use for showing nested values",
)
@click.option("--width", type=int, default=80, help="Max line width")
@click.option(
    "--depth", type=int, default=5, help="Max depth to print. Default 5. Set to -1 for infinite.",
)
@click.option(
    "--no-sort-keys",
    type=bool,
    default=False,
    help="Do not sort keys in output",
    is_flag=True,  # pylint:disable=R0913
)  # pylint:disable=R0913
@click.pass_obj
def read(context, node, key, indent, width, no_sort_keys, depth):
    """Either reads the whole NODE or the KEY from the NODE.

    NODE is the uuid of the node to read from. Example:
    353430d7-a043-4c2a-bd1c-57d816a65787

    KEY is the name of a top-level key or a path relative to the NODE root in
    the form `creator/email`. A trailing or leading `/` is also accepted, but
    considered non-standard. Using multiple `/` in between keys
    (`creator////email`) also works, but is considered ugly.

    """
    sort = not no_sort_keys
    explorer = context["explorer"]

    if depth == -1:
        depth = None

    explorer.go_to(node, key)

    click.echo(
        pformat(explorer.get_path_data(), indent=indent, width=width, sort_dicts=sort, depth=depth,)
    )


@cli.command()
@click.pass_obj
@click.argument("node", type=str, envvar="CALYPSO_NODE")
@click.argument("key", type=str, envvar="CALYPSO_KEY", default=None, required=False)
@click.option(
    "--editor", type=str, envvar="CALYPSO_EDITOR", default="nano", required=False,
)
def edit(context, node, key, editor):
    """Edits a key in a node."""
    explorer = context["explorer"]
    explorer.go_to(node, key)

    filepath = context[
        "repo"
    ] / "DATA-EDIT-IN-PROGRESS-BY-{}-ON-NODE-{}--DO-NOT-DELETE.json".format(
        context["user"].name, node
    )

    with open(filepath, "w") as tmp_file:
        tmp_file.write(json.dumps(explorer.get_path_data(), indent=2, sort_keys=True))
        tmp_file.flush()

        proc = subprocess.Popen("{} {}".format(editor, tmp_file.name), shell=True)
        proc.communicate()
        proc.wait()

    with open(filepath, "r") as tmp_file:
        data = json.load(tmp_file)

        explorer.change_data(data)

    # delete the file
    filepath.unlink()


@cli.command()
def repl():
    """
    Starts an interactive read-eval-print loop.
    """
    click.echo("starting read-eval-print loop...")


@cli.command()
def version():
    """Prints version and copyright information"""
    click.echo("You are using CALYPSO, originally coded by Khaïs COLIN.")
    click.echo("Copyright: GNU GPL 3.0")
    click.echo("Calypso v2.2.0 `deep`")


if __name__ == "__main__":
    cli()  # pylint:disable=E1120
