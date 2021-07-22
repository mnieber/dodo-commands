.. _tutorial_part2:

Scenario: local development with Docker
=======================================

We will continue the previous scenario (:ref:`tutorial_part1`) by Dockerizing the two services. If you haven't done the steps
of the previous scenario, run this to get started:

.. code-block:: bash

  cd /tmp
  git clone git@github.com:mnieber/dodo_commands_tutorial.git

  # Copy the end state of part 1 of the tutorial
  cp -rf ./dodo_commands_tutorial/part1/after ./tutorial

  # Create and activate a dodo environment for our project
  cd ./tutorial
  $(dodo env --init tutorial)


Running the docker-compose file
-------------------------------

Our services come with Docker files that we have not used so far.

.. code-block:: yaml

  cat /tmp/tutorial/docker-compose.yml

      version: "3"
      services:
        writer:
          image: dodo_tutorial
          build:
            dockerfile: ./Dockerfile
            context: .
          volumes:
            - ./writer:/app
            - ./time.log:/time.log
          working_dir: /app
          command: make runserver
        reader:
          depends_on: [writer]
          image: dodo_tutorial
          volumes:
            - ./reader:/app
            - ./time.log:/time.log
          working_dir: /app
          command: make runserver

  cat /tmp/tutorial/Dockerfile

      FROM python:3.7-alpine

      RUN apk add make

Let's test if it works:

.. code-block:: bash

  cd /tmp/tutorial
  docker-compose up

      Creating network "tutorial_default" with the default driver
      Creating tutorial_writer_1 ... done
      Creating tutorial_reader_1 ... done
      Attaching to tutorial_writer_1, tutorial_reader_1
      reader_1  | echo "Starting reader service"
      reader_1  | Starting reader service
      writer_1  | echo "Starting writer service"
      reader_1  | tail -f ../time.log
      writer_1  | Starting writer service
      reader_1  | 1586270720.460995


Using the docker-compose command
--------------------------------

We'd like to be able to bring this docker system up from any directory with the
``dodo docker-compose up`` command. To facilitate this, we'll create
a new configuration layer in ``/tmp/tutorial/.dodo_commands/docker.yaml``:

.. code-block:: yaml

  # /tmp/tutorial/.dodo_commands/docker.yaml
  DOCKER_COMPOSE:
    cwd: ${/ROOT/project_dir}

To enable this layer, we should add it to the ``LAYERS`` of the main configuration file.
Note that this layer is always loaded.

.. code-block:: yaml

  # /tmp/tutorial/.dodo_commands/config.yaml
  LAYERS:
  - docker.yaml

Now, when we run ``dodo docker-compose up`` it should start the docker system. Remember that
you can use the ``--confirm`` flag to see the command before it's executed. You can also use
the ``--echo`` flag for this purpose. The ``docker-compose`` command comes standard with
Dodo Commands. If you want to see its location and inspect its contents, you can use the
``dodo which`` command:

.. code-block:: bash

  dodo which docker-compose

      /some/path/to/dodo_docker_commands/docker-compose.py

.. tip::

  We could also have added the ``DOCKER_COMPOSE`` section directly to ``config.yaml``. It's
  up to you to decide when parts of the configuration should be moved to a separate layer file.


Details: Adding an alias for docker-compose up
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We can add an alias for ``docker-compose up`` so we don't have to type too much. With this
alias we can start the Docker system with ``dodo up``:

.. code-block:: yaml

  # /tmp/tutorial/.dodo_commands/config.yaml
  ROOT:
    # other stuff
    aliases:
      up: docker-compose up

Aliases that should be available in any environment can be added to the global configuration
file. To find out where this file lives run ``dodo which --global-config``. Let's add an alias
there for ``docker-compose up --detach``:

.. code-block:: ini

  # ~/.dodo_commands/config

  [alias]
  upd = docker-compose up --detach


When we try out the command with ``dodo upd`` it will start both containers.

