=======
hydrant
=======

Redirects stdin to Amazon Kinesis Firehose.


************
Installation
************

Install into a virtualenv.

.. code-block:: bash

    $ pip install --editable .


*****
Usage
*****

Pipe newline separated records into hydrant,
which will send each record to the delivery stream:

.. code-block:: bash

    $ producer | hydrant my-firehose-stream

Specify a region if not using ``us-east-1``:

.. code-block:: bash

    $ producer | hydrant --region='us-west-2' my-firehose-stream

Read the help text for more information:

.. code-block:: bash

    $ hydrant --help
