freeway
=======

Freeway is a module for managing file system structures with recursive pattern rules.

Install freeway
^^^^^^^^^^^^^^^

This module can be installed from PyPi, as follows:

.. code-block:: bash

    $ pip install freeway


Some usage examples
===================

Examples require the RULESFILE environment variable to be set, which points to a JSON file that contains all the rule patterns to resolve the paths and nomenclatures.
The file can be found at 'freeway/examples/rules.json'

Parse data from path
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from freeway import Freeway
    filepath = "C:/example/assets/Characters/Roberto/MOD/Work/example_CH_Roberto_MOD.v001.abc"
    myPath = Freeway(filepath)

    # Show all parsed data
    print(myPath)

Result::

    ['assetWorkspacePath']: {'assetType': 'Characters', 'asset': 'Roberto', 'process': 'MOD', 'stage': 'Work', 'assetPrefix': 'CH', 'task': 'MOD', 'version': '001', 'ext': 'abc'}

Use parsed data
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    print("%s_%s_%s_example" % (myPath.asset, myPath.assetType, myPath.task))

Results::

    Roberto_Characters_MOD_example

Use parsed data for make new paths
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    print(myPath.assetDir)

Results::

    C:/example/assets/Characters/Roberto

Make a path from data
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    data = {'assetType': 'Prop',
            'asset': 'Table',
            'process': 'MOD',
            'stage': 'Work',
            'assetPrefix': 'PR',
            'task': 'MOD',
            'version': '001',
            'ext': 'abc'}

    myPath = Freeway(**data)

    print(myPath.assetWorkspacePath)
    print(myPath.assetFile)
    print(myPath.assetDir)

Results::

    C:/example/assets/Prop/Table/MOD/Work/example_PR_Table_MOD.v001.abc
    example_Prop_Table_MOD_v001.abc
    C:/example/assets/Prop/Table

Modify parsed data to make new paths
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    other = myPath.copy()
    myPath.stage = "Publish"
    myPath.ext = "usd"
    myPath.asset = "Chair"
    print(myPath.assetWorkspacePath)

Results::

    C:/example/assets/Prop/Chair/MOD/Publish/example_PR_Chair_MOD.v001.usd

Or also
^^^^^^^

.. code-block:: python

    other.update({"process": "SHD",
                  "ext": "mb",
                  "version": "123"})

    print(other.assetWorkspacePath)

Results::

    C:/example/assets/Prop/Table/SHD/Work/example_PR_Table_MOD.v123.mb