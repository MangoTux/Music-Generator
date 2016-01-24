Random Music Generator
======================

Overview
--------

This is a project I've been working on when I have some free time. It randomly generates music, based off of certain musical scales and markov rhythm chains.
The project uses the [midiutil](https://code.google.com/p/midiutil/) library to build the music file. 

This is currently on a temporary hiatus, as class work is beginning to pick up.

Usage
-----

To compile and run the script, issue the command `python music.py [<instr>]`.  
If the instrument field is left blank, it will choose 3 or 4 instruments that should sound decent together.
The space-separated list of instruments are values from [this list](https://www.midi.org/specifications/item/general-midi).  
**Please Note:** The indexed values in the above link range from 1-128, whereas the corresponding instrument range is 0-127.

Planned updates
---------------
* Adding harmony elements
* Add a rhythm line of percussion instruments
* Improving instrument groups
* (Possibly) using other .midi files to build the rhythm/note chains