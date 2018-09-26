from midiutil import MIDIFile
import sys, getopt, time, os, math, random, hashlib, json
from types import *
from bisect import bisect
import numpy
import copy, yaml, argparse, collections
import __main__

debug_log = False
verbose_log = False

def log(event):
    if verbose_log is True:
        print(event)

def debug(event):
    if debug_log is True:
        print(event)

class Util:
    scales = {
      'chromatic': [0,1,2,3,4,5,6,7,8,9,10,11],
      'major': [0,2,4,5,7,9,11],
      'harmonicMinor': [0,2,3,5,7,8,11],
      'minorPentatonic': [0,3,5,7,10],
      'naturalMinor': [0,2,3,5,7,8,10],
      'melodicMinorUp': [0,2,3,5,7,9,11],
      'melodicMinorDown': [0,2,4,5,7,9,10],
      'dorian': [0,2,3,5,7,9,10],
      'mixolydian': [0,2,4,5,7,9,10],
      'ahavaRaba': [0,1,4,5,7,8,10],
      'majorPentatonic': [0,2,4,7,9],
      'diatonic': [0,2,4,6,8,10],
      'phrygian': [0,1,3,5,7,8,10]
    }

    chords = {
      'major': [0,4,7],
      'minor': [0,3,7],
      'relMinor1stInv': [0,4,9],
      'subdominant2ndInv': [0,5,9],
      'major7th': [0,4,7,11],
      'minor7th': [0,3,7,10],
      'major9th': [0,4,7,14],
      'minor9th': [0,3,7,13],
      'major6th': [0,4,9],
      'minor6th': [0,3,8],
      'major7th9th': [0,4,7,11,14],
      'minor7th9th': [0,3,7,10,13],
      'major7th11th': [0,4,7,11,18],
      'minor7th11th': [0,3,7,10,17],
    }

    chord_systems = {
        'major': ['major', 'major7th', 'major9th', 'major6th', 'major7th9th', 'major7th11th', 'subdominant2ndInv'],
        'harmonicMinor': ['minor', 'relMinor1stInv', 'minor7th', 'minor9th', 'minor6th', 'minor7th9th', 'minor7th11th'],
        'minorPentatonic': ['minor', 'relMinor1stInv', 'minor7th', 'minor9th', 'minor6th', 'minor7th9th', 'minor7th11th'],
        'naturalMinor': ['minor', 'relMinor1stInv', 'minor7th', 'minor9th', 'minor6th', 'minor7th9th', 'minor7th11th'],
        'melodicMinorUp': ['minor', 'relMinor1stInv', 'minor7th', 'minor9th', 'minor6th', 'minor7th9th', 'minor7th11th'],
        'melodicMinorDown': ['minor', 'relMinor1stInv', 'minor7th', 'minor9th', 'minor6th', 'minor7th9th', 'minor7th11th'],
        'dorian': ['minor', 'relMinor1stInv', 'minor7th', 'minor9th', 'minor6th', 'minor7th9th', 'minor7th11th'],
        'mixolydian': ['minor', 'relMinor1stInv', 'minor7th', 'minor9th', 'minor6th', 'minor7th9th', 'minor7th11th'],
        'ahavaRaba': ['minor', 'relMinor1stInv', 'minor7th', 'minor9th', 'minor6th', 'minor7th9th', 'minor7th11th'],
        'majorPentatonic': ['minor', 'relMinor1stInv', 'minor7th', 'minor9th', 'minor6th', 'minor7th9th', 'minor7th11th'],
        'diatonic': ['minor', 'relMinor1stInv', 'minor7th', 'minor9th', 'minor6th', 'minor7th9th', 'minor7th11th'],
        'phrygian': ['minor', 'relMinor1stInv', 'minor7th', 'minor9th', 'minor6th', 'minor7th9th', 'minor7th11th'],
    }

    instrument_sets = [
        #{'melody':72,'harmony':56,'bass':61,'rhythm':112}, # Clarinet/Trumpet/Brass Section/Tinkle Bell
        {'melody':2,'harmony':2,'bass':49,'rhythm':118}, # Electric Piano/Electric Piano/String Ensemble 2/Synth Drum
        {'melody':0,'harmony':0,'bass':0,'rhythm':118}, # Grand Piano/Grand Piano/Grand Piano/Synth Drum
        #{'melody':71,'harmony':48,'bass':60,'rhythm':118}, # Clarinet/String Ensemble 1/French Horn/Synth Drum
        #{'melody':67,'harmony':75,'bass':105,'rhythm':53}, # Baritone Sax/Pan Flute/Banjo/Voice Oohs
        #{'melody':80,'harmony':81,'bass':87,'rhythm':84} # Lead 1 (square)/Lead 1 (Square)/Lead 8 (Bass + Lead)/Lead 5 (Charang)
        #{'melody':80,'harmony':80,'bass':81,'rhythm':85}, # Square/Square/Sawtooth/Voice
        #{'melody':105,'harmony':22,'bass':32,'rhythm':117}, # Banjo/Harmonica/Acoustic Bass/Melodic Tom
        #{'melody':12,'harmony':76,'bass':68,'rhythm':115}, # Marimba/Blown Bottle/Kalimba/Woodblock
        #{'melody':13,'harmony':14,'bass':15,'rhythm':10},
        #{'melody':3,'harmony':3,'bass':3,'rhythm':113}
    ]

    notes = {
      0: { 'name':'C0', 'frequency':16.35, },
      1: { 'name':'C#0/Db0', 'frequency':17.32, },
      2: { 'name': 'D0', 'frequency': 18.35 },
      3: { 'name': 'D#0/Eb0', 'frequency': 19.45 },
      4: { 'name': 'E0', 'frequency': 20.60 },
      5: { 'name': 'F0', 'frequency': 21.83 },
      6: { 'name': 'F#0/Gb0', 'frequency': 23.12 },
      7: { 'name': 'G0', 'frequency': 24.50 },
      8: { 'name': 'G#0/Ab0', 'frequency': 25.96 },
      9: { 'name': 'A0', 'frequency': 27.50 },
      10: { 'name': 'A#0/Bb0', 'frequency': 29.14 },
      11: { 'name': 'B0', 'frequency': 30.87 },
      12: { 'name': 'C1', 'frequency': 32.70 },
      13: { 'name': 'C#1/Db1', 'frequency': 34.65 },
      14: { 'name': 'D1', 'frequency': 36.71 },
      15: { 'name': 'D#1/Eb1', 'frequency': 38.89 },
      16: { 'name': 'E1', 'frequency': 41.20 },
      17: { 'name': 'F1', 'frequency': 43.65 },
      18: { 'name': 'F#1/Gb1', 'frequency': 46.25 },
      19: { 'name': 'G1', 'frequency': 49.00 },
      20: { 'name': 'G#1/Ab1', 'frequency': 51.91 },
      21: { 'name': 'A1', 'frequency': 55.00 },
      22: { 'name': 'A#1/Bb1', 'frequency': 58.27 },
      23: { 'name': 'B1', 'frequency': 61.74 },
      24: { 'name': 'C2', 'frequency': 65.41 },
      25: { 'name': 'C#2/Db2', 'frequency': 69.30 },
      26: { 'name': 'D2', 'frequency': 73.42 },
      27: { 'name': 'D#2/Eb2', 'frequency': 77.78 },
      28: { 'name': 'E2', 'frequency': 82.41 },
      29: { 'name': 'F2', 'frequency': 87.31 },
      30: { 'name': 'F#2/Gb2', 'frequency': 92.50 },
      31: { 'name': 'G2', 'frequency': 98.00 },
      32: { 'name': 'G#2/Ab2', 'frequency': 103.83 },
      33: { 'name': 'A2', 'frequency': 110.00 },
      34: { 'name': 'A#2/Bb2', 'frequency': 116.54 },
      35: { 'name': 'B2', 'frequency': 123.47 },
      36: { 'name': 'C3', 'frequency': 130.81 },
      37: { 'name': 'C#3/Db3', 'frequency': 138.59 },
      38: { 'name': 'D3', 'frequency': 146.83 },
      39: { 'name': 'D#3/Eb3', 'frequency': 155.56 },
      40: { 'name': 'E3', 'frequency': 164.81 },
      41: { 'name': 'F3', 'frequency': 174.61 },
      42: { 'name': 'F#3/Gb3', 'frequency': 185.00 },
      43: { 'name': 'G3', 'frequency': 196.00 },
      44: { 'name': 'G#3/Ab3', 'frequency': 207.65 },
      45: { 'name': 'A3', 'frequency': 220.00 },
      46: { 'name': 'A#3/Bb3', 'frequency': 233.08 },
      47: { 'name': 'B3', 'frequency': 246.94 },
      48: { 'name': 'C4', 'frequency': 261.63 },
      49: { 'name': 'C#4/Db4', 'frequency': 277.18 },
      50: { 'name': 'D4', 'frequency': 293.66 },
      51: { 'name': 'D#4/Eb4', 'frequency': 311.13 },
      52: { 'name': 'E4', 'frequency': 329.63 },
      53: { 'name': 'F4', 'frequency': 349.23 },
      54: { 'name': 'F#4/Gb4', 'frequency': 369.99 },
      55: { 'name': 'G4', 'frequency': 392.00 },
      56: { 'name': 'G#4/Ab4', 'frequency': 415.30 },
      57: { 'name': 'A4', 'frequency': 440.00 },
      58: { 'name': 'A#4/Bb4', 'frequency': 466.16 },
      59: { 'name': 'B4', 'frequency': 493.88 },
      60: { 'name': 'C5', 'frequency': 523.25 },
      61: { 'name': 'C#5/Db5', 'frequency': 554.37 },
      62: { 'name': 'D#5/Eb5', 'frequency': 622.25 },
      63: { 'name': 'E5', 'frequency': 659.26 },
      64: { 'name': 'F5', 'frequency': 698.46 },
      65: { 'name': 'F#5/Gb5', 'frequency': 739.99 },
      66: { 'name': 'G5', 'frequency': 783.99 },
      67: { 'name': 'G#5/Ab5', 'frequency': 830.61 },
      68: { 'name': 'A5', 'frequency': 880.00 },
      69: { 'name': 'A#5/Bb5', 'frequency': 932.33 },
      70: { 'name': 'B5', 'frequency': 987.77 },
      71: { 'name': 'C6', 'frequency': 1046.50 },
      72: { 'name': 'C#6/Db6', 'frequency': 1108.73 },
      73: { 'name': 'D#6/Eb6', 'frequency': 1244.51 },
      74: { 'name': 'E6', 'frequency': 1318.51 },
      75: { 'name': 'F6', 'frequency': 1396.91 },
      76: { 'name': 'F#6/Gb6', 'frequency': 1479.98 },
      77: { 'name': 'G6', 'frequency': 1567.98 },
      78: { 'name': 'G#6/Ab6', 'frequency': 1661.22 },
      79: { 'name': 'A6', 'frequency': 1760.00 },
      80: { 'name': 'A#6/Bb6', 'frequency': 1864.66 },
      81: { 'name': 'B6', 'frequency': 1975.53 },
      82: { 'name': 'C7', 'frequency': 2093.00 },
      83: { 'name': 'C#7/Db7', 'frequency': 2217.46 },
      84: { 'name': 'D7', 'frequency': 2349.32 },
      85: { 'name': 'D#7/Eb7', 'frequency': 2489.02 },
      86: { 'name': 'E7', 'frequency': 2637.02 },
      87: { 'name': 'F7', 'frequency': 2793.83 },
      88: { 'name': 'F#7/Gb7', 'frequency': 2959.96 },
      89: { 'name': 'G7', 'frequency': 3135.96 },
      90: { 'name': 'G#7/Ab7', 'frequency': 3322.44 },
      91: { 'name': 'A7', 'frequency': 3520.00 },
      92: { 'name': 'A#7/Bb7', 'frequency': 3729.31 },
      93: { 'name': 'B7', 'frequency': 3951.07 },
      94: { 'name': 'C8', 'frequency': 4186.01 }
    }

    def __init__(self):
        pass

    def random_choice(self, choices):
        return random.choice(choices)

    def weighted_choice(self, choices):
        values, weights = zip(*choices)
        total = 0
        cum_weights = []
        for w in weights:
            total += w
            cum_weights.append(total)
        x = random.random() * total
        i = bisect(cum_weights, x)
        return values[i]

