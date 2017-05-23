=====
m64py
=====

                  _____ __ __
       ____ ___  / ___// // / ____  __  __
      / __ `__ \/ __ \/ // /_/ __ \/ / / /
     / / / / / / /_/ /__  __/ /_/ / /_/ /
    /_/ /_/ /_/\____/  /_/ / .___/\__, /
                          /_/    /____/
        http://m64py.sourceforge.net
        A frontend for Mupen64Plus


    /-\  |_  |*  |-|  /-\        {_,  |`  |  |= |=  |  |\|

        Alpha Griffin Edition
        http://alphagriffin.com


.. contents:: Table of Contents
.. toctree::
   API Documentation <api/modules>


About
-----

M64Py is a Qt5 front-end (GUI) for Mupen64Plus, a cross-platform
plugin-based Nintendo 64 emulator. Front-end is written in Python and it
provides a user-friendly interface over Mupen64Plus shared library.

**Alpha Griffin Edition**

The Alpha Griffin Edition showcases new advancements in machine learning
with TensorFlow, allowing the emulator to learn by watching the player's
games.

Features
--------

* Changeable emulation plugins for audio, core, input, rsp, video
* Selection of emulation core
* Configuration dialogs for core, plugin and input settings
* ROMs list with preview images
* Input bindings configuration
* Cheats support
* Support gzip, bzip2, zip, rar and 7z archives
* Video extension (embedded OpenGL window)

**Alpha Griffin Edition**

* Game recorder for capturing the player's games
* Training system to train models for playing
* Game player for playing trained models in new levels

Dependencies
------------

* [PyQt5](https://www.riverbankcomputing.com/software/pyqt/download5) (QtCore, QtGui, QtWidgets, QtOpenGL)
* [PySDL2](https://pysdl2.readthedocs.io)

**Alpha Griffin Edition**

Additional dependencies are required for the Alpha Griffin Edition machine learning support:

* [Matplotlib](http://matplotlib.org)
* [CUDA](https://developer.nvidia.com/cuda-downloads) (recommended but not required)
* [TensorFlow](https://www.tensorflow.org/install/)
* [Pandas](http://pandas.pydata.org)
* [Pygame](http://www.pygame.org)
* [Pillow](https://python-pillow.org) (fork of Python Imaging Library)
* [aglog](http://github.com/AlphaGriffin/logpy)

Install
-------

Run *python setup.py install* to install

Run *python setup.py build_qt* before you can start ./m64py from source dir

License
-------

M64Py is free/libre software released under the terms of the GNU GPL license,
see the `COPYING' file for details.

