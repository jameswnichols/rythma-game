import pygame
import pygame.gfxdraw
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
        self.boardSurface = pygame.Surface(self.size, pygame.SRCALPHA)
        self.noteSurface = pygame.Surface(self.size, pygame.SRCALPHA)

    def update(self, size : Vector2):
        if size != self.size:
            self.size = size
            self.boardSurface = pygame.Surface(self.size, pygame.SRCALPHA)
            self.noteSurface = pygame.Surface(self.size, pygame.SRCALPHA)
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

    def generateAlpha(self, surface : pygame.Surface, centre : Vector2, distance : float, gradient : list):
        for i in range(distance):
            alphaIndex = int(len(gradient) * (i / distance))
            alpha = gradient[alphaIndex]
            alphaCentreVector = Vector2(i - i/2, i - i/2)
            screenPosition = centre - alphaCentreVector
            alphaRect = pygame.Rect(*screenPosition, i, i)
            surface.fill((255,255,255,alpha),alphaRect,special_flags=pygame.BLEND_RGBA_MULT)

    def generateVerticalAlpha(self, surface : pygame.Surface, area : pygame.Rect, gradient : list):
        for y in range(area.y, area.y+area.height):
            alphaIndex = int(((y-area.y) / area.height) * len(gradient))
            alpha = gradient[alphaIndex]
            alphaRect = pygame.Rect(area.x, y, area.width, area.height)
            surface.fill((255,255,255,alpha), alphaRect, special_flags=pygame.BLEND_RGBA_MULT)

    def render(self, surface : pygame.Surface, notes : list[chart_parser.Note], headerTime : float, footerTime : float):
        self.boardSurface.fill((0,0,0,0))

        scoreLinePercentage = 1 - ((config.SONG_SCOREBAR_MS/1000) / (config.SONG_LOOKAHEAD_MS/1000))
        scoreLineStart = self.trackStartingPosition
        scoreLineEnd = self.trackStartingPosition + Vector2(self.widthPerTrack * self.tracks, 0)
        scoreLineStartVector = config.VANISHING_POINT_POSITION.lerp(scoreLineStart, scoreLinePercentage)
        scoreLineEndVector = config.VANISHING_POINT_POSITION.lerp(scoreLineEnd, scoreLinePercentage)
        scoreLineStartScreenSpace = scoreLineStartVector.elementwise() * self.size.elementwise()
        scoreLineEndScreenSpace = scoreLineEndVector.elementwise() * self.size.elementwise()
        scoreLineStartShadow = scoreLineStartScreenSpace + Vector2(0, 1)
        scoreLineEndShadow = scoreLineEndScreenSpace + Vector2(0, 1)

        pygame.draw.line(self.boardSurface, config.TRACK_BARRIER_SHADE_COLOUR, scoreLineStartShadow, scoreLineEndShadow)

        for barrier, points in self.barrierPoints.items():
            renderPoints = [point.renderpos.elementwise() * self.size.elementwise() for point in list(points.values())]
            shadowPoints = [(point.renderpos.elementwise() * self.size.elementwise()) + Vector2(0, 1) for point in list(points.values())]
            pygame.draw.lines(self.boardSurface, config.TRACK_BARRIER_SHADE_COLOUR, False, shadowPoints)
            pygame.draw.lines(self.boardSurface, config.TRACK_BARRIER_COLOUR, False, renderPoints)
        
        pygame.draw.line(self.boardSurface, config.TRACK_BARRIER_COLOUR, scoreLineStartScreenSpace, scoreLineEndScreenSpace)

        self.renderNotes(self.boardSurface, notes, headerTime, footerTime)
        self.generateAlpha(self.boardSurface, self.size.elementwise() * config.VANISHING_POINT_POSITION.elementwise(),config.TRACK_FADEOFF_DISTANCE,config.TRACK_FADEOFF_GRADIENT)

        blurStartPosition = scoreLineStartScreenSpace - Vector2(scoreLineStartScreenSpace.x*config.TRACK_BOTTOM_BUFFER, -config.TRACK_BOTTOM_FADEOFF_OFFSET)
        blurEndPosition = scoreLineEndScreenSpace + Vector2(scoreLineEndScreenSpace.x*config.TRACK_BOTTOM_BUFFER, config.TRACK_BOTTOM_FADEOFF_OFFSET)
        blurWidth = (blurEndPosition.x - blurStartPosition.x)
        blurHeight = (self.barrierPoints[0][0].renderpos.elementwise() * self.size.elementwise()).y - blurStartPosition.y
        self.generateVerticalAlpha(self.boardSurface,pygame.Rect(blurStartPosition, Vector2(blurWidth, blurHeight)),config.TRACK_BOTTOM_FADEOFF_GRADIENT)#config.TRACK_FADEOFF_GRADIENT
        
        surface.blit(self.boardSurface, (0, 0))
    
    def renderNotes(self, surface : pygame.Surface, notes : list[chart_parser.Note], headerTime : float, footerTime : float):
        self.noteSurface.fill((0,0,0,0))

        #foundNotes = song.getNotes(headerTime, footerTime)
        for i in range(0, len(notes)):
            note = notes[len(notes)-1-i]
            #Percentage of how far the note should be down the track
            noteStartPercentage = -1 * ((note.startSeconds - footerTime) / (footerTime - headerTime)) #1 is at header, 0 is far away
            noteEndPercentage = -1 * ((note.startSeconds + 2*(config.NOTE_DEPTH_MS/1000) - footerTime) / (footerTime - headerTime))
            noteTailPercentage = -1 * ((note.endSeconds - footerTime) / (footerTime - headerTime))
            noteStartPercentage = max(0, min(noteStartPercentage, 1))
            noteEndPercentage = max(0, min(noteEndPercentage, 1))
            noteTailPercentage = max(0, min(noteTailPercentage, 1))

            noteLeftPosition = Vector2(self.widthPerTrack * note.track, 0) + self.trackStartingPosition + Vector2(self.widthPerTrack * config.NOTE_WIDTH,0)
            noteRightPosition = Vector2(self.widthPerTrack * (note.track + 1), 0) + self.trackStartingPosition - Vector2(self.widthPerTrack * (config.NOTE_WIDTH),0)
            noteTailLeftPosition = Vector2(self.widthPerTrack * note.track, 0) + self.trackStartingPosition + Vector2(self.widthPerTrack * config.NOTE_TAIL_WIDTH,0)
            noteTailRightPosition = Vector2(self.widthPerTrack * (note.track + 1), 0) + self.trackStartingPosition - Vector2(self.widthPerTrack * (config.NOTE_TAIL_WIDTH),0)

            noteStartLeftVector = config.VANISHING_POINT_POSITION.lerp(noteLeftPosition, noteStartPercentage)
            noteStartRightVector = config.VANISHING_POINT_POSITION.lerp(noteRightPosition, noteStartPercentage)
            noteEndLeftVector = config.VANISHING_POINT_POSITION.lerp(noteLeftPosition, noteEndPercentage)
            noteEndRightVector = config.VANISHING_POINT_POSITION.lerp(noteRightPosition, noteEndPercentage)

            noteTailStartLeftVector = config.VANISHING_POINT_POSITION.lerp(noteTailLeftPosition, noteStartPercentage)
            noteTailEndLeftVector = config.VANISHING_POINT_POSITION.lerp(noteTailLeftPosition, noteTailPercentage)
            noteTailStartRightVector = config.VANISHING_POINT_POSITION.lerp(noteTailRightPosition, noteStartPercentage)
            noteTailEndRightVector = config.VANISHING_POINT_POSITION.lerp(noteTailRightPosition, noteTailPercentage)

            frontNoteWidth = noteStartRightVector.x - noteStartLeftVector.x
            endNoteWidth = noteEndRightVector.x - noteEndLeftVector.x
            frontNoteHeight = Vector2(0, frontNoteWidth * config.NOTE_HEIGHT)
            endNoteHeight = Vector2(0, endNoteWidth * config.NOTE_HEIGHT)

            noteTopStartLeftSS = (noteStartLeftVector - frontNoteHeight).elementwise() * self.size.elementwise()
            noteTopStartRightSS = (noteStartRightVector - frontNoteHeight).elementwise() * self.size.elementwise()
            noteTopEndLeftSS = (noteEndLeftVector - endNoteHeight).elementwise() * self.size.elementwise()
            noteTopEndRightSS = (noteEndRightVector - endNoteHeight).elementwise() * self.size.elementwise()

            noteStartLeftSS = noteStartLeftVector.elementwise() * self.size.elementwise()
            noteStartRightSS = noteStartRightVector.elementwise() * self.size.elementwise()
            noteEndLeftSS = noteEndLeftVector.elementwise() * self.size.elementwise()
            noteEndRightSS = noteEndRightVector.elementwise() * self.size.elementwise()

            noteTailStartLeftSS = noteTailStartLeftVector.elementwise() * self.size.elementwise()
            noteTailEndLeftSS = noteTailEndLeftVector.elementwise() * self.size.elementwise()
            noteTailStartRightSS = noteTailStartRightVector.elementwise() * self.size.elementwise()
            noteTailEndRightSS = noteTailEndRightVector.elementwise() * self.size.elementwise()

            noteSideColour = tuple([max(x*config.NOTE_SIDE_COLOUR_MULTIPLIER,0) for x in config.NOTE_COLORS[note.track]])
            noteTopColour = tuple([min(x*config.NOTE_TOP_COLOUR_MULTIPLIER, 255) for x in config.NOTE_COLORS[note.track]])

            #Hold Note Tail
            pygame.gfxdraw.filled_polygon(self.noteSurface,(noteTailStartLeftSS, noteTailEndLeftSS, noteTailEndRightSS, noteTailStartRightSS),config.NOTE_COLORS[note.track])

            #Left Side
            pygame.gfxdraw.filled_polygon(self.noteSurface,(noteEndLeftSS, noteTopEndLeftSS, noteTopStartLeftSS, noteStartLeftSS), noteSideColour)
            #Right Side
            pygame.gfxdraw.filled_polygon(self.noteSurface,(noteEndRightSS, noteTopEndRightSS, noteTopStartRightSS, noteStartRightSS), noteSideColour)
            #Top
            pygame.gfxdraw.filled_polygon(self.noteSurface,(noteTopEndLeftSS, noteTopStartLeftSS, noteTopStartRightSS, noteTopEndRightSS), (*noteTopColour,config.NOTE_TOP_ALPHA))
            #Front
            pygame.gfxdraw.filled_polygon(self.noteSurface,(noteTopStartLeftSS, noteTopStartRightSS, noteStartRightSS, noteStartLeftSS), config.NOTE_COLORS[note.track])
            
        surface.blit(self.noteSurface, (0, 0))