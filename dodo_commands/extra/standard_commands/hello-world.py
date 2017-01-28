"""Print hello world."""
from dodo_commands.framework import BaseCommand


class Command(BaseCommand):  # noqa
    def handle(self, *args, **kwargs):  # noqa
        print ("Hello world")
