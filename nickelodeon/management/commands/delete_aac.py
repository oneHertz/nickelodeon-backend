import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand

from nickelodeon.models import MP3Song
from nickelodeon.utils import s3_object_delete, s3_object_exists
from tqdm import tqdm

class Command(BaseCommand):
    args = ["workers"] 
    help = "Delete te AACs"

    def add_arguments(self, parser):
        parser.add_argument("-w", "--workers", type=int, default=1)

    def handle(self, *args, **options):
        songs = MP3Song.objects.select_related("owner")
        song_count = songs.count()
        try:
            with tqdm(total=song_count, unit="song") as pbar:
                with ThreadPoolExecutor(max_workers=options.get("workers")) as executor:
                    future_to_song = {executor.submit(self.handle_song, song): song for song in songs}
                    for future in as_completed(future_to_song):
                        song = future_to_song[future]
                        pbar.update(1)
        except KeyboardInterrupt:
            pass
        
    def handle_song(self, song):
        file_path = song.get_file_format_path("aac").encode("utf-8")
        if s3_object_exists(file_path):
            s3_object_delete(file_path)