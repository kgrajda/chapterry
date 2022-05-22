import sys
from typing import List, Optional
import click
from eyed3.id3 import Tag
from eyed3.id3.frames import ChapterFrame, StartEndTuple, TITLE_FID


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


@click.command(help="Add chapter")
@click.argument("input", type=click.Path(exists=True))
@click.argument("chapter_id", type=click.STRING)
@click.argument("start", type=click.IntRange(min=0))
@click.argument("end", type=click.IntRange(min=0), required=False)
@click.option(
    "--force",
    is_flag=True,
    show_default=True,
    default=False,
    help="Ignore warnings and remove/update conflicting chapters.",
)
def add(input: click.Path, chapter_id: str, start: int, end: int, force: bool):
    tag = Tag()
    tag.parse(input)

    if tag is None:
        click.echo("Unsupported file type.")
        return

    if chapter_id == "":
        click.echo("Chapter ID must not be empty.")
        return

    if start >= end:
        click.echo("'start' argument must be less than 'end' argument.")
        return

    chapters: List[ChapterFrame] = tag.chapters

    conflicting_chapters: List[ChapterFrame] = list(
        filter(
            lambda chapter: chapter.times.start >= start and chapter.times.end <= end,
            chapters,
        )
    )

    if len(conflicting_chapters) > 0 and not force:
        click.echo(
            "Chapters are present in the specified time frame. "
            + "Consider --force flag to remove those chapters."
        )
        chapter_ids = [
            chapter.element_id.decode("utf-8") for chapter in conflicting_chapters
        ]
        click.echo(f"Conflicting chapters: {chapter_ids}")
        return
    elif len(conflicting_chapters) > 0:
        for chapter in conflicting_chapters:
            tag.chapters.remove(chapter.element_id)
        click.echo(f"{len(conflicting_chapters)} chapters removed.")

    chapter_conflicting_before: Optional[ChapterFrame] = next(
        filter(
            lambda chapter: chapter.times.start < start and chapter.times.end > start,
            tag.chapters,
        ),
        None,
    )

    if chapter_conflicting_before is not None and not force:
        conflicting_chapter_id = chapter_conflicting_before.element_id.decode("utf-8")
        click.echo(
            f"Chapter conflicts at the beginning: {conflicting_chapter_id}. "
            + "Consider --force flag to update this chapter."
        )
        return
    if chapter_conflicting_before is not None:
        new_times = chapter_conflicting_before.times = StartEndTuple(
            chapter_conflicting_before.times.start,
            start,
        )
        click.echo(f"Before: {new_times}")
        chapter_conflicting_before.times = new_times

    chapter_conflicting_after: Optional[ChapterFrame] = next(
        filter(
            lambda chapter: chapter.times.start < end and chapter.times.end > end,
            tag.chapters,
        ),
        None,
    )

    if chapter_conflicting_after is not None and not force:
        conflicting_chapter_id = chapter_conflicting_after.element_id.decode("utf-8")
        click.echo(
            f"Chapter conflicts at the end: {conflicting_chapter_id}. "
            + "Consider --force flag to update this chapter."
        )
        return
    elif chapter_conflicting_after is not None:
        new_times = StartEndTuple(end, chapter_conflicting_after.times.end)
        click.echo(f"After: {new_times}")
        chapter_conflicting_after.times = new_times

    tag.chapters.set(chapter_id.encode("utf-8"), times=(start, end))
    tag.save()


@click.command(help="Add chapter")
@click.argument("input", type=click.Path(exists=True))
@click.argument("id", type=click.STRING)
def remove_chapter(input: click.Path, id: str):
    tag = Tag()
    tag.parse(input)

    if tag is None:
        click.echo("Unsupported file type.")
        return

    if id == "":
        click.echo("Chapter ID must not be empty.")
        return

    chapter: Optional[ChapterFrame] = next(
        filter(lambda c: c.element_id.decode("utf-8") == id, tag.chapters), None
    )

    if chapter is None:
        click.echo("Chapter does not exist.")
        return

    tag.chapters.remove(id.encode("utf-8"))
    tag.save()


@click.command(help="Add chapter")
@click.argument("input", type=click.Path(exists=True))
@click.argument("chapter_id", type=click.STRING)
@click.argument("new_chapter_id", type=click.STRING)
def rename(input: click.Path, chapter_id: str, new_chapter_id: str):
    tag = Tag()
    tag.parse(input)

    if tag is None:
        click.echo("Unsupported file type.")
        return

    if new_chapter_id == "":
        click.echo("Chapter ID must not be empty.")
        return

    chapter: Optional[ChapterFrame] = next(
        filter(lambda c: c.element_id.decode("utf-8") == chapter_id, tag.chapters), None
    )

    if chapter is None:
        click.echo("Chapter does not exist.")
        return

    chapter.element_id = new_chapter_id.encode("utf-8")

    click.echo("Chapter renamed.")
    tag.save()


@click.group("set")
def set_cmd():
    pass


@click.command(help="Set title of the specified chapter")
@click.argument("input", type=click.Path(exists=True))
@click.argument("chapter_id", type=click.STRING)
@click.argument("title", type=click.STRING)
def set_title(input: click.Path, chapter_id: str, title: str):
    tag = Tag()
    tag.parse(input)

    if tag is None:
        click.echo("Unsupported file type.")
        return

    if chapter_id == "":
        click.echo("Chapter ID must not be empty.")
        return

    chapter: Optional[ChapterFrame] = next(
        filter(lambda c: c.element_id.decode("utf-8") == chapter_id, tag.chapters), None
    )

    if chapter is None:
        click.echo("Chapter does not exist.")
        return

    chapter.title = title
    tag.save()


@click.group("remove")
def remove_cmd():
    pass


@click.command(help="Remove title of the specified chapter")
@click.argument("input", type=click.Path(exists=True))
@click.argument("chapter_id", type=click.STRING)
def remove_title(input: click.Path, chapter_id: str):
    tag = Tag()
    tag.parse(input)

    if tag is None:
        click.echo("Unsupported file type.")
        return

    if chapter_id == "":
        click.echo("Chapter ID must not be empty.")
        return

    chapter: Optional[ChapterFrame] = next(
        filter(lambda c: c.element_id.decode("utf-8") == chapter_id, tag.chapters), None
    )

    if chapter is None:
        click.echo("Chapter does not exist.")
        return

    chapter.sub_frames.pop(TITLE_FID, None)
    tag.save()


set_cmd.add_command(set_title, "title")

remove_cmd.add_command(remove_title, "title")
remove_cmd.add_command(remove_chapter, "chapter")

cli.add_command(ls)
cli.add_command(add)
cli.add_command(remove_chapter)
cli.add_command(rename)
cli.add_command(set_cmd, "set")
cli.add_command(remove_cmd, "remove")

if __name__ == "__main__":
    sys.exit(cli())
