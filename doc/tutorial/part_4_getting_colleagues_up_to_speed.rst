.. _tutorial_part4:

Scenario: getting colleagues up-to-speed
========================================

If someone joins your project, then it makes sense to share your working environment with them.
At the same time, you want working environments to be independent, so that each project member
can arrange it to their preferences. This is achieved by having a shared configuration from
which you cherry-pick the parts you need.

We will continue where we left off in part 3 (:ref:`tutorial_part3`). If you haven't done the
steps of the previous scenario, run this to get started:

.. code-block:: bash

  cd /tmp
  git clone git@github.com:mnieber/dodo_commands_tutorial.git

  # Copy the end state of part 3 of the tutorial
  cp -rf ./dodo_commands_tutorial/part3/after ./tutorial

  # Create and activate a dodo environment for our project
  cd ./tutorial
  $(dodo env --init tutorial)


Preparing the configuration files for sharing
---------------------------------------------

Let's start by activating the `tutorial` environment:

.. code-block:: bash

  $(dodo env tutorial)


If you followed the tutorial so far (or the steps at the start of this tutorial to create a
starting point) then we currently have a working Dodo Commands configuration in
`/tmp/tutorial/.dodo_commands`, and some scripts in ``/tmp/tutorial/commands``. We want to share
this configuration with colleagues. The first step we will take is to move some files into a ``src``
directory that we can add to git:

.. code-block:: bash

  cd /tmp/tutorial
  mkdir src
  mv commands/ docker-compose.yml Dockerfile reader/ writer/ time.log src/

  cd src
  git init
  git add *
  git commit -m "First commit"

      [master (root-commit) 56f79a1] First commit
       9 files changed, 77741 insertions(+)
       create mode 100644 Dockerfile
       create mode 100644 commands/greet.py
       create mode 100644 commands/mk.meta
       create mode 100644 commands/mk.py
       create mode 100644 docker-compose.yml
       create mode 100644 reader/Makefile
       create mode 100644 time.log
       create mode 100644 writer/Makefile
       create mode 100644 writer/write_periodically.py


We're not adding the ``.dodo_commands`` directory to git, because then the
ownership of these files will become a problem. It's better if each developer can tweak the
configuration to their liking. Therefore, we will copy our configuration files to a new
location inside ``/tmp/tutorial/src`` and consider this copy to be the shared configuration:

.. code-block:: bash

  cd /tmp/tutorial
  mkdir -p ./src/extra/dodo_commands
  cp -rf .dodo_commands ./src/extra/dodo_commands/config

  cd src
  git add *
  git commit -m "Add shared configuration files"

      [master de33a3f] Add shared configuration files
       4 files changed, 39 insertions(+), 5 deletions(-)
       create mode 100644 extra/dodo_commands/config/config.yaml
       create mode 100644 extra/dodo_commands/config/docker.yaml
       create mode 100644 extra/dodo_commands/config/server.reader.yaml
       create mode 100644 extra/dodo_commands/config/server.writer.yaml

Finally, we will add the ``${/ROOT/config/shared_config_dir}`` key to tell Dodo Commands
where the shared configuration files are:

.. code-block:: yaml

  ROOT:
    # Keep the rest of the settings as they are
    src_dir: ${/ROOT/project_dir}/src
    shared_config_dir: ${/ROOT/src_dir}/extra/dodo_commands/config

Now, we can compare our local configuration files to the shared files as follows:

.. code-block:: bash

  dodo diff --confirm

      (/tmp) meld \
        /tmp/tutorial/src/extra/dodo_commands/config \
        /tmp/tutorial/.dodo_commands/.

When you run this command then ``meld`` will tell us that the ``config.yaml`` file has
changed. You can double click on this file to get a detailed view of the differences.
In this view, you can copy the local changes (remember, we added a ``shared_config_dir``
key to the ``ROOT`` section) over to the shared file. Since this means that we have a
new version, it's a good habit to also bump the ``${/ROOT/version}`` key in both files.
Finally, you can add the changes in ``/tmp/tutorial/src/extra/dodo_commands/config/config.yaml``
to git and commit them:

.. code-block:: bash

  cd /tmp/tutorial/src
  git add *
  git commit -m "Update shared configuration files"

      [master 256a23b] Update shared configuration files
       1 file changed, 3 insertions(+), 1 deletion(-)

