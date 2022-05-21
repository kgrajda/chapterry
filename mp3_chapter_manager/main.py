import sys
import click


@click.group()
def cli():
    pass


@click.command(help="Input MP3 file")
@click.argument("input", type=click.Path(exists=True))
def ls(input: click.Path):
    pass


cli.add_command(ls)

if __name__ == "__main__":
    sys.exit(cli())
