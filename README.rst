unrardll
==========

|pypi| |build|

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

See the :file:`.github/workflows/ci.py` file for a script to install the unrar
dll from source, if needed. This is used on the continuous integration servers.


.. |pypi| image:: https://img.shields.io/pypi/v/unrardll.svg?label=version
    :target: https://pypi.python.org/pypi/unrardll
    :alt: Latest version released on PyPi

.. |build| image:: https://github.com/kovidgoyal/unrardll/workflows/CI/badge.svg
    :target: https://github.com/kovidgoyal/unrardll/actions?query=workflow%3ACI"
    :alt: Build status of the master branch
