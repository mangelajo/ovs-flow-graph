
This project is a little renderer to watch openflow rules as graphs.

At this moment it's highly immature, and just a proof of concept.

TO-DO
-----

If the project proves to be useful/interesting, several refactors
would be interesting:

[ ] order rows by bytes and idle time

[ ] Make a better parser for ofctl-dump or get the table entries ourselves
    (no parsing) At this moment it's a dirty LL(1) grammar on the actions part,
    and string splitting  before that.

[x] Refactor dot generation as Model/View

[x] Tiny twisted based server, to allow connection via http for watching
    live rules.


