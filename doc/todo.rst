.. _todo:

*****
To do
*****

- git-pull-default-project is broken. Also, add a default project setting in the root. The diff command should diff with respects to that default project. This allows the workflow:
dodo-activate --create git@foo...git

- add (beta) version number to dodo_commands
- allow to activate the foo/FooBar OR if it's not ambiguous the FooBar project
- the dodo bootstrap command reads bootstrap.yml from the dodo_commands dir and copies over
the real project config





Nice to have
------------
- allow to tag the command in its meta file, and list commands with certain tags
- completion not working inside braces
- completion in other shells
