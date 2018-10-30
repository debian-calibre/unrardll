unrardll
==========

|pypi| |unix_build| |windows_build| 

Python wrapper for the `UNRAR DLL <http://www.rarlab.com/rar_add.htm>`_.

Usage
-------

.. code-block:: python

    from unrardll import extract
    extract(archive_path, destination_directory)  # extract everything

    from unrardll import names
    print(list(names(archive_path)))  # get list of filenames in archive

    from unrardll import headers
    from pprint import pprint
    pprint(list(headers(archive_path)))  # get list of file headers in archive

    from unrardll import extract_member
    # Extract a single file using a predicate function to select the file
    filename, data = extract_member(archive_path, lambda h: h['filename'] == 'myfile.txt')

    from unrardll import comment
    print(comment(archive_path))  # get the comment from the archive


Installation
--------------

Assuming that the RAR dll is installed and the RAR headers available in the
include path.

.. code-block:: bash

    pip install unrardll

You can set the environment variables ``UNRAR_INCLUDE`` and ``UNRAR_LIBDIRS``
to point to the location of the unrar headers and library file.

See the ``ci.py`` file for a script to install the unrar dll from source, if
needed. This is used on the continuous integration servers.


.. |pypi| image:: https://img.shields.io/pypi/v/unrardll.svg?label=version
    :target: https://pypi.python.org/pypi/unrardll
    :alt: Latest version released on PyPi

.. |unix_build| image:: https://api.travis-ci.org/kovidgoyal/unrardll.svg
    :target: http://travis-ci.org/kovidgoyal/unrardll
    :alt: Build status of the master branch on Unix

.. |windows_build|  image:: https://ci.appveyor.com/api/projects/status/github/kovidgoyal/unrardll?svg=true
    :target: https://ci.appveyor.com/project/kovidgoyal/unrardll
    :alt: Build status of the master branch on Windows


