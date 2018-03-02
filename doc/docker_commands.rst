.. _docker_support:

**************
Docker support
**************

The docker decorator
====================

If the "docker" decorator is used, then all command lines will be prefixed with ``/usr/bin/docker run`` and related docker arguments found in ``$(/DOCKER/options/<pattern>``. Here, ``<pattern>`` matches the name of the current dodo command. For example, consider this configuration:

.. code-block:: yaml

    DOCKER:
      options:
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

    dodo django-manage --echo

    # outputs:
    docker run
        --rm --interactive --tty
        --name=django-manage
        --volume=/home/maarten/projects/foobar/src:/srv/foobar/src
        --publish=127.0.0.1:80:80
        foobar:base
        python manage.py


#. The value of ``$(/DOCKER/options/<pattern>/image}`` is used to identify the docker image.

#. The value of ``$(/DOCKER/options/<pattern>/name}`` is used to name the docker docker container (defaults to the name of the dodo command).

#. each key-value pair in ``$(/DOCKER/options/<pattern>/volume_map}`` will be added as a docker volume (where 'key' in the host maps to 'value' in the docker container)

#. each item in ``$(/DOCKER/options/<pattern>/volume_list}`` will be added as a docker volume (where 'item' in the host maps to 'item' in the docker container)

#. each item in ``$(/DOCKER/options/<pattern>/volumes_from_list}`` will be added as a docker "volumes_from" argument

#. each item in ``$(/DOCKER/options/<pattern>/link_list}`` will be added as a docker "link" argument

#. each environment variable listed in ``$(/DOCKER/options/<pattern>/variable_list}`` or ``$(/DOCKER/options/<pattern>/variable_map}`` will be added as an environment variable in the docker container. Variables in ``variable_list`` have the same name in the host and in the container.

#. arguments in ``${/DOCKER/options/<pattern>/extra_options}`` are passed as extra options to the docker command line call.

#. each key-value pair in ``$(/ENVIRONMENT/variable_map}`` will be added as an environment variable in the docker container.

#. The docker container is automatically removed depending on ``$(/DOCKER/options/<pattern>/rm}`` (defaults to True).

#. the ``-i`` and ``-t`` flags are added unless you pass the ``--non-interactive`` flag when running the dodo command.


Aliases
=======
Sometimes it's convenient to use the same docker settings for multiple commands. To use the docker settings for ``bar`` also when running the ``foo`` command, use:

.. code-block:: yaml

    DOCKER:
      aliases:
        foo: bar


The dockerbuild command
=======================

Though you can refer to a docker image in ``$(/DOCKER/options/<pattern>/image}``, you may also needs to ensure this image is built. The details for building an image are specified in ``$(/DOCKER/images}``:

.. code-block:: yaml

    DOCKER:
      images:
        'base':
          image: foobar:base
          build_dir: ${/ROOT/src_dir}/docker/base

Running ``dodo dockerbuild base`` builds the image:

.. code-block:: bash

    dodo dockerbuild --confirm base

    # outputs something like:
    (/home/maarten/projects/foobar/src/docker/base) docker build -t foobar:base -f Dockerfile .

    continue? [Y/n]


The dockerexec command
======================

To inspect a running docker container, run ``dodo dockerexec``. This will print a list of running containers, allowing you to select one. A bash shell will be opened giving you access to the container.


The dockercreate command
========================

If your environment depends on docker data containers, then you can store their configuration in ``$(/DOCKER/container_types}``:

.. code-block:: yaml

    DOCKER:
      container_types:
        mongodb:
            image: foobar:base
            dirs:
            - /var/lib/mongodb

Now, running ``dodo dockercreate mongodb dc_mongodb`` will create a new docker container (with name ``dc_mongodb``) based on the ``foobar:base`` image. This container can be used in a ``volumes_from_list`` to persist the contents of the ``/var/lib/mongodb`` directory:

.. code-block:: yaml

    DOCKER:
      options:
        django-manage:
          volumes_from_list:
          - dc_mongodb

For each container type, the ``dockercreate`` command stores the name of the last created container in ``$(/DOCKER/containers}``, so you can also use:

.. code-block:: yaml

    DOCKER:
      options:
        django-manage:
          volumes_from_list:
          - ${/DOCKER/containers/mongodb}
