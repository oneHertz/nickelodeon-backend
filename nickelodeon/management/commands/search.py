from django.core.management.base import BaseCommand

from nickelodeon.models import MP3Song


class Command(BaseCommand):
    args = ["query"]
    help = "Add the missing durations for the songs in the library"

    def add_arguments(self, parser):
        parser.add_argument("-q", "--query", type=str, required=True)
        parser.add_argument("-r", "--replace", type=str, default=None)
        parser.add_argument("--dryrun", action="store_true")

    def handle(self, *args, **options):
        songs = (
            MP3Song.objects.select_related("owner")
            .filter(filename__contains=options["query"])
            .order_by("filename")
        )
        try:
            for song in songs:
                print(song.filename)
            print("")
            if (replace_str := options["replace"]) is not None:
                for song in songs:
                    target = song.filename.replace(options["query"], replace_str)
                    if not options["dryrun"]:
                        song.move_file_to(target)
                        song.save()
                    print(target)
        except KeyboardInterrupt:
            pass
