docker-build
============

When referring to a docker image in ``$(/DOCKER_OPTIONS/<pattern>/image}``, you may also need to ensure this image is built. The details for building an image are specified in ``$(/DOCKER_IMAGES}``:

.. code-block:: yaml

    DOCKER_IMAGES:
      'base':
        image: foobar:base
        build_dir: ${/ROOT/src_dir}/docker/base

Running ``dodo docker-build base`` builds the image:

.. code-block:: bash

    dodo docker-build --confirm base

    # outputs something like:
    (/home/maarten/projects/foobar/src/docker/base) docker build -t foobar:base -f Dockerfile .

    continue? [Y/n]
