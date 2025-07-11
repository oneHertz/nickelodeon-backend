import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand

from nickelodeon.models import MP3Song
from nickelodeon.utils import convert_audio, s3_object_url, s3_upload
from tqdm import tqdm

class Command(BaseCommand):
    help = "Add the missing duration of the songs in the library"

    def add_arguments(self, parser):
        parser.add_argument("-w", "--workers", type=int, default=1)

    def handle(self, *args, **options):
        songs = MP3Song.objects.select_related("owner").filter(duration=0)
        song_count = songs.count()
        i = 0
        try:
            with tqdm(song_count) as pbar:
                with ThreadPoolExecutor(max_workers=options.get("workers")) as executor:
                    future_to_song = {executor.submit(self.handle_song, song): song for song in songs}
                    for future in as_completed(future_to_song):
                        song = future_to_song[future]
                        # print(song.filename)
                        pbar.update(1)
        except KeyboardInterrupt:
            pass
        
    def handle_song(self, song):
        song.get_duration()
