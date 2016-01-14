#!/usr/bin/env python2

from midiutil.MidiFile import MIDIFile

import random
import math
import os
import time
import sys
from types import *
from bisect import bisect


# Handles writeback of every channel  to file
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

'''
The arrangement contains everything about the song.
It's divided up into an instrument that receives the melody, and remaining instruments that compose the harmony.
The melody receives a part for the Intro, Chorus, each verse, and the Outro.
Harmonies *might* get an intro part, have a part for the chorus and verses, and hold for outro
'''
class Arrangement(object):
    def __init__(self, key):
        self.key = key
        self.scale = SCALE
        self.length_intro = random.randrange(10, 20)
        self.Intro = None # List of notes used as the 'pickup'
        self.length_chorus = random.randrange(30, 50)
        self.Chorus = None # List of notes used as the main motif
        self.length_verse = random.randrange(30, 50)
        self.Verses = [] # List of verses, which are each list of notes of the verse
        self.numVerses = random.randrange(2, 5)
        self.length_outro = random.randrange(10, 20)
        self.Outro = None # List of notes used as the end of the song
    def gen(self):
        self.Chorus = Chorus(self.length_chorus, self.key)
        self.Chorus.gen()
        self.Intro = Intro(self.length_intro, self.key)
        self.Intro.gen()
        for i in range(self.numVerses):
            self.Verses.append(Verse(self.length_verse, self.key))
            self.Verses[i].gen()
        self.Outro = Outro(self.length_outro, self.key)
        self.Outro.gen()
        print "Length of Intro:", (self.length_intro)
        print "Length of Chorus:", (self.length_chorus) 
        print"Length of Verses:", (self.length_verse)
        print "Number of verses:", (self.numVerses)
        
    def build_arrangement(self):
        # Song structure is Intro/Chorus/(Verse/Chorus pairs)/Outro
        self.melody = []
        self.melody += (self.Intro.melody) 
        self.melody += (self.Chorus.melody)
        for i in range(self.numVerses):
            self.melody += (self.Verses[i].melody)
            self.melody += (self.Chorus.melody)
        self.melody += (self.Outro.melody)
        return [self.melody] ## TODO HARMONY

class Chorus(object):
    def __init__(self, length, key):
        self.length = length
        self.melody = []
        self.harmonies = []
        self.key = key
    def gen(self):
        mel = Melody(self.length, self.key)
        mel.gen()
        self.melody = mel.sequence
        ## TODO Harmony

class Intro(object):
    def __init__(self, length, key):
        self.length = length
        self.melody = []
        self.harmonies = []
        self.key = key
    def gen(self):
        mel = Melody(self.length, self.key)
        mel.gen()
        self.melody = mel.sequence[::-1]
        ## TODO Harmony
        
class Outro(object):
    def __init__(self, length, key):
        self.length = length
        self.melody = []
        self.harmonies = []
        self.key = key
    def gen(self):
        mel = Melody(self.length, self.key)
        mel.gen()
        self.melody = mel.sequence
        ## TODO Harmony

class Verse(object):
    def __init__(self, length, key):
        self.length = length
        self.melody = []
        self.harmonies = []
        self.key = key
    def gen(self):
        mel = Melody(self.length, self.key)
        mel.gen()
        self.melody = mel.sequence
        ## TODO Harmony

'''
    Low-level objects:
    Notes, Rhythm, Scale generation
'''
class Note(object):
    def __init__(self, pitch, time, duration, volume):
        self.pitch = pitch
        self.time = time
        self.duration = duration
        self.volume = volume
        
# Probabilities that a given note is followed by another note length
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

# Lists of instruments that pair well together, maybe.
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
	

MAJOR = [0,2,4,5,7,9,11]
MINOR = [0,2,3,5,7,8,10]
PHRYGIAN = [0,1,4,5,7,8,10]
UKRAINIAN_DORIAN = [0,2,3,6,7,9,10]
MOLOCH = [0,2,4,5,7,9,10]
PERSIAN = [0,1,4,5,6,8,11]

def gen_scale():
	k = random.choice([MAJOR, MINOR, PHRYGIAN, UKRAINIAN_DORIAN, MOLOCH, PERSIAN])
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
    
DIRECTION = random.randrange(0, 100) # < DIRECTION Implies direction change
JUMPINESS = random.randrange(0, 100) # < JUMPINESS Implies jump
MOBILITY = random.randrange(60, 90) # < MOBILITY Implies moving notes

class Melody(object):
    def __init__(self, length, key):
        self.key = 72+key
        self.rhythm = []
        self.sequence = []
        self.scale = SCALE
        self.length = length
    def gen(self):
        self.rhythm = Rhythm(self.length).gen() ## TODO Rhythm length
        currentNote = self.key
        t = 0
        currentDirection = 1
        index = 0
        for i in self.rhythm:
            self.sequence.append(Note(currentNote, t, i, 100))
            if (random.randrange(0, 100) < MOBILITY):
                currentNote = self.key + (self.scale[index%len(self.scale)]+(index/len(self.scale))*12 if index > 0 else self.scale[-(-index%len(self.scale))]+12*(index/len(self.scale)))
            if (random.randrange(0, 100) < DIRECTION):
                currentDirection = -currentDirection
            if (random.randrange(0, 100) < JUMPINESS):
                index += currentDirection * random.choice([2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 4, 5])
            if (currentNote < 50 or currentNote > 100):
                currentNote = self.key
            t += i

# I don't know at the moment how this should work, aside from picking 'nice' chords relating to melody'
class Harmony(object):
    def __init__(self, melody):
        self.melody = melody
        self.key = melody.key#+random.randchoice(-24, -12, 0, 12) # Get a random octave shift
        self.shift = random.choice([-24, -12, 0])
        self.rhythm = [] # Currently copying the rhythm
        self.sequence = []
    def gen_rhythm(self):
        for i in range(songLength, 8): ## TODO
            self.rhythm.append(8) # For now, half notes 
            
    def gen(self):
        gen_rhythm()
        startNote = self.key
        t = 0
        for i in self.rhythm:
            self.sequence.append(Note(i.pitch+self.shift+random.choice([-8, -4, 0, 4, 8]), i.time, i.duration, 75)) ## TODO


name = time.strftime('song-%Y-%m-%d_%H%M%S.mid')
print name
instrList = getInstruments() # Get a list of instruments used, either randomly or from user input
numHarmonies = len(instrList)-1
print "Number of harmonies:", (numHarmonies)
# Initialize the entire song, part-by-part
arrangement = Arrangement(random.randrange(0, 12))
arrangement.gen()
write_midi(name, arrangement.build_arrangement())
#os.system('./play.sh %s' % (name,))