import re
import ast
from dataclasses import dataclass
import pygame
import pathlib
import config
SECTION_PATTERN = re.compile("\[\w+\]")

@dataclass
class Note:
    pos : int
    track : int
    endSeconds : int
    startSeconds : float
    index : int

@dataclass
class Tempo:
    bpm : float
    secondsIn : float
    position : int

class Song:
    def __init__(self, filepath : str):
        self.filepath = pathlib.Path(filepath)
        self.resolution = 192
        self.musicPath = None
        self.songName = None
        self.artistName = None
        self.timesig = "4 4"
        self.tempoData = {}
        self.noteData = {}
        self.notePassedList = []
        self.loadSections()
        self.music = None
    
    def __parseData(self, data):
        try:
            return ast.literal_eval(data)
        except:
            return str(data)

    def __loadSongData(self, lines):
        songData = {}
        for line in lines:
            if "=" not in line:
                continue
            definition, data = line.split("=")
            songData[definition.strip()] = self.__parseData(data.strip())
        self.musicPath = pathlib.Path.joinpath(self.filepath.parent.absolute(),songData["MusicStream"])
        self.songName = songData["Name"]
        self.artistName = songData["Artist"]
        self.resolution = songData["Resolution"]

        self.music = pygame.mixer.music.load(self.musicPath)
    
    def __loadSyncTrack(self, lines):
        self.tempoData = {}
        firstTempo = True
        for line in lines:
            if "=" not in line:
                continue
            position, data = line.split("=")
            dataSplit = data.strip().split()
            if dataSplit[0] == "B":
                if firstTempo:
                    firstTempo = False
                    self.tempoData[int(position)] = Tempo(int(dataSplit[1])/1000,0,0)
                else:
                    secondsIn = self.getSecondsIn(int(position))
                    self.tempoData[int(position)] = Tempo(int(dataSplit[1])/1000,secondsIn,int(position))

    def __loadNoteTrack(self, lines):
        self.noteData = []
        index = 0
        for line in lines:
            if "=" not in line:
                continue
            position, data = line.split("=")
            position = int(position)
            dataSplit = data.strip().split()
            if (dataSplit[0] in ["E","S"]) or (int(dataSplit[1]) >= 5):
                continue
            _, track, endSeconds = dataSplit
            self.noteData.append(Note(position, int(track), self.getSecondsIn(position)+self.getSecondsIn(int(endSeconds)), self.getSecondsIn(position), index))
            index += 1

    def getSecondsIn(self, position : int):
        tempo = self.getTempo(position)
        tempoPosition, bpm, tempoSeconds = tempo.position, tempo.bpm, tempo.secondsIn
        deltaTicks = position - tempoPosition
        if position == tempoPosition:
            return tempoSeconds
        secondsIn = ((60 / bpm) * (deltaTicks / self.resolution)) + tempoSeconds
        return secondsIn
    
    def getTempo(self, position : int):
        currentTempo = Tempo(120000,0,0)
        for tempoPosition, tempo in self.tempoData.items():
            if position >= tempoPosition:
                currentTempo = tempo
        return currentTempo
    
    def getNotes(self, minimumTime, maximumTime):
        checkedIndex = self.notePassedList[0] if self.notePassedList else 0
        notes = []
        while checkedIndex < len(self.noteData):
            note = self.noteData[checkedIndex]
            if note.startSeconds >= maximumTime:
                return notes
            if note.startSeconds >= minimumTime - config.SONG_SCOREBAR_MS/1000 or note.endSeconds + 2*(config.NOTE_DEPTH_MS/1000 )>= minimumTime - config.SONG_SCOREBAR_MS/1000:
                if note.index not in self.notePassedList:
                    self.notePassedList.append(note.index)
                notes.append(note)
            if note.endSeconds + 2*(config.NOTE_DEPTH_MS/1000) < minimumTime - config.SONG_SCOREBAR_MS/1000:
                if note.index in self.notePassedList:
                    self.notePassedList.remove(note.index)
            checkedIndex += 1

        return notes

    def loadSections(self):
        fileData = None
        currentSection = None
        sections = {}
        with open(self.filepath, "r") as f:
            fileData = f.readlines()

        for line in fileData:
            line = line.strip()
            result = SECTION_PATTERN.findall(line)
            if not result:
                sections[currentSection].append(line)
                continue
            currentSection = str(result).replace("[","").replace("]","").replace("'","")
            sections[currentSection] = []

        for section, lines in sections.items():
            match section:
                case "Song":
                    self.__loadSongData(lines)
                case "SyncTrack":
                    self.__loadSyncTrack(lines)
                case config.DIFFICULTY_PREF:
                    self.__loadNoteTrack(lines)