.. _installation:

********************
The diagnose command
********************

When a colleague shares a Dodo Commands project with you, then you obtain a set of commands for working with this environment. However, to be in control, it's still required to understand how the commands work. Questions you will have include:

- which tasks are supported by the environment?
- which commands are available to perform these tasks?
- which configuration values are used by these commands?

This information needs to be documented. Dodo Commands supports this in a dynamic way through the `dodo diagnose` command.


Jinja2 documentation templates
------------------------------

Documentation is produced with `dodo diagnose` using the following workflow:

- the project author writes documentation in .rst (restructured text) files
- through the jinja2 templating system, these .rst files can inspect the local system and Dodo Commands configuration. This means that the documentation can directly report on issues with your local environment
- the `dodo diagnose` command invokes jinja2 and writes the rendered output into a output directory.
- finally, it renders the .rst files with sphinx and opens the result in the web browser.

Diagnose dodo configuration
---------------------------

The typical Dodo configuration for the diagnose command is:

.. yaml::

    DIAGNOSE:
        # Documentation .rst is read from here
        src_dir: ${/ROOT/src_dir}/extra/dodo_commands/diagnose

        # Rendered documentation is written here
        output_dir: ${/ROOT/project_dir}/res/diagnose

        # Import custom jinja2 filters and tests
        filters:
            - - ${/DIAGNOSE/src_dir}
              - filters

Note that you should have a `index.rst` file in the diagnose source directory, which has a table of contents that references the other .rst files.


The dodo_expand jinja2 filter
-----------------------------

The `dodo_exand` filter is used to print configuration values:

- to print a configuration value in the documentation output, use `{{ '/ROOT/some/key' | dodo_expand }}`

- if you want to print both the key and its value, use `{{ '/ROOT/some/key' | dodo_expand(key=True) }}`

- if you want to print the key and use the value as a browser link, use `{{ '/ROOT/some/key' | dodo_expand(link=True) }}`

- if the configuration value is a dictionary, then it's automatically placed in a yaml block layout that starts on a new line.

- you can force or disable this layout behaviour with the `layout` argument: `{{ '/ROOT/some/key' | dodo_expand(layout=True) }}`

- the `quote_key` and `quote_val` arguments control whether the key and value are printed between backtick quotes.
