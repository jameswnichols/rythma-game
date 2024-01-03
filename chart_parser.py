import re

SECTION_PATTERN = re.compile("\[\w+\]")

class File:
    def __init__(self, filepath : str):
        self.filepath = filepath
        self.Resolution = None
        self.musicPath = None
    
    def loadSections(self):
        fileData = None
        sections = {}
        with open(self.filepath, "r") as f:
            fileData = f.readlines()
        
        for line in fileData:
            
            result = SECTION_PATTERN.match(line)
            if not result:
                continue

            print(result)
        