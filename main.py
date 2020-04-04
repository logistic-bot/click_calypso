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

import click

from pathlib import Path
from sys import argv
from pprint import pprint as print

from user import User
from explorer import Explorer


def create_dir_if_not_exists(path):
    """
    path: Path

    Create the directory at <path> if it doesn't exist
    """
    path.mkdir(exist_ok=True)


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
)
@click.option(
    "--email",
    type=str,
    envvar="CALYPSO_EMAIL",
    help="Email. Will prompt if not provided.",
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
    context.obj["current_user"] = current_user
    context.obj["explorer"] = explorer


@cli.command()
@click.pass_context
@click.option("--name", type=bool, help="Show node names", default=False, is_flag=True)
@click.option(
    "--no-uuid", type=bool, help="Show node uuids", default=True, is_flag=True
)
@click.option(
    "--separator", type=str, help="Separator between atributes", default=" - "
)
@click.option(
    "--format-string",
    type=str,
    help="Format string. If specified, --name, --uuid and --separator are ignored. NOT IMPLEMENTED",
    default=None,
)
def list(context, name, no_uuid, separator, format_string):
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
        for f in formats:
            format_string += f

            if not formats.index(f) == len(formats) - 1:
                format_string += separator
    else:
        raise NotImplementedError("Sorry about that")

    # run
    for node in nodes:
        print(format_string)
        click.echo(format_string.format(node=node))


@cli.command()
def read():
    """Read a node or a key from a node."""
    click.echo("reading node or key from specified node...")


@cli.command()
def edit():
    """Edits a key in a node."""
    click.echo("editing key from specified node...")


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
    click.echo("Calypso v1.0.0 `Click`")


if __name__ == "__main__":
    cli()
