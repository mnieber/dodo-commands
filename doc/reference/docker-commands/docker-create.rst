docker-create
=============

If your environment depends on docker data containers, then you can store their configuration in ``$(/DOCKER/container_types}``:

.. code-block:: yaml

    DOCKER:
      container_types:
        mongodb:
            image: foobar:base
            dirs:
            - /var/lib/mongodb

Now, running ``dodo docker-create mongodb dc_mongodb`` will create a new docker container (with name ``dc_mongodb``) based on the ``foobar:base`` image. This container can be used in a ``volumes_from_list`` to persist the contents of the ``/var/lib/mongodb`` directory:

.. code-block:: yaml

    DOCKER_OPTIONS:
      django-manage:
        volumes_from_list:
        - dc_mongodb

For each container type, the ``docker-create`` command stores the name of the last created container in ``$(/DOCKER/containers}``, so you can also use:

.. code-block:: yaml

    DOCKER_OPTIONS:
      django-manage:
        volumes_from_list:
        - ${/DOCKER/containers/mongodb}
