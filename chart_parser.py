import re
import ast
from dataclasses import dataclass
SECTION_PATTERN = re.compile("\[\w+\]")

@dataclass
class Note:
    pos: int
    key: int
    duration : int

class Song:
    def __init__(self, filepath : str):
        self.filepath = filepath
        self.resolution = 192
        self.musicPath = None
        self.songName = None
        self.artistName = None
        self.timesig = "4 4"
        self.tempoData = {}
        self.noteData = {}
        self.notesPositionList = []
        self.lastPassedNotePositionIndex = None
        self.tempo = 120000
        self.loadSections()
        self.updateTempo(0)
    
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
        self.musicPath = songData["MusicStream"]
        self.songName = songData["Name"]
        self.artistName = songData["Artist"]
        self.resolution = songData["Resolution"]
    
    def __loadSyncTrack(self, lines):
        self.tempoData = {}
        for line in lines:
            if "=" not in line:
                continue
            position, data = line.split("=")
            dataSplit = data.strip().split()
            if dataSplit[0] == "B":
                self.tempoData[int(position)] = int(dataSplit[1])

    def __loadNoteTrack(self, lines):
        self.noteData = {}
        self.notesPositionList = []
        for line in lines:
            if "=" not in line:
                continue
            position, data = line.split("=")
            dataSplit = data.strip().split()
            if dataSplit[0] in ["E","S"]:
                continue
            _, key, duration = dataSplit
            self.noteData[int(position)] = Note(int(position), key, duration)
        
        self.notesPositionList = list(self.noteData.keys())

    def updateTempo(self, position):
        for pos, tempo in self.tempoData.items():
            if position >= pos:
                self.tempo = tempo
    
    def getPosition(self, elapsedTime : int):
        elapsedMinutes = elapsedTime / 1000 / 60
        return elapsedMinutes * (self.tempo / 1000) * self.resolution
    
    def getNotes(self, minimumPos, maximumPos):
        checkedIndex = self.lastPassedNotePositionIndex if self.lastPassedNotePositionIndex else 0
        notes = []
        while checkedIndex < len(self.notesPositionList):
            position = self.notesPositionList[checkedIndex]

            if position >= maximumPos:
                return notes

            if position >= minimumPos:
                notes.append(self.noteData[position])
            
            if position < minimumPos:
                self.lastPassedNotePositionIndex = checkedIndex
            
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
                case "EasySingle":
                    self.__loadNoteTrack(lines)