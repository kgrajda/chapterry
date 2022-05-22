import sys
from typing import List
import click
from eyed3.id3 import Tag
from eyed3.id3.frames import ChapterFrame, StartEndTuple


@click.group()
def cli():
    pass


@click.command(help="Input MP3 file")
@click.argument("input", type=click.Path(exists=True))
def ls(input: click.Path):
    tag = Tag()
    tag.parse(input)

    if tag is None:
        click.echo("Unsupported file type.")
        return

    if tag.artist is not None:
        click.echo(f"Artist: {tag.artist}")
    if tag.album is not None:
        click.echo(f"Album: {tag.album}")

    chapters: List[ChapterFrame] = tag.chapters
    for chapter in chapters:
        times: StartEndTuple = chapter.times
        title_part = ' "' + chapter.title + '"' if chapter.title is not None else ""
        click.echo(
            f"<{times.start}:{times.end}> {chapter.element_id.decode('utf-8')}{title_part}"
        )


cli.add_command(ls)

if __name__ == "__main__":
    sys.exit(cli())
