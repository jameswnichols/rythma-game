import re
import ast
from dataclasses import dataclass
SECTION_PATTERN = re.compile("\[\w+\]")

@dataclass
class Note:
    pos: int
    key: int
    duration : int

class File:
    def __init__(self, filepath : str):
        self.filepath = filepath
        self.resolution = 192
        self.musicPath = None
        self.songName = None
        self.artistName = None
        self.timesig = "4 4"
        self.tempoData = {}
        self.noteData = {}
        self.loadSections()
    
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
        for line in lines:
            if "=" not in line:
                continue
            position, data = line.split("=")
            dataSplit = data.strip().split()
            if dataSplit[0] in ["E","S"]:
                continue
            _, key, duration = dataSplit
            self.noteData[position] = Note(position, key, duration)

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