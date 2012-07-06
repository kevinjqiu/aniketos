Aniketos
========

[Aniketos](http://www.theoi.com/Ouranios/AniketosAlexiares.html) is one of two gatekeepers of [Mount Olympus](http://en.wikipedia.org/wiki/Mount_Olympus). It also keeps your git repository from pushes that don't fit your project standards.

Why
---

Imagine you have a project, and you have your coding convention setup, or even have a Jenkins job that runs a linter on every push. Now one of your colleague comes alone, who isn't too familiar with the coding conventions. He checks in some code that violates the standard, pushes and breaks the build. Wouldn't it be nice if the git repository can run the linter on the pushed files, and reject the push if it's not up-to-par? This way, your colleague gets immediate feedback and can learn the conventions faster.

This is where Aniketos can help. [Hate](http://stopwritingramblingcommitmessages.com/) long rambling commit messages? Write a Aniketos checker that rejects those pushes. Some commits don't have a reference to a ticket? Write a Aniketos checker that rejects those pushes.

How it works
------------

[Git](http://git-scm.com/) has this mechanism called 'hooks' which allows scripts to be executed when certain events happen to your repository. Aniketos can be used as the server `update` hook, which gets called before the server `ref` is updated.

Installation
------------

* If you're using [pip](http://www.pip-installer.org/)

```
pip install aniketos
```

* or with [EasyInstall](http://packages.python.org/distribute/easy_install.html)

```
easy_install aniketos
```

After `aniketos` is installed, invoke:

```
install-hook <repository-location>
```

You need write permission to `repository-location`. This will install aniketos to `<repository-location>/hooks/update`

Configure
---------

Deployment
----------

Git repo has the following layout:

    sample.git
    |-- HEAD
    |-- config
    |-- aniketos_config*
    |-- description
    |-- hooks
    |   |-- ...
    |   |-- update -> /path/to/aniketos/bin/update**
    |   `-- ...
    |-- info
    |   `-- exclude
    |-- objects
    |   |-- ...
    |   `-- ...
    `-- refs
        |-- heads
        |   `-- master
        `-- tags

The nodes with asterisks are the ones specific to aniketos.
