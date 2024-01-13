import chart_parser
import config
import pygame
from dataclasses import dataclass

@dataclass
class Track:
    id : int
    justPressed : bool
    isHeld : bool

class Scoring:
    def __init__(self):
        self.currentStreak = 0
        self.hitNotes = 0
        self.tracks = {}
        self.initialiseTracks()
    
    def initialiseTracks(self):
        self.tracks = {}
        for track in config.TRACK_BINDS:
            self.tracks[track] = Track(track, False, False)

    def updateTracks(self, heldKeys : list[bool]):
        for track, key in config.TRACK_BINDS.items():
            keyPressedThisFrame = heldKeys[key]
            if self.tracks[track].justPressed and keyPressedThisFrame:
                print(f"HOLDING TRACK {track}")
                self.tracks[track].justPressed = False
                self.tracks[track].isHeld = True
            elif ((not self.tracks[track].justPressed) and (not self.tracks[track].isHeld)) and keyPressedThisFrame:
                print(f"PRESSED TRACK {track}")
                self.tracks[track].justPressed = True
                self.tracks[track].isHeld = False
            elif (not keyPressedThisFrame) and (self.tracks[track].justPressed or self.tracks[track].isHeld):
                print(f"LIFTED TRACK {track}")
                self.tracks[track].justPressed = False
                self.tracks[track].isHeld = False

    def checkNotes(self, foundNotes : list[chart_parser.Note], scoreBarSeconds : float, dt : float):
        pass