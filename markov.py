#!/usr/bin/env python2

from midiutil.MidiFile import MIDIFile

import random
import math
import os
import time
import sys

from types import *
from bisect import bisect

import re
import sys

import mido

with open('/usr/share/dict/words') as f:
    WORDS = [re.sub(r'\W+', '', word) for line in f for word in line.split()]
# Handling writeback for each channel to file
def write_midi(filename, sequence):
    filename = "markov/"+filename
    midi = MIDIFile(1)
    track = 0
    start_time = 0
    midi.addTrackName(track, start_time, filename[:-4])
    tempo = random.randrange(360, 480)
    midi.addTempo(track, start_time, tempo)
    midi.addProgramChange(0, 0, 0, 1)
    
    for i in range(len(sequence)):
        note = sequence[i]
        midi.addNote(track, 0, note.pitch, note.time, note.duration, note.volume)
    f = open(filename, 'w')
    midi.writeFile(f)
    f.close()
    
class Mdict:
    def __init__(self):
        self.d = {}
    def __getitem__(self, key):
        if key in self.d:
            return self.d[key]
        else:
            raise KeyError(key)
    def add_key(self, prefix, suffix):
        if prefix in self.d:
            self.d[prefix].append(suffix)
        else:
            self.d[prefix] = [suffix]
    def get_suffix(self,prefix):
        l = self[prefix]
        return random.choice(l)  

class MName:
    """
    A name from a Markov chain
    """
    def __init__(self, chainlen = 2):
        """
        Building the dictionary
        """
        if chainlen > 10 or chainlen < 1:
            print "Chain length must be between 1 and 10, inclusive"
            sys.exit(0)
        self.mcd = Mdict() # Creates a dictionary
        oldnames = [] # Saves original list of names
        self.chainlen = chainlen
        for l in WORDS:
            l = l.strip()
            oldnames.append(l) # Build whitespace-stripped list of names
            s = " " * chainlen + l # s = "   "
            for n in range(0,len(l)): # Iterate through the string l
                self.mcd.add_key(s[n:n+chainlen], s[n+chainlen]) # For each element of string, add 
            self.mcd.add_key(s[len(l):len(l)+chainlen], "\n")
    
    def New(self):
        """
        New name from the Markov chain
        """
        prefix = " " * self.chainlen # Prefix = "  "
        name = "" 
        suffix = ""
        while True:
            suffix = self.mcd.get_suffix(prefix)
            if suffix == "\n" or len(name) > 9:
                break
            else:
                name = name + suffix
                prefix = prefix[1:] + suffix
        if not name in WORDS:
            return name
        else:
            return self.New()
        
class Note(object):
    def __init__(self, pitch, time, duration, volume):
        self.pitch = pitch
        self.time = time
        self.duration = duration
        self.volume = volume       
'''
Goal structure:
NOTES = 
{
noteA:[(noteA, number), (noteB, number), (noteC, number)],
noteB:[(noteB, number), (noteA, number), (noteC, number)],
---
or
---
noteA:{noteA:number, noteB:number, ...} and map(list, noteA.items())
}

Obtained by this:
if mode == "start":
    if message.name == "note_on":
        append note to start
    elif message.name == "note_off":
        mode = "follow"
        lead = message.note
elife mode == "follow"
    if message.name == "note_on":
        append message.note to NOTES{lead} or increment if exists
    elif message.name == "note_off":
        lead = message.note
'''
def weighted_choice(choices):
    values, weights = zip(*choices)
    total = 0
    cum_weights = []
    for w in weights:
        total += w
        cum_weights.append(total)
    x = random.random() * total
    i = bisect(cum_weights, x)
    return values[i]

if len(sys.argv) != 2:
    print "Input requires exactly one midi file as parameter."
    sys.exit()

file_name = sys.argv[1]

start_list = dict()
mode = "start"
NOTES = {}
lead = 0

for message in mido.MidiFile(file_name):
    if mode == "start":
        if message.type == 'note_on':
            start_list[message.note] = start_list.get(message.note, 0) + 1
        elif message.type == 'note_off':
            lead = message.note
            mode = "follow"
            if not message.note in NOTES:
                NOTES[message.note] = {}
    elif mode == "follow":
        if message.type == 'note_on':
            NOTES[lead][message.note] = start_list.get(message.note, 0) + 1
        elif message.type == 'note_off':
            lead = message.note
            if not message.note in NOTES:
                NOTES[message.note] = {}
    
#if message.type == 'note_on':
#   note_list[message.note] = note_list.get(message.note, 0) + 1

#print start_list, "\n"
#print NOTES, "\n"

num_notes = 200
final_sequence = []
'''
After done, pull random element from start_list as the starting item
and use it for developing the rest of the song
'''
pitch = weighted_choice(map(list, start_list.items()))
i=0
t=1
while i < num_notes:
    t = weighted_choice([(1, .5), (2, .4), (4, .1)])
    note = Note(pitch, i, t, 100)
    final_sequence.append(note)
    new_map = map(list, NOTES[pitch].items())
    if len(new_map) == 0:
        new_map = map(list, start_list.items())
    pitch = weighted_choice(new_map)
    i+=t

file_name = time.strftime(MName().New() + '.mid')
write_midi(file_name, final_sequence)
print "File successfully creating:", file_name