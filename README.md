
This project is a little renderer to watch openflow rules as graphs.

At this moment it's highly immature, and just a proof of concept.

TO-DO
-----

If the project proves to be useful/interesting, several refactors
would be interesting:

* Make a better parser for ofctl-dump or get the table entries ourselves
  (no parsing) At this moment it's a dirty LL(1) grammar on the actions part,
    and string splitting  before that.

* Add a label with interface details, timestamp, server, etc...

* Get port information and include it into the graph


Installing in rhel/CentOS
-------------------------

yum install graphviz python-twisted python-jinja2 python-unittest2