.. note::

  The purpose of ``${/ROOT/version}`` is to track the version of the configuration
  file. If the version in the local file is smaller than the version in the shared file, then
  it means that your colleague added something to the shared file. In this case, use
  ``dodo diff`` to synchronize your local file with the shared one. When you are done, make
  sure to edit the ``${/ROOT/version}`` value so that it's the same as the value in the shared file (this marks
  the fact that you are up-to-date with the shared configuration).


Bootstrapping a Dodo Commands environment
-----------------------------------------

We are now ready to let a colleague work on our project. This colleague will also create a `tutorial`
environment on their computer. However, to similate this situation on our computer, we will create
an environment named `colleague` and pretend that this is the "tutorial" environment that they will use.
We will use the ``bootstrap`` command to initialize it. This will provide our colleage with a copy of the
configuration files that we just added to git:

.. code-block:: bash

  $(dodo env --create colleague)
  dodo bootstrap --git-url=/tmp/tutorial/src src extra/dodo_commands/config --confirm

      (/tmp) mkdir -p /home/maarten/projects/colleague

      confirm? [Y/n]

      (/tmp) cp -rf \
        ~/projects/colleague/src/extra/dodo_commands/config/config.yaml
        ~/projects/colleague/.dodo_commands/config.yaml

      Copying shared environment files to your local environment...

      Warning, destination path already exists: ~/projects/colleague/.dodo_commands/config.yaml. Overwrite it?
      confirm? [Y/n]

      (/tmp) cp -rf
        ~/projects/colleague/src/extra/dodo_commands/config/server.writer.yaml
        ~/projects/colleague/.dodo_commands/server.writer.yaml
      confirm? [Y/n]

      (/tmp) cp -rf
        ~/projects/colleague/src/extra/dodo_commands/config/server.reader.yaml
        ~/projects/colleague/.dodo_commands/server.reader.yaml
      confirm? [Y/n]

      (/tmp) cp -rf
        ~/projects/colleague/src/extra/dodo_commands/config/docker.yaml
        ~/projects/colleague/.dodo_commands/docker.yaml
      confirm? [Y/n]

Because we used the ``--confirm`` flag, the command asks permission to copy the shared
configuration files to our local configuration directory. Let's look at the arguments that
were supplied in the call to ``bootstrap``:

- We used a ``--git-url`` that points to our local git repository. Usually you would use
  a remote git url.
- The repository is cloned to the ``src`` subdirectory of colleague's project directory.
- The shared configuration files are copied from the ``extra/dodo_commands/config`` location
  (which is relative to ``src``) to the configuration directory of colleague.


Details: Checking the config version
------------------------------------

When your colleague changes their local configuration files, they may decide at some point to
contribute these changes to the shared configuration files. Hopefully, they
will also bump the ``${/ROOT/version}`` value when they do. Whenever you pull the git repository
on which you both work, you can run the ``dodo check-version --config`` command to find out if the
shared configuration has changed. This command compares the ``${/ROOT/version}`` value in your local
configuration with the value in the shared configuration. Then, use ``dodo diff`` to synchronize
any changes.


Details: Checking the Dodo Commands version
-------------------------------------------

There is a similar (optional) value ``${/ROOT/required_dodo_commands_version}`` that is
used to check that you have the right version of Dodo Commands. The call ``dodo check-version --dodo``
verifies this. If you are using the ``autostart`` script to enable the last used environment
automatically when opening a shell, then these checks happen automatically (they are
part of the ``autostart`` script).


Details: Alternatives to git as the starting point
--------------------------------------------------

In the steps above, we cloned a git repository to obtain a ``src`` directory that has the shared
configuration files. However, there are other ways to obtain these files. First of all, you can
obtain the ``src`` directory from a cookiecutter template:

.. code-block:: bash

    dodo bootstrap --cookiecutter-url https://github.com/foo/foobar.git src extra/dodo_commands/config

Note that the cookiecutter url can also point to a directory on the local filesystem. Second, when you
already have a checked out monolithic source tree, then you can use any subdirectory of this tree as
the ``src`` directory of your new project:

.. code-block:: bash

    dodo bootstrap --link-dir ~/sources/monolith/foobar src extra/dodo_commands/config

Note that both examples look very similar to the case where git was used.
