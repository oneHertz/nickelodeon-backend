from django.core.management.base import BaseCommand
from tqdm import tqdm

from nickelodeon.models import MP3Song


class Command(BaseCommand):
    args = ["query"]
    help = "Add the missing durations for the songs in the library"

    def add_arguments(self, parser):
        parser.add_argument("-q", "--query", type=str, required=True)
        parser.add_argument("-r", "--replace", type=str, default=None)

    def handle(self, *args, **options):
        songs = MP3Song.objects.select_related("owner").filter(
            filename__contains=options["query"]
        )
        song_count = songs.count()
        try:
            for song in songs:
                print(song.filename)
            if (replace_str := options["replace"]) is not None:
                with tqdm(total=song_count, unit="song") as pbar:
                    for song in songs:
                        target = song.filename.replace(options["query"], replace_str)
                        print(target)
                    pbar.update(1)
        except KeyboardInterrupt:
            pass
