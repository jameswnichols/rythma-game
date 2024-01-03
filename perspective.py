import pygame
from pygame import Vector2
import config
from dataclasses import dataclass

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

                    clampedY = max(point.baseline.y-config.TRACK_VFX_MAX_STRAY, min(point.pos.y, point.baseline.y+config.TRACK_VFX_MAX_STRAY))
                    change = point.pos.y - clampedY
                    point.pos.y = clampedY
                    point.renderpos.y - change


    def addWave(self, barrier : int):
        currentYHeight = self.barrierPoints[barrier][1].pos.y
        maxYHeight = self.barrierPoints[barrier][1].baseline.y - config.TRACK_VFX_MAX_STRAY
        change = currentYHeight - min(currentYHeight - config.TRACK_VFX_PRESS_STRENGTH,maxYHeight)
        self.barrierPoints[barrier][1].pos.y -= change
        self.barrierPoints[barrier][1].renderpos.y -= change

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

                alpha = int(255 * ((len(pointsList) - i) / len(pointsList)))

                pygame.draw.line(self.drawSurface, (*config.TRACK_BARRIER_COLOUR, alpha), renderPoint, nextPoint)
        
        surface.blit(self.drawSurface, (0, 0))


        
