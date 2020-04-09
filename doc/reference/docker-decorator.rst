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


#. The value of ``$(/DOCKER_OPTIONS/<pattern>/image}`` is used to identify the docker image.

#. The value of ``$(/DOCKER_OPTIONS/<pattern>/name}`` is used to name the docker docker container (defaults to the name of the dodo command).

#. each key-value pair in ``$(/DOCKER_OPTIONS/<pattern>/volume_map}`` will be added as a docker volume (where 'key' in the host maps to 'value' in the docker container)

#. each key-value pair in ``$(/DOCKER_OPTIONS/<pattern>/volume_map_strict}`` is also added as a docker volume. If the key does not exist as a local path, an error is raised.

#. each item in ``$(/DOCKER_OPTIONS/<pattern>/volume_list}`` will be added as a docker volume (where 'item' in the host maps to 'item' in the docker container)

#. each key-value pair in ``$(/DOCKER_OPTIONS/<pattern>/publish_map}`` and each item in ``$(/DOCKER_OPTIONS/<pattern>/publish_list}`` will be added as a docker published port

#. each item in ``$(/DOCKER_OPTIONS/<pattern>/volumes_from_list}`` will be added as a docker "volumes_from" argument

#. each item in ``$(/DOCKER_OPTIONS/<pattern>/link_list}`` will be added as a docker "link" argument

#. each environment variable listed in ``$(/DOCKER_OPTIONS/<pattern>/variable_list}`` or ``$(/DOCKER_OPTIONS/<pattern>/variable_map}`` will be added as an environment variable in the docker container. Variables in ``variable_list`` have the same name in the host and in the container.

#. arguments in ``${/DOCKER_OPTIONS/<pattern>/extra_options}`` are passed as extra options to the docker command line call.

#. each key-value pair in ``$(/ENVIRONMENT/variable_map}`` will be added as an environment variable in the docker container.

#. The docker container is automatically removed depending on ``$(/DOCKER_OPTIONS/<pattern>/rm}`` (defaults to True).

#. the ``-i`` and ``-t`` flags are added unless the ``$(/DOCKER_OPTIONS/<pattern>/is_interactive}`` flag is set to ``False``.


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
