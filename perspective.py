import pygame
from pygame import Vector2
import config
from dataclasses import dataclass
import chart_parser

@dataclass
class VFXPoint:
    pos : Vector2
    renderpos : Vector2
    baseline : Vector2
    renderbaseline : Vector2
    speed : Vector2
    mass : float

class Board:
    def __init__(self, surface : pygame.Surface, tracks : int = 4):
        self.tracks = tracks
        self.barrierPoints = {}
        self.size = None
        self.update(Vector2(surface.get_size()))
        self.createBarrierPoints()
        self.updateBarrierPoints([i for i in range(self.tracks+1)])
        self.drawSurface = pygame.Surface(self.size, pygame.SRCALPHA)

    def update(self, size : Vector2):
        if size != self.size:
            self.size = size
            self.drawSurface = pygame.Surface(self.size, pygame.SRCALPHA)
            widthPerTrack = (config.TRACKS_MAX_WIDTH) / self.tracks
            self.widthPerTrack = min(config.TRACK_MAX_WIDTH, widthPerTrack)
            self.trackStartingPosition = config.TRACK_CENTRE_POSITION - Vector2((self.tracks * self.widthPerTrack)/2, 0)

    def createBarrierPoints(self):
        self.barrierPoints = {}
        for barrier in range(self.tracks + 1):
            self.barrierPoints[barrier] = {}
            barrierStartPoint = self.trackStartingPosition + Vector2(self.widthPerTrack * barrier, 0)
            for p in range(config.TRACK_VFX_NUM_POINTS):
                pointPerc = p / config.TRACK_VFX_NUM_POINTS
                renderBarrierPoint = barrierStartPoint.lerp(config.VANISHING_POINT_POSITION, pointPerc)
                barrierPoint = Vector2(renderBarrierPoint.x, 0)
                self.barrierPoints[barrier][p] = VFXPoint(pos=barrierPoint, baseline=barrierPoint, renderpos=renderBarrierPoint, renderbaseline=renderBarrierPoint, speed=Vector2(0, 0), mass=1)

    def updateBarrierPoints(self, barriers : list):
        for barrier in barriers:
            barrierPoints = self.barrierPoints[barrier]
            indList = list(barrierPoints.keys())
            for iter in range(config.TRACK_VFX_ITERATIONS):
                for ind, point in barrierPoints.items():

                    if ind > len(barrierPoints) * config.TRACK_VFX_LENGTH:
                        break

                    force = 0
                    forceFromLeft = 0
                    forceFromRight = 0
                    if ind != 0:
                        dy = barrierPoints[ind - 1].pos.y - point.pos.y
                        forceFromLeft = config.TRACK_VFX_SPRING_CONSTANT * dy
                    if ind != len(indList) - 1:
                        dy = barrierPoints[ind + 1].pos.y - point.pos.y
                        forceFromRight = config.TRACK_VFX_SPRING_CONSTANT * dy
                    dy = point.baseline.y - point.pos.y
                    forceToBaseline = config.TRACK_VFX_SPRING_CONSTANT_BASELINE * dy
                    force += forceFromLeft + forceFromRight + forceToBaseline
                    acceleration = force / point.mass
                    point.speed.y = (config.TRACK_VFX_DAMPING * point.speed.y + acceleration)
                    
                    #Prevents line from permanently moving up by locking first and last pos
                    if 0 < ind < len(indList) -1:
                        point.pos.y += point.speed.y
                        point.renderpos.y += point.speed.y
                    else:
                        point.pos.y = point.baseline.y
                        point.renderpos.y = point.renderbaseline.y

                    point.pos.y = max(point.baseline.y-config.TRACK_VFX_MAX_STRAY, min(point.pos.y, point.baseline.y+config.TRACK_VFX_MAX_STRAY))
                    point.renderpos.y = max(point.renderbaseline.y-config.TRACK_VFX_MAX_STRAY, min(point.renderpos.y, point.renderbaseline.y+config.TRACK_VFX_MAX_STRAY))


    def addWave(self, barrier : int, value : float = config.TRACK_VFX_PRESS_STRENGTH):
        point = self.barrierPoints[barrier][1]
        point.pos.y = max(point.baseline.y-config.TRACK_VFX_MAX_STRAY, min(point.pos.y - value, point.baseline.y+config.TRACK_VFX_MAX_STRAY))
        point.renderpos.y = max(point.renderbaseline.y-config.TRACK_VFX_MAX_STRAY, min(point.renderpos.y - value, point.renderbaseline.y+config.TRACK_VFX_MAX_STRAY))

    def render(self, surface : pygame.Surface):
        self.drawSurface.fill((0,0,0,0))
        for barrier, points in self.barrierPoints.items():
            renderPoints = {}
            pointsList = list(points.values())
            for i, point in enumerate(pointsList):

                if i == len(pointsList) - 1:
                    continue
                
                renderPoint = None

                if i not in renderPoints:
                    renderPoint = point.renderpos.elementwise() * self.size.elementwise()
                    renderPoints[i] = renderPoint
                else:
                    renderPoint = renderPoints[i]
                
                nextPoint = pointsList[i + 1].renderpos.elementwise() * self.size.elementwise()
                renderPoints[i + 1] = nextPoint

                inversePositionPercentage = (len(pointsList) - i) / (len(pointsList) * config.TRACK_FADEOFF_DISTANCE)

                alpha = int(255 * min(inversePositionPercentage, 1))

                pygame.draw.line(self.drawSurface, (*config.TRACK_BARRIER_COLOUR, alpha), renderPoint, nextPoint)
        
        surface.blit(self.drawSurface, (0, 0))
    
    def renderNotes(self, surface : pygame.Surface, song : chart_parser.Song, headerTime : float, footerTime : float):
        self.drawSurface.fill((0,0,0,0))
        foundNotes = song.getNotes(headerTime, footerTime)

        for note in foundNotes:
            #Percentage of how far the note should be down the track
            noteStartPercentage = -1 * ((note.startSeconds - footerTime) / (footerTime - headerTime)) #1 is at header, 0 is far away
            noteEndPercentage = -1 * ((note.endSeconds - footerTime) / (footerTime - headerTime))

            if (noteEndPercentage != noteStartPercentage) and noteEndPercentage < 0:
                noteEndPercentage = 0

            #difference = self.size.y * (noteStartPercentage - noteEndPercentage) if noteEndPercentage != noteStartPercentage else 1

            notePosition = Vector2(self.widthPerTrack * note.track, 0) + (self.trackStartingPosition + Vector2(self.widthPerTrack / 2, 0))
            noteStartTrackedVector = config.VANISHING_POINT_POSITION.lerp(notePosition, noteStartPercentage)
            notEndTrackedVector = config.VANISHING_POINT_POSITION.lerp(notePosition, noteEndPercentage)
            noteStartScreenSpace = noteStartTrackedVector.elementwise() * self.size.elementwise()
            noteEndScreenSpace =  notEndTrackedVector.elementwise() * self.size.elementwise()

            inverseAlphaPercentage = noteStartPercentage / config.TRACK_FADEOFF_DISTANCE

            alpha = int(255 * min(inverseAlphaPercentage, 1))

            pygame.draw.line(self.drawSurface, (255,0,0,alpha), noteStartScreenSpace, noteEndScreenSpace)
        
        surface.blit(self.drawSurface, (0, 0))

            #noteRect = pygame.Rect(noteStartScreenSpace.x, noteScreenSpace.y, 1, 1)

            #pygame.draw.rect(surface, (255,0,0), noteRect)



