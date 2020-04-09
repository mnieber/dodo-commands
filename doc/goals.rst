Dodo Commands, who and what is it for?
======================================

The main goal of Dodo Commands is to make it easier to run a variety of scripts and commands from the command line. Below we will describe a few scenarios in which Dodo Commands can be useful. In the next chapter, we will explain how Dodo Commands can be set up to support these scenarios.


Scenario: working with micro-services
-------------------------------------

Working with micro-services by definition involves working with multiple environments, where each environment offers specific commands. Typically these commands are organized in a Makefile or package.json file. Dodo Commands allows you to use these files from any directory. For example, use `dodo foo.make bar` to call the `bar` function for the Foo micro-service, and use `dodo foo.git log` to see the git history of this micro-service. Moreover, Dodo Commands makes it easy to show the console output of different services in a single screen using tmux.


Scenario: local development with Docker
---------------------------------------

It's a good idea to install the entire tool-chain that is needed for local development in one or more Docker containers. This isolates the run-time environment from the host computer. Dodo Commands makes it easy to execute commands inside these containers. For example, if you have a Makefile inside the Foo service container, then you can use it (from the host computer) by calling `dodo foo.make test`. Dodo commands will take care of prefixing the command with the right Docker arguments, so that it will run successfully in the container.


Scenario: using project-specific sets of aliases
------------------------------------------------

Shell aliases are useful but they also have some drawbacks. You need to make sure that you load the right set of aliases for your current project into the shell. If you reuse your aliases between projects, then it can be challenging to maintain sets of similar but slightly different aliases. Finally, for more complex aliases it would make sense to use a powerful language such as Python instead of shell script. With Dodo Commands, you can write your aliases and functions as Python scripts. These aliases can read some of their arguments from a project specific configuration file. This helps to keep them short and makes them reusable between projects.


Scenario: getting colleagues up-to-speed
----------------------------------------

There are usually some steps that every developer needs to take when they join a project. You can describe these steps in a README but a more effective way is to automate them. With Dodo Commands, you can write setup scripts for your project that can be invoked as simple commands. You can group these commands into menus that can be accessed by calling `dodo menu`. Moreover, new developers can run these commands with the `--confirm` flag. This prints each step and asks for confirmation, giving new developers the chance to understand what happens in each script.