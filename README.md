kevoladome
==========
Copyright Marko Grönroos 2014
Turun Ursa ry astronomical association

This project is a Raspberry Pi based dome controller of the zenith tower in the Kevola Observatory.

Kevola Observatory is owned and operated by Turun Ursa, the astronomical association
operating in Turku area in Finland.
  http://turunursa.fi/

The dome is a custom-made dome, with direction sensors, direction control motors,
and shutter control. The telescope is a 17 inch Planewave astrograph with a 10micron GM 3000 HPS
mount. The dome is controlled by reading the direction from the mount by the Ethernet protocol
and automatically following the motion of the mount.

Hardware
========

We use a Raspberry Pi B+ to control the dome.
The implementation of the motor control is undecided at the moment.

Dome Server
===========

The dome is controlled by the domeserver.py application, which must be run with root priviledges
to enable accessing the IO ports. The server runs by default in port 8080.

The architecture of the dome server is threaded;
the dome encoder and other services are run in their own threads, and
a web server interface for controlling the dome in one thread.

Dome Encoder
============

The direction encoding is done by three switches: two overlapping magnets and a reset switch
at the south direction.

Implemented as the DirectionService in the dome server.

Dome Rotator
============

Will rotate the dome using a motor according to commands.

To be implemented.

Mount Client
============

The mount client will communicate with the mount to read its current pointing direction.
Then, the client will command the dome to turn to the direction of the telescope.

To be implemented.
