import re

SECTION_PATTERN = re.compile("\[\w+\]")

class File:
    def __init__(self, filepath : str):
        self.filepath = filepath
        self.Resolution = None
        self.musicPath = None
        self.loadSections()
    
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
            currentSection = str(result).replace("[","").replace("]","")
            sections[currentSection] = []
            print(currentSection)
        