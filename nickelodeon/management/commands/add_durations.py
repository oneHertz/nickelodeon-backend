import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand

from nickelodeon.models import MP3Song
from nickelodeon.utils import convert_audio, s3_object_url, s3_upload


class Command(BaseCommand):
    help = "Add the missing duration of the songs in the library"

    def handle(self, *args, **options):
        songs = MP3Song.objects.select_related("owner").filter(duration=0)
        song_count = songs.count()
        i = 0
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_song = {executor.submit(self.handle_song, song): song for song in songs}
            for future in as_completed(future_to_song):
                song = future_to_song[future]
                print(song.filename)
                print(f"{i}/{song_count}")
                i += 1
        
    def handle_song(self, song):
        song.get_duration()
