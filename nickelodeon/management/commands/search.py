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
            if (replace_str := options["replace"]) is None:
                for song in songs:
                    text_to_print = song.filename.replace(
                        options["query"], f"\033[92m{options["query"]}\033[0m"
                    )
                    print(text_to_print)
            else:
                for song in songs:
                    target = song.filename.replace(options["query"], replace_str)
                    text_to_print = song.filename.replace(
                        options["query"],
                        f"\033[91m{options["query"]}\033[0m\033[92m{replace_str}\033[0m",
                    )
                    print(text_to_print)
                    if not options["dryrun"]:
                        song.move_file_to(target)
                        song.save()
        except KeyboardInterrupt:
            pass
