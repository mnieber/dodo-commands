# noqa
from dodo_commands.extra.standard_commands import DodoCommand
import os
import ansible


class Command(DodoCommand):  # noqa
    help = ""
    decorators = ['docker']

    def add_arguments_imp(self, parser):  # noqa
        # parser.add_argument('foo')
        # parser.add_argument(
        #     '--bar',
        #     required=True,
        #     help=''
        # )
        pass

    def handle_imp(self, **kwargs):  # noqa
        ansible

        ansible_script = os.path.join(
            self.get_config("/ROOT/project_dir"),
            "ansible",
            "setup-computer.yml"
        )

        self.runcmd(
            [
                "ansible-playbook",
                ansible_script
            ]
        )
