import tempfile

from django.core.management.base import BaseCommand

from nickelodeon.models import MP3Song
from nickelodeon.utils import convert_audio, s3_object_url, s3_upload


class Command(BaseCommand):
    help = "Add the missing duration of the songs in the library"

    def handle(self, *args, **options):
        songs = MP3Song.objects.select_related("owner").filter(duration=0)
        song_count = songs.count()
        for i, song in enumerate(songs):
            try:
                print(f"{i}/{song_count}")
                self.handle_song(song)
            except KeyboardInterrupt:
                break

    def handle_song(self, song):
        print(song.filename)
        song.get_duration()

    def print_conversion_progress(self, perc):
        self.stdout.write("\r{}%".format(round(100 * perc, 1)), ending="")