class Generator:
    events = []
    song = []
    rest_threshold = 15
    metadata = {}

    def __init__(self, args={}):
        melody_type = "random"
        harmony_type = "random"
        bass_type = "random"
        rhythm_type = "random"
        log("Starting generation...")
        self.config(args=args)
        log(" Building melody...")
        self.melody(args=args)
        log(" Melody complete.")
        log(" Generating bass line...")
        self.bass(args=args)
        log(" Bass line complete.")
        log(" Generating harmony...")
        self.harmony(args=args)
        log(" Harmony complete.")
        log(" Generating rhythm...")
        self.rhythm(args=args)
        log(" Rhythm complete.")
        log(" Performing post-processing...")
        self.postprocess()
        log(" Post-processing complete.")
        self.finalize()
        log("Song generation complete.")

    def config(self, args={}):
        # Key signature, Time signature, Scale
        if "tempo" in args:
            self.tempo = args["tempo"]
        else:
            self.tempo = int(numpy.random.normal(120, 32))
        if "scale" in args and args["scale"] in list(Util().scales.keys()):
            scale_key = args["scale"]
        else:
            scale_key = Util().random_choice(list(Util().scales.keys()))
        self.base_note = random.randint(48, 84)
        if "base_note" in args:
            for note in Util().notes:
                if Util().notes[note]["name"] == args["base_note"]:
                    self.base_note = note
                    break
        self.scale = Util().scales[scale_key]
        self.time_signature = {"count":Util().random_choice([3,4,5,6,8]),"unit":Util().random_choice([4,4,4,4,8,8])}
        log("    Scale: " + scale_key)
        log("    Time signature: " + str(self.time_signature["count"]) + "/" + str(self.time_signature["unit"]))
        log("    Base note: " + Util().notes[self.base_note]["name"])
        log("    Tempo: " + str(self.tempo) + " bpm")

    def _d_weighted(self, previous, args):
        if "probability" in args:
            probability = args["probability"]
        else:
            probability = [(0.5, .35), (1, .35), (2, .2), (3, .05), (4, .05)]
        return Util().weighted_choice(probability)

    def _d_uniform(self, previous, args):
        return Util().random_choice([0.5, 1, 2, 3, 4])

    # Mostly markov except for a chance to start a new duration sequence
    def _d_semimarkov(self, previous, args):
        if "probability" in args:
            probability = args["probability"]
        else:
            probability = {
                0.5:[(0.5, 0.5), (1, 0.25), (1.5, .15), (2, 0.1), (3, 0), (4, 0)],
                1:[(0.5, 0.25), (1, 0.35), (1.5, .1), (2, 0.2), (3, 0.06), (4, 0.04)],
                1.5:[(0.5, .5), (1, .1), (1.5, .3), (2, .1), (3, 0), (4, 0)],
                2:[(0.5, 0.1), (1, 0.2), (1.5, .1), (2, 0.4), (3, 0.1), (4, 0.1)],
                3:[(0.5, 0.01), (1, 0.2), (1.5, 0.05), (2, 0.14), (3, 0.4), (4, 0.1)],
                4:[(0.5, 0.01), (1, 0.09), (1.5, 0), (2, 0.5), (3, 0.2), (4, 0.2)]
            }
        new_notes = [0.5, 1, 1.5, 2, 3, 4]
        new_threshold = 2
        if (random.randint(0,100) < new_threshold):
            return Util().random_choice(new_notes)
        else:
            return Util().weighted_choice(probability[previous])

    def _d_markov(self, previous, args):
        if "probability" in args:
            probability = args["probability"]
        else:
            probability = {
                0.5:[(0.5, 0.5), (1, 0.25), (1.5, .15), (2, 0.1), (3, 0), (4, 0)],
                1:[(0.5, 0.25), (1, 0.35), (1.5, .1), (2, 0.2), (3, 0.06), (4, 0.04)],
                1.5:[(0.5, .5), (1, .1), (1.5, .3), (2, .1), (3, 0), (4, 0)],
                2:[(0.5, 0.1), (1, 0.2), (1.5, .1), (2, 0.4), (3, 0.1), (4, 0.1)],
                3:[(0.5, 0.01), (1, 0.2), (1.5, 0.05), (2, 0.14), (3, 0.4), (4, 0.1)],
                4:[(0.5, 0.01), (1, 0.09), (1.5, 0), (2, 0.5), (3, 0.2), (4, 0.2)]
            }
        return Util().weighted_choice(probability[previous])

    def _duration(self, type="random", note=1, args={}):
        if type=="weighted":
            return self._d_weighted(note, args)
        elif type=="uniform":
            return self._d_uniform(note, args)
        elif type=="markov":
            return self._d_markov(note, args)
        elif type=="semimarkov":
            return self._d_semimarkov(note, args)
        generation_type = Util().random_choice([getattr(self, '_d_weighted'), getattr(self, '_d_uniform'), getattr(self, '_d_markov'), getattr(self, '_d_semimarkov')])

        return generation_type(note, args)

    # Currently returns the step interval for the new note.
    def _nm_normal_skew(self, note, args):
        if "cutoffs" in args:
            cutoffs = args["cutoffs"]
        else:
            cutoffs={0.5: 0, 1: 1, 1.5: 2, 2: 3, 2.5: 4, 3: 5}
        skew = (self.base_note - note) / 12.0
        p = numpy.random.normal(0, 1) + skew
        max_jump = 0
        for i in list(cutoffs.keys()):
            if abs(cutoffs[i]) > max_jump:
                max_jump = cutoffs[i]
            if abs(p) < i:
                return cutoffs[i] * numpy.sign(p)
        return (max_jump + 1) * numpy.sign(p)

    # Will return [-1, 0, 1]
    def _nm_step(self, note, args):
        return random.randint(-1, 1)

    # Uniform distribution of [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
    def _nm_uniform(self, note, args):
        return random.randint(-5, 5)

    def _note_mutation(self, note, type="random", args={}):
        # The handler for different generation
        if type=="normal_skew":
            return self._nm_normal_skew(note, args)
        elif type=="step":
            return self._nm_step(note, args)
        elif type=="uniform":
            return self._nm_uniform(note, args)
        generation_type = Util().random_choice([getattr(self, '_nm_normal_skew'), getattr(self, '_nm_step'), getattr(self, '_nm_uniform')])
        return generation_type(note, args)

    def _v_midpoint_displacement(self, args={}):
        log("  Verse: Midpoint Displacement")
        verse = []
        note_value = self.base_note
        iterations = random.randint(2, 5)
        verse_length = 2**iterations+1 # Distinct notes
        if "roughness" in args:
            displace = args["roughness"]
        else:
            displace = 1
        if "melody_duration" in args:
            duration_type = args["melody_duration"]
        else:
            duration_type = "random"
        # Build the note series
        for i in range(verse_length):
            verse.append({"pitch":note_value, "time":0, "duration":0, "volume":100, "index":0})
        # Use midpoint displacement algorithm to build series
        midpoint = int(verse_length / 2)
        i = 1
        while i < verse_length:
            j = int(verse_length/i/2)
            while j < verse_length:
                if j == midpoint:
                    verse[j]["index"] = Util().random_choice([-12, -11, -10, -9, -8, -7, -6, 6, 7, 8, 9, 10, 11, 12])
                else:
                    verse[j]["index"] = int((verse[j - int((verse_length / i) / 2)]["index"] + verse[j + int((verse_length / i) / 2)]["index"]) / 2)
                    verse[j]["index"] += random.uniform(-1.0*displace, 1.0*displace)
                j += int(verse_length / i)
            i *= 2
        elapsed_time = 0
        for i in range(len(verse)):
            verse[i]["index"] = int(verse[i]["index"])
            verse[i]["pitch"] = min(max(12 * int(verse[i]["index"] / len(self.scale)) + self.scale[verse[i]["index"] % len(self.scale)] + self.base_note, 1), 126)
            # todo variate lengths, total duration and adjust to offset
            duration = self._duration(note=(verse[i-1]["duration"] if i>0 else 1), type=duration_type)
            verse[i]["duration"] = duration
            elapsed_time += duration
            verse[i]["time"] = elapsed_time
        return verse

    # Builds the verse one note at a time, and then reiterates to find any places where
    def _v_piecewise_notes(self, args={}):
        log("  Verse: Piecewise Notes")
        verse = []
        joined_notes = []
        note_value = self.base_note
        note_index = 0
        verse_length = random.randint(3, 10)
        index = 0

        if "join_threshold" in args:
            base_join_threshold = args["join_threshold"]
        else:
            base_join_threshold = 75
        if "base_duration" in args:
            base_duration = args["base_duration"]
        else:
            base_duration = 0.5

        # Base generation here
        for i in range(int(verse_length * self.time_signature["count"] * (4 / base_duration) / self.time_signature["unit"])): # Want to generate a note for each eigth note (for now)
            time = i*base_duration
            if random.randint(0,100) < self.rest_threshold:
                continue

            note_value = min(max(12 * int(note_index / len(self.scale)) + self.scale[note_index % len(self.scale)] + self.base_note, 1), 126)
            note = {
                "pitch":note_value, "time":time, "duration":base_duration, "volume":100, "index":note_index
            }
            verse.append(note)
            note_index += int(self._note_mutation(note_value, type="random", args={"cutoffs":{1: 0, 1.5: 1, 1.9: 2, 2.3: 3, 2.7: 4, 3: 5}}))
        # Link together similar notes
        for i in range(len(verse)-1):
            join_threshold = base_join_threshold + (0 if int(verse[i]["time"]) == verse[i]["time"] else 15)
            if verse[i]["pitch"] == verse[i+1]["pitch"] and random.randint(0, 100) < join_threshold:
                verse[i]["duration"] += base_duration
                joined_notes.append(i)
        for i in reversed(joined_notes):
            verse.pop(i)
        return verse

    # I'm actually having a hard time understanding how this is different than the other systems I've built.
    def _v_by_measure(self, args={}):
        log("  Verse: By Measure")
        if "duration_type" in args:
            duration_type = args["duration_type"]
        else:
            duration_type = 0.5
        # Generate a main theme for the melody to repeat >1 time in song
        verse = []
        note_value = self.base_note
        measure_length = random.randint(3,10)
        # Develop each measure note-by-note
        note_count = 0
        total_note_count = 0
        index = 0 # base note
        for measure in range(measure_length):
            note_count = note_count % self.time_signature["count"]
            while note_count < self.time_signature["count"]:
                duration = self._duration(note=(verse[len(verse)-1]["duration"] if len(verse)>0 else 1), type=duration_type)
                volume = 100
                note_count += duration
                total_note_count += duration
                # Apply a rest if random int is less than the threshold
                if random.randint(0,100) < self.rest_threshold:
                    continue
                index += int(self._note_mutation(note_value))
                note_value = min(max(12 * int(index / len(self.scale)) + self.scale[index % len(self.scale)] + self.base_note, 1), 126)
                note = { # Time is established here, but the real value is used later.
                    "pitch":note_value, "time":total_note_count, "duration": duration, "volume":100, "index": index
                }
                verse.append(note)
        return verse

    def _verse(self, type="random", args={}):
        if type=="midpoint_displacement":
            return self._v_midpoint_displacement(args)
        elif type=="piecewise":
            return self._v_piecewise_notes(args)
        elif type=="measure":
            return self._v_by_measure(args)
        generation_type = [getattr(self, '_v_midpoint_displacement'), getattr(self, '_v_piecewise_notes'), getattr(self, '_v_by_measure')]
        return Util().random_choice(generation_type)(args=args)

    def melody(self, args={}):
        if "melody_type" in args:
            type=args["melody_type"]
        else:
            type="random"
        if "melody_structure" in args:
            structure = args["melody_structure"]
        else:
            structure = Util().random_choice(["abcbdbebf", "abcba", "ababc", "abcbdbe", "abcde", "abba", "abbc"])
        self.metadata["melody_structure"] = structure
        self.metadata["melody"] = []
        log("  Chosen structure: " + structure)
        structure_components = list(set(structure))
        melody_components = {}
        melody = []
        for x in structure_components:
            melody_components[x] = {'verse': self._verse(type=type, args=args)}
            melody_components[x]['duration'] = melody_components[x]["verse"][-1]["time"] + melody_components[x]["verse"][-1]["duration"]
        offset = 0
        for x in structure:
            # Take melody_components[x]'s list and
            current_theme = copy.deepcopy(melody_components[x]["verse"])
            self.metadata["melody"].append({'component': x, 'start': offset})
            for note in range(len(current_theme)):
                current_theme[note]["time"] += offset
                melody.append(current_theme[note])
            offset += melody_components[x]["duration"]
        self.melody = melody

    def _h_multibridge(self, args={}):
        log("  Harmony: Multi Bridge")
        harmony = []
        time = 0
        max_time = self.melody[-1]["time"] + self.melody[-1]["duration"]
        melody_index = 0
        harmony_index = 0
        valid_intervals = []
        chord_choice = Util().random_choice(list(Util().chord_systems.keys()))
        debug("Chord Choice: " + chord_choice)
        candidate_removal_threshold = 80
        for chord in Util().chord_systems[chord_choice]:
            valid_intervals = set(list(valid_intervals) + Util().chords[chord])
        while time < max_time:
            candidate_notes = []
            note_duration = Util().random_choice([2,3,4,5,6,7,8])
            harmony_index += 1
            start_note = self.melody[melody_index]["pitch"]
            while melody_index < len(self.melody)-1:
                if time+note_duration < self.melody[melody_index]["time"]+self.melody[melody_index]["duration"]:
                    break
                melody_index += 1
            end_note = self.melody[melody_index]["pitch"]
            available_start = [start_note + i for i in valid_intervals]
            available_end = [end_note + i for i in valid_intervals]
            for i in available_start:
                if i in available_end:
                    candidate_notes.append(i)
            if len(candidate_notes) > 0:
                harmony.append({"pitch":candidate_notes[0],"time":time,"duration":note_duration,"volume":90})
            secondary_candidate_notes = []
            index = 1
            while index < len(candidate_notes):
                if candidate_notes[index] - candidate_notes[0] > 4: # For right now, using this as a basis of "good" notes
                    secondary_candidate_notes.append(candidate_notes[index])
                index+=1
            num_additions = random.randint(0, len(secondary_candidate_notes))
            elapsed_duration = time
            for i in range(num_additions):
                secondary_duration = max(min(Util().random_choice(range(2, note_duration+1)), note_duration - elapsed_duration), 0)
                secondary_pitch = Util().random_choice(secondary_candidate_notes)
                if secondary_duration <= 0:
                    break
                harmony.append({"pitch":secondary_pitch, "time": elapsed_duration, "duration": secondary_duration, "volume": 75})
                elapsed_duration += secondary_duration
                if random.randint(0, 100) < candidate_removal_threshold:
                    secondary_candidate_notes.remove(secondary_pitch)
            time += note_duration
            debug(harmony)
        return harmony

    # Pick a random time interval, recording the note at the beginning and end (Fine-tune to start and stop when melody does?)
    # Based on selected chord system, compile list of notes that appear in both notes' chord lists
    # If a pool of notes is available, pick at least one available note (More if each note in pool is a reasonable step away)
    def _h_bridge(self, args={}):
        log("  Harmony: Bridge")
        harmony = []
        time = 0
        max_time = self.melody[-1]["time"] + self.melody[-1]["duration"]
        melody_index = 0
        harmony_index = 0
        valid_intervals = []
        chord_choice = Util().random_choice(list(Util().chord_systems.keys()))
        for chord in Util().chord_systems[chord_choice]:
            valid_intervals = set(list(valid_intervals) + Util().chords[chord])
        while time < max_time:
            candidate_notes = []
            note_duration = Util().random_choice([2,3,4,5,6,7,8])
            harmony_index += 1
            start_note = self.melody[melody_index]["pitch"]
            while melody_index < len(self.melody)-1:
                if time+note_duration < self.melody[melody_index]["time"]+self.melody[melody_index]["duration"]:
                    break
                melody_index += 1
            end_note = self.melody[melody_index]["pitch"]
            available_start = [start_note + i for i in valid_intervals]
            available_end = [end_note + i for i in valid_intervals]
            for i in available_start:
                if i in available_end:
                    candidate_notes.append(i)
            if len(candidate_notes) > 0:
                harmony.append({"pitch":Util().random_choice(candidate_notes),"time":time,"duration":note_duration,"volume":90})
            time += note_duration
        return harmony

    # Discrete Chord harmony will pick notes with frequency of 1-rest_threshold*2 (Pending) and append all notes in harmony.
    # The original version, which keyed off of assuming the interval was based on the scale index instead of number of half-steps, added some amount of pleasant dissonance that the new version is missing.
    def _h_discrete_chord(self, args={}):
        log("  Harmony: Discrete Chords")
        harmony = []
        index = 0
        melody_index = 0
        melody_duration = 0
        basis = self.melody
        chord_selection = Util().random_choice(list(Util().chord_systems.keys()))
        chord_options = Util().chord_systems[chord_selection]
        for note in basis:
            if random.randint(0,100) < self.rest_threshold*2:
                continue;
            chord = Util().chords[Util().random_choice(chord_options)]
            for idx in chord:
                harmony_note = {"pitch":note["pitch"] + idx, "time": note["time"], "duration":note["duration"] , "volume": int(100 - idx*2)}
                harmony.append(harmony_note)
        return harmony

    def harmony(self, args={}):
        type="random"
        if "harmony_type" in args:
            type = args["harmony_type"]
        if type=="discrete_chord":
            harmony = self._h_discrete_chord(args)
        elif type=="bridge":
            harmony = self._h_bridge(args)
        elif type=="multibridge":
            harmony = self._h_multibridge(args)
        else:
            generation_type = [getattr(self, '_h_discrete_chord'), getattr(self, '_h_bridge'), getattr(self, '_h_multibridge')]
            harmony = Util().random_choice(generation_type)(args=args)
        self.harmony = harmony

    def _b_pulse(self, args={}):
        log("  Bass: Pulse")
        bass = []
        index = 0
        melody_index = 0
        aggression = Util().weighted_choice([(4.0, 0.05), (2.0, .35), (1.0, .59), (0.5, .01)])
        pitch_drop = Util().random_choice([12, 24])
        if self.base_note < 55:
            pitch_drop += 12
        while index < self.melody[-1]["time"]:
            note = {
                "pitch":max(self.melody[melody_index]["pitch"]-pitch_drop, 1), "time":index, "duration":self.time_signature["count"], "volume":75, "index":self.melody[melody_index]["index"]
            }
            index += self.time_signature["count"]/aggression
            while melody_index < len(self.melody) and self.melody[melody_index]["time"] < index:
                melody_index += 1
            bass.append(note)
        return bass

    def _b_slide(self, args={}):
        log("  Bass: Slide")
        bass = []
        index = 0
        melody_index = 0
        next_melody_index = 0
        slide_duration = Util().random_choice([0.5, 1])
        pitch_drop = Util().random_choice([12, 24])
        note_duration = self.time_signature["count"] / Util().random_choice([1, 2])
        should_break = False
        if self.base_note < 55:
            pitch_drop += 12
        while index < self.melody[-1]["time"] and melody_index < len(self.melody):
            while next_melody_index < len(self.melody) and self.melody[next_melody_index]["time"] < index:
                next_melody_index += 1
            current_melody = {"pitch": self.melody[melody_index]["pitch"], "index": self.melody[melody_index]["index"]}
            next_melody = {"pitch": self.melody[next_melody_index]["pitch"], "index": self.melody[next_melody_index]["index"]}
            next_melody_index = self.melody[next_melody_index]["pitch"]
            hold_note = {
                "pitch":max(self.melody[melody_index]["pitch"]-pitch_drop, 1), "time":index, "duration":note_duration - slide_duration, "volume":75, "index":self.melody[melody_index]["index"]
            }
            index += note_duration
            if index < self.melody[-1]["time"]:
                hold_note["duration"] += slide_duration
                should_break = True
            bass.append(hold_note)
            if should_break:
                break
            slide_note = {
                "time": index + hold_note["duration"], "duration": slide_duration, "volume": 100, "pitch": 0, "index": 0
            }
            slide_index = next_melody["index"] - 1
            if current_melody["pitch"] > next_melody["pitch"]:
                slide_index = next_melody["index"] + 1
            slide_note["index"] = slide_index
            slide_note["pitch"] = min(max(12 * int(slide_index / len(self.scale)) + self.scale[slide_index % len(self.scale)] + self.base_note - pitch_drop, 1), 126)
            bass.append(slide_note)
            melody_index = next_melody_index
        return bass

    def bass(self, args={}):
        type="random"
        if "bass_type" in args:
            type = args["bass_type"]
        if type=="slide":
            bass = self._b_slide(args)
        elif type=="pulse":
            bass = self._b_pulse(args)
        else:
            generation_type = [getattr(self, '_b_slide'), getattr(self, '_b_pulse')]
            bass = Util().random_choice(generation_type)(args=args)
        self.bass = bass

    def _r_atonal(self, args):
        log("  Atonal Rhythm")
        rhythm = []
        index = 0;
        # Setting up a baseline for right now
        # Create a config for note lists
        pattern = Util().random_choice([[0.125,0.125,0.125,0.125], [0.25, 0.25, 0.25, 0.25], [0.4,0.1,0.4,0.1],[0.34,0.33,0.33]])
        total_duration = self.melody[-1]["time"] # + self.melody[-1]["duration"]
        while index < total_duration:
            for i in range(len(pattern)):
                volume = 30
                if i%4 == 0:
                    volume += 20
                if i%2 == 0:
                    volume += 20
                rhythm.append({"pitch":38,"time":index,"duration":0.05,"volume":volume})
                index += pattern[i]
        return rhythm;

    def _r_tonal(self, args):
        log("  Tonal Rhythm")
        rhythm = []
        index = 0;
        # Setting up a baseline for right now
        # Create a config for note lists
        pattern = Util().random_choice([[0.5,0.5,0.5,0.5], [1, 1, 1, 1], [1.6,0.4,1.6,0.4],[1.34,1.33,1.33]])
        total_duration = self.melody[-1]["time"] # + self.melody[-1]["duration"]
        while index < total_duration:
            for i in range(len(pattern)):
                volume = 60
                if i%4 == 0:
                    volume += 20
                if i%2 == 0:
                    volume += 20
                rhythm.append({"pitch":38,"time":index,"duration":0.05,"volume":volume})
                if i%4 == 0:
                    rhythm.append({"pitch":36,"time":index,"duration":0.05,"volume":volume})
                elif i%4 == 1:
                    rhythm.append({"pitch":42,"time":index,"duration":0.05,"volume":volume})
                elif i%4 == 2:
                    rhythm.append({"pitch":37,"time":index,"duration":0.05,"volume":volume})
                elif i%4 == 3:
                    rhythm.append({"pitch":44,"time":index,"duration":0.05,"volume":volume})
                index += pattern[i]
        return rhythm;

    def rhythm(self, args={}):
        percussion_chance = 75
        type="random"
        if "rhythm_type" in args:
            type = args["rhythm_type"]
            percussion_chance = 100
        if random.randint(0,100) > percussion_chance:
            self.rhythm = []
            return
        if type == "atonal":
            self.rhythm = self._r_atonal(args)
        elif type == "tonal":
            self.rhythm = self._r_tonal(args)
        else:
            generation_type = [getattr(self, '_r_atonal'), getattr(self, '_r_tonal')]
            self.rhythm = Util().random_choice(generation_type)(args=args)

    def _pp_keychange(self, on_verse):
        keychange_threshold = 25
        if on_verse[1] < 3 or random.randint(0, 100) > keychange_threshold:
            return
        log("Applying keychange to song on final " + on_verse[0])
        timestamp_start = 0;
        # Todo get suitable candidate for key change
        # Get note delta from base note
        # Do I go for a straight note change, or recalculate based on supplied index and change the scale?
        # Base implementation: Apply a flat note delta
        note_delta = 4 # Improve a third
        # Advanced:
        """
        Decide a new key (and scale?), and figure out an optimal bridge from old => new
        Use an index_delta value and recalculate notes based on new_base_note, index, and index_delta
        """

        for i in self.metadata["melody"][::-1]:
            if i["component"] == on_verse[0]:
                timestamp_start = i["start"]
                break
        for i in self.melody:
            if i["time"] > timestamp_start:
                i["pitch"] += note_delta
        for i in self.harmony:
            if i["time"] > timestamp_start:
                i["pitch"] += note_delta
        for i in self.bass:
            if i["time"] > timestamp_start:
                i["pitch"] += note_delta

    def _pp_dynamics(self, verse_frequency):
        pass

    def _pp_tempo(self, verse_frequency):
        self.events.append({"type":"tempo","time":0,"value":self.tempo})
        tempochange_threshold = 50
        temposlow_threshold = 20
        if verse_frequency[0][1] > 1 and random.randint(0, 100) < tempochange_threshold:
            log("  Applying tempo change to song on final " + verse_frequency[0][0])
            for i in self.metadata["melody"][::-1]:
                if i["component"] == verse_frequency[0][0]:
                    self.events.append({"type":"tempo","time":i["start"],"value":numpy.random.normal(10, 10)+self.tempo})
                    break
        if random.randint(0, 100) < temposlow_threshold:
            log("  Applying slowdown on final part of song")
            new_tempo = int(self.tempo / 2)
            step_increment = int(new_tempo / (self.time_signature["count"]*2))
            for i in self.melody[::-1]:
                if new_tempo >= self.tempo:
                    break
                self.events.append({"type":"tempo","time":i["time"],"value":new_tempo})
                new_tempo = new_tempo + step_increment

    def _pp_melodyvoice(self, verse_frequency):
        newvoice_threshold=45
        if random.randint(0, 100) > newvoice_threshold:
            return
        log("  Doubling melody voice on a verse")
        selected_verse = verse_frequency[0][0]
        acceptable_deltas = []
        if self.base_note > 60:
            acceptable_deltas.append(-12)
        if self.base_note < 75:
            acceptable_deltas.append(12)
        delta = Util().random_choice(acceptable_deltas)
        for i in range(len(self.metadata["melody"])-1):
            if self.metadata["melody"][i]["component"] == selected_verse:
                start_time = self.metadata["melody"][i]["start"]
                end_time = self.metadata["melody"][i+1]["start"]
        for i in self.melody:
            if i["time"] >= end_time:
                break
            if i["time"] >= start_time and i["time"] <= end_time:
                self.melody.append({"pitch":i["pitch"]+delta,"duration":i["duration"],"time":i["time"],"index":i["index"],"volume":i["volume"]-15})

    # Handle any post-processing, such as optionally fading out at the end of the song, adding a padding so song doesn't cut out, etc
    def postprocess(self):
        hold_note = {"pitch":0,"time":self.melody[-1]["time"]+1, "duration":4, "volume":0}
        self.melody.append(hold_note)
        # Keychange handler
        verse_frequency = collections.Counter(self.metadata["melody_structure"]).most_common()
        self._pp_keychange(verse_frequency[0])
        # Idea: If a melody note has a long duration and a harmony follows it, Change the harmony hold to a roll.
        self._pp_dynamics(verse_frequency)
        self._pp_tempo(verse_frequency)
        self._pp_melodyvoice(verse_frequency)

    def finalize(self):
        song = {"melody": { "channel": 0, "note_series": [], "program": 0},
                "harmony": { "channel": 1, "note_series": [], "program": 0},
                "bass": { "channel": 2, "note_series": [], "program": 0},
                "rhythm": { "channel": 9, "note_series": [], "program": 0}}
        program_set = Util().random_choice(Util().instrument_sets)
        for key in program_set:
            song[key]["program"] = program_set[key]
        song["melody"]["note_series"] = self.melody
        song["harmony"]["note_series"] = self.harmony
        song["bass"]["note_series"] = self.bass
        song["rhythm"]["note_series"] = self.rhythm
        self.song = song

