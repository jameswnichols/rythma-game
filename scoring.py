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
                self.tracks[track].justPressed = False
                self.tracks[track].isHeld = True
            elif ((not self.tracks[track].justPressed) and (not self.tracks[track].isHeld)) and keyPressedThisFrame:
                self.tracks[track].justPressed = True
                self.tracks[track].isHeld = False
            elif (not keyPressedThisFrame) and (self.tracks[track].justPressed or self.tracks[track].isHeld):
                self.tracks[track].justPressed = False
                self.tracks[track].isHeld = False

    def checkNotes(self, foundNotes : list[chart_parser.Note], scoreBarSeconds : float, dt : float):
        pressedInLane = {x : False for x in self.tracks}
        for note in foundNotes:
            graceSeconds = 0 if note.beenPressed else config.NOTE_GRACE_MS/1000
            noteHeadStart = note.startSeconds - graceSeconds - (config.NOTE_DEBOUNCE_TIME_MS/1000)
            noteHeadEnd = note.startSeconds + (2*(config.NOTE_DEPTH_MS/1000)) + graceSeconds + (config.NOTE_DEBOUNCE_TIME_MS/1000)
            noteTailEnd = note.endSeconds
            noteWithinRange = noteHeadStart <= scoreBarSeconds <= noteHeadEnd
            if not note.beenPressed and noteWithinRange and self.tracks[note.track].justPressed: #
                note.beenPressed = True
                self.hitNotes += 1
                self.currentStreak += 1
                pressedInLane[note.track] = True
                print(f"Note Hit : {note.pos}")
            elif note.beenPressed and noteWithinRange and self.tracks[note.track].justPressed:
                self.currentStreak = 0
                print(f"Pressed Same Note Twice : {note.pos}")
            elif not note.beenPressed and noteHeadEnd < scoreBarSeconds:
                note.beenPressed = True
                self.currentStreak = 0
                print("Missed Note")
        
        hasStruck = False
        for track, notePressed in pressedInLane.items():
            if not notePressed and self.tracks[track].justPressed:
                hasStruck = True
                break
        
        if hasStruck:
            self.currentStreak
            print("Strike")
        
                
            