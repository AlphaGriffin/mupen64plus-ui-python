::

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
=====

M64Py is a Qt5 front-end (GUI) for Mupen64Plus, a cross-platform
plugin-based Nintendo 64 emulator. Front-end is written in Python and it
provides a user-friendly interface over the Mupen64Plus shared library.

Features
========

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
============

* `PyQt5 <https://www.riverbankcomputing.com/software/pyqt/download5>`_ (QtCore, QtGui, QtWidgets, QtOpenGL)
* `PySDL2 <https://pysdl2.readthedocs.io>`_

Ubuntu
++++++

``sudo apt-get install python-pyqt5 pyqt5-dev-tools python-pyqt5.qtopengl
libsdl2-dev``

PyPi
++++

To install just the Python dependencies:

``pip install -r requirements.txt --user``

.. note::

  This will not install the other system dependencies which are listed above.

  You can also drop the ``--user`` flag and run as root user if you want to
  install system-wide, but this is not recommended, as this will likely
  screw up your distro's package management.

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
=======

First, run ``python setup.py build`` followed by  ``python setup.py install``
to install

.. code::

  python setup.py build
  python setup.py install --user

.. note::

  If you use the ``--user`` flag, make sure ``~/.local/bin`` is in your
  user's path environment variable.

License
=======

M64Py is free/libre software released under the terms of the GNU GPL license.
Please see the ``COPYING`` file for details.
