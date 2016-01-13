#!/usr/bin/env python2

from midiutil.MidiFile import MIDIFile

class Note(object):
    def __init__(self, pitch, time, duration, volume):
        self.pitch = pitch
        self.time = time
        self.duration = duration
        self.volume = volume
		
# Handles writeback of every channel (sop/alt/ten/bass) to file
def write_midi(filename, sequence):
    midi = MIDIFile(1)
    track = 0
    start_time = 0
    midi.addTrackName(track, start_time, 'genmus')
    tempo = random.randrange(120, 350)
    midi.addTempo(track, start_time, tempo)
    for seq in range(len(sequence)):
        for note in sequence[seq]:
            midi.addNote(track, seq, note.pitch, note.time, note.duration, note.volume)
        midi.addProgramChange(0, seq, 0, instrList[seq])
    f = open(filename, 'w')
    midi.writeFile(f)
    f.close()
##

import random
import math
import os
import time
import sys
from types import *
from bisect import bisect


MAJOR = [0,2,4,5,7,9,11]
MINOR = [0,2,3,5,7,8,10]
PHRYGIAN = [0,1,4,5,7,8,10]
UKRAINIAN_DORIAN = [0,2,3,6,7,9,10]
MOLOCH = [0,2,4,5,7,9,10]
PERSIAN = [0,1,4,5,6,8,11]

def gen_scale():
	k = random.choice([MAJOR, MINOR, PHRYGIAN, UKRAINIAN_DORIAN, MOLOCH, PERSIAN])
	print k
	return k
SCALE = gen_scale()

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
    
noteDict = {1:[(3, .8), (1, .19), (4, .01)], 2:[(2, .45), (1, .05), (4, .2), (6, .3)], 3:[(3, .45), (1, .45), (4, .1)], 4:[(4, .3), (2, .3), (6, .25), (8, .15)], 6:[(6, .3), (2, .5)], 8:[(8, .2), (4, .45), (2, .35)]}

class Rhythm(object):
    def __init__(self, period):
        self.period = period
        self.rhythm = []
        
    def gen(self):
        current = random.choice([1, 2, 3, 4, 6, 8]) # Starting notes, with 1 being 16th note
        i = 0
        while i < self.period:
            self.rhythm.append(current)
            i += current
            current = weighted_choice(noteDict[current])
        return self.rhythm

# Generates a motif based on rhythm and pitch
def gencell(rhythm):
    scale = SCALE
    seq = []
    t = 0
    startNote = random.randrange(50, 73)
    for i in rhythm: 
        currentNote = startNote + random.randrange(-2, 4)
        seq.append(Note(currentNote, t, i, 100)) # Todo notes, stacatto, legato + random.choice(scale)
        t += i
    return seq

def generate():
    rhythm = Rhythm(30).gen() ##TODO Rhythm length
    return gencell(rhythm)

instrGroups = [[0, 0, 0, 0], [40, 41, 42], [21, 22, 105, 109], [77, 79, 104, 15], [14, 10, 6], [65, 59, 1]] # TODO

def getInstruments():
    if len(sys.argv) == 1: # Generate random instruments
        return random.choice(instrGroups)
    elif len(sys.argv) > 17: # 16 insturments allowed + program name
        return random.choice(instrGroups)
    instr = []
    for i in range(1, len(sys.argv)): # Ignore program name
        assert int(sys.argv[i]) in range(0, 128), "Instrument must be in bounds (0, 127): %d" %sys.argv[i]
        instr.append(int(sys.argv[i]))
    return instr

name = time.strftime('song-%Y-%m-%d_%H%M%S.mid')
instrList = getInstruments() # Get a list of instruments used
print instrList
parts = [generate() for i in range(len(instrList))]

write_midi(name, parts)
print name
#os.system('./play.sh %s' % (name,))