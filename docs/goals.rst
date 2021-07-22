Dodo Commands, who and what is it for?
======================================

The main goal of Dodo Commands is to make it easier to run a variety of scripts and commands from the command line. Below we will describe two scenarios in which Dodo Commands can be useful. In the next chapter, we will explain how Dodo Commands can be set up to support these scenarios.


Scenario: working with micro-services running in containers
-----------------------------------------------------------

Imagine that you have a Frontend and a Backend microservice running in Docker containers. How would you open a shell in one of these containers? With Dodo Commands you would type `dodo backend.shell` or `dodo frontend.shell`. How about running the backend Python tests and saving the output to an html file? That would be `dodo backend.pytest`.

In general, Dodo Commands tries to reduce typing and mental overhead by compressing commands in the shortest possible alias. These aliases expand to scripts that are either ready-made or custom-made (by you). The scripts access the project-specific dodo configuration to read parameters (such as the pytest html file location).


Scenario: getting colleagues up-to-speed
----------------------------------------

Becoming productive in a development environment means being able to easily
execute all the tasks that are commonly required. This involves setting up software and developing an efficient workflow. If every developer writes their
own set of aliases then you waste of potential for sharing best practices.
With dodo commands you can share scripts between projects and between developers,
maximizing reuse and promoting a uniform workflow.
When a new developer bootstraps their environment by cloning the Dodo Commands
configuration, then they will have all the main tasks available to them
as convenient and easy to discover aliases. You can group commands into menus that can be accessed by calling `dodo menu`. Moreover, when developers run these commands with the `--confirm` flag then they will be asked for confirmation at each step in the script, giving them the chance to follow what happens in each script.