class Transcriber:
    # https://soundprogramming.net/file-formats/general-midi-instrument-list/
    # 1 track, each index is a channel
    def __init__(self, file_name):
        self.file_name = file_name

    def compile(self, song_generator):
        self.generator = MIDIFile(1)
        for i in song_generator.song:
            self.generator.addProgramChange(0, song_generator.song[i]["channel"], 0, song_generator.song[i]["program"])
            for note in song_generator.song[i]["note_series"]:
                self.generator.addNote(0, song_generator.song[i]["channel"], note["pitch"], note["time"], note["duration"], note["volume"])
        for i in song_generator.events:
            if i["type"] == "tempo":
                self.generator.addTempo(0, i["time"], i["value"])
        self.write_to_file()

    def write_to_file(self):
        with open(self.file_name, "wb") as output_file:
            self.generator.writeFile(output_file)

def loadArgsFromFile(filename):
    file = open(filename, "r")
    data = file.read()
    return yaml.load(data)

# Load unique params here
def loadCustomArgs(args):
    custom_args = {}
    pass
    return custom_args

def main(argv):
    global verbose_log
    global debug_log
    opts, args = getopt.getopt(argv, 'vdhp:o:c:s:', ['verbose', 'debug', 'help', 'output=','config=','params=','seed='])
    song_name = time.strftime('song-%Y-%m-%d_%H%M%S.mid')
    custom_args = {}
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('python '+__main__.__file__+' [--output=<outputfile>] [--help] [--config=<config_file>] [--params=<params>]')
            return
        elif opt in ("-v", "--verbose"):
            verbose_log = True
        elif opt in ("-d", "--debug"):
            debug_log = True
        elif opt in ("-o", "--output"):
            song_name = arg
        elif opt in ("-c", "--config"):
            custom_args = loadArgsFromFile(arg)
        elif opt in ("-p", "--params"):
            continue
        elif opt in ("-s", "--seed"):
            seed = int(hashlib.sha256(arg.encode('utf-8')).hexdigest(), 16) % (2**32 - 1)
            random.seed(seed)
            numpy.random.seed(seed)
    log("Starting...")
    generator = Generator(custom_args)
    transcriber = Transcriber(song_name)
    transcriber.compile(generator)
    log("Complete. Song stored in " + song_name)

if __name__ == "__main__":
    main(sys.argv[1:])