Details: Preset docker commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dodo Commands comes with various useful commands to work with Docker containers. For example,
``dodo docker-kill`` will show you a menu in which you can select the container that you want to kill:

.. code-block:: bash

  dodo docker-kill

      1 - tutorial_writer_1
      2 - tutorial_reader_1
      Select a container:

The ``dodo docker-exec`` command lets you execute a command in a selected docker container.

.. code-block:: bash

  dodo docker-exec --cmd ls

      0 - exit
      1 - tutorial_reader_1
      2 - tutorial_writer_1

      Select a container:
      2
      Makefile               write_periodically.py


Running a command inside a container
------------------------------------

Let's add another command to the Makefile of the writer service:

.. code-block:: bash

  # /tmp/tutorial/writer/Makefile
  greeting:
    echo "Hello ${GREETING}"

We'll add a ``mk-greet.py`` script to ``/tmp/tutorial/commands`` that sets the ``GREETING``
environment variable and then runs ``make greeting``:

.. code-block:: python

  # /tmp/tutorial/commands/mk-greet.py
  from dodo_commands import Dodo

  Dodo.parser.add_argument("greeting")
  Dodo.run(
      ["make", "greeting", "GREETING=%s" % Dodo.args.greeting],
      cwd=Dodo.get("/MAKE/cwd")
  )

Remember that we have to run this as ``dodo writer.mk-greet`` so that the ``server.writer.yaml`` layer
is loaded. Let's see what it currently looks like:

.. code-block:: bash

  dodo writer.mk-greet hi --confirm

      (/tmp/tutorial/writer) make greeting GREETING=hi

      confirm? [Y/n]

This is not quite right yet, because we want to run this command in the ``tutorial_writer_1`` container.
To achieve this, we first need to tell Dodo Commands that the ``mk-greet`` command is dockerized:

.. code-block:: yaml

  # /tmp/tutorial/.dodo_commands/server.writer.yaml
  ROOT:
    # other stuff
    decorators:
      docker: [mk-greet]

Next, we need to specify in which container the ``mk-greet`` command should run:

.. code-block:: yaml

  # /tmp/tutorial/.dodo_commands/writer.yaml
  DOCKER_OPTIONS:
    mk-greet:
      container: tutorial_writer_1

Finally, we need to update the value of ``${/MAKE/cwd}}`` because it should point to a location
in the container:

.. code-block:: yaml

  # /tmp/tutorial/.dodo_commands/writer.yaml
  MAKE:
    cwd: /app

When we try again we see that the command is prefixed with the proper Docker arguments:

.. code-block:: bash

  dodo writer.mk-greet hi --confirm

      (/tmp/tutorial) docker exec  \
        --interactive --tty  \
        --workdir=/app  \
        tutorial_writer_1  \
        make greeting GREETING=hi

      confirm? [Y/n]

      echo "Hello hi"
      Hello hi

.. tip::

  The keys in the ``DOCKER_OPTIONS`` take wild-cards, so instead of ``mk-greet`` we could have used
  ``*``. In our example, this means that *any* dockerized script will use the
  ``tutorial_writer_1`` container.


Details: Inferred commands
--------------------------

If the ``mk-greet`` command is only used in combination with the ``writer`` layer then there is a way
to make the call even shorter. We can tell Dodo Commands that the ``writer`` layer is inferred by
the ``mk-greet`` command:

.. code-block:: yaml

  # /tmp/tutorial/.dodo_commands/config.yaml

  LAYER_GROUPS:
    server:
    - writer:
        inferred_by: [mk-greet]
    - reader

Now we can run ``dodo mk-greet hi`` instead of ``dodo writer.mk-greet hi``:

.. code-block:: bash

  dodo mk-greet hi --trace

      ['/usr/local/bin/dodo', 'mk-greet', 'hi', '--layer=server.writer.yaml']

.. warning::

  Because inferred commands are magical, they are also a bit dangerous. For this reason,
  it's only allowed to use them in the main ``config.yaml`` configuration file. Using them in
  layers has no effect. This makes it easier to reason about the configuration.
