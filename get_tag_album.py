from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3
from mutagen.oggvorbis import OggVorbis as OGG
from pathlib import Path
import argparse

MUSIC_DIR = Path("~/Music/mpd").expanduser()


def main(album: Path, tag: str, show_only_first: bool = False):
    # get album path
    # get type of tag, then arg
    # for every song:
        # add tag to list
    # show tags for album

    if tag == "albumname": tag = "album"
    
    assert album.is_dir()
    exts = ("*.flac", "*.mp3", "*.ogg")
    p = [f for ext in exts for f in album.glob(ext)]
    files = [x for x in p if x.is_file()]
    files.sort()

    all_tags = []
    for track in files:
        match track.suffix:
            case ".flac":
                audio = FLAC(track)
            case ".mp3":
                audio = EasyID3(track)
            case ".ogg":
                audio = OGG(track)

        try:
            tag = audio[tag]
            all_tags += tag
        except KeyError:
            print("") # blank str for pipe

        if show_only_first:
            break

    formatted_tags = "; ".join(set(all_tags))
    print(formatted_tags)


def init_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument("album", type=str)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--date", action="store_true", default=False)
    group.add_argument("--genre", action="store_true", default=False)
    group.add_argument("--artist", action="store_true", default=False)
    group.add_argument("--albumname", action="store_true", default=False)
    group.add_argument("--albumartist", action="store_true", default=False)

    return parser


if __name__ == "__main__":
    parser = init_parser()
    args = parser.parse_args()


    dict_args = vars(args)
    assert "album" in dict_args.keys()
    album = dict_args.pop("album", None)
    album_path = MUSIC_DIR / album

    assert album_path.exists(), album_path
    assert album_path.is_dir(), album_path

    only_passed_tag = {k: v for k, v in dict_args.items() if v}

    if len(only_passed_tag) == 1:
        tag = list(only_passed_tag)[0]
        main(album=album_path, tag=tag, show_only_first=True)
