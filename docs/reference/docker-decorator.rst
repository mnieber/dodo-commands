.. _docker_support:

The docker decorator
====================

If the "docker" decorator is used, then all command lines will be prefixed with ``/usr/bin/docker run`` and related docker arguments found in ``$(/DOCKER_OPTIONS/<pattern>``. Here, ``<pattern>`` matches the name of the current dodo command. For example, consider this configuration:

.. code-block:: yaml

    DOCKER_OPTIONS:
      # * will match any name
      '*':
        image: foobar:base
        volume_map:
          ${/ROOT/src_dir}: /srv/foobar/src
      # docker options when running the 'django-manage' command
      'django-manage':
        extra_options:
        - '--publish=127.0.0.1:27017:27017'

Running the ``django-manage`` command will produce something like this:

.. code-block:: bash

    # note that docker options for django-manage are looked up in ${/DOCKER_OPTIONS}
    # where it will match with '*' and 'django-manage'
    dodo django-manage --echo

    # outputs:
    docker run
        --rm --interactive --tty
        --name=django-manage
        --volume=/home/maarten/projects/foobar/src:/srv/foobar/src
        --publish=127.0.0.1:80:80
        foobar:base
        python manage.py


``$(/DOCKER_OPTIONS/<pattern>/image}``
--------------------------------------

Identifies the docker image.


``$(/DOCKER_OPTIONS/<pattern>/name}``
-------------------------------------

Used to name the docker docker container (defaults to the name of the dodo command).


``$(/DOCKER_OPTIONS/<pattern>/volume_map}``
-------------------------------------------

Each key-value pair will be added as a docker volume (where 'key' in the host maps to 'value' in the docker container)


``$(/DOCKER_OPTIONS/<pattern>/volume_map_strict}``
--------------------------------------------------

Each key-value pair is added as a docker volume. If the key does not exist as a local path, an error is raised.


``$(/DOCKER_OPTIONS/<pattern>/volume_list}``
--------------------------------------------

Each item will be added as a docker volume (where 'item' in the host maps to 'item' in the docker container)


``$(/DOCKER_OPTIONS/<pattern>/publish_map}``
--------------------------------------------

Each key-value pair will be added as a docker published port


``$(/DOCKER_OPTIONS/<pattern>/publish_list}``
---------------------------------------------

Each item will be added as a docker published port


``$(/DOCKER_OPTIONS/<pattern>/volumes_from_list}``
--------------------------------------------------

Each item will be added as a docker "volumes_from" argument


``$(/DOCKER_OPTIONS/<pattern>/link_list}``
------------------------------------------

Each item will be added as a docker "link" argument


``$(/DOCKER_OPTIONS/<pattern>/variable_list}``
----------------------------------------------

Each environment variable will be added as an environment variable in the docker container. Variables in ``variable_list`` have the same name in the host and in the container.


``$(/DOCKER_OPTIONS/<pattern>/variable_map}``
---------------------------------------------

Each key-value pair will be added as an environment variable in the docker container.


``${/DOCKER_OPTIONS/<pattern>/extra_options}``
----------------------------------------------

Key-value pairs are passed as extra options to the docker command line call.


``$(/ENVIRONMENT/variable_map}``
--------------------------------

Each key-value pair will be added as an environment variable in the docker container.


``$(/DOCKER_OPTIONS/<pattern>/rm}``
-----------------------------------

Decides if the docker container is automatically removed (defaults to True).


``$(/DOCKER_OPTIONS/<pattern>/is_interactive}``
-----------------------------------------------

Decides if the ``-i`` and ``-t`` flags are added.


Matching multiple names
-----------------------

It's possible to match multiple names using a list:

.. code-block:: yaml

    DOCKER_OPTIONS:
      ['django-manage', 'django-runserver']:
        extra_options:
        - '--publish=127.0.0.1:27017:27017'

Patterns starting with '!' indicate names that should be excluded:

.. code-block:: yaml

    DOCKER_OPTIONS:
      # match django-manage but not django-runserver
      ['django-*', '!django-runserver']:
        extra_options:
        - '--publish=127.0.0.1:27017:27017'
