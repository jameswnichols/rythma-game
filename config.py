from pygame import Vector2

#Song Data
CHART_PATH = "Songs/notes.chart" #Path to chart file.
DIFFICULTY_PREF = "ExpertSingle" #Preffered difficulty, easiest available will be selected if not present.
SONG_LOOKAHEAD_MS = 3000 #Lower number means larger gaps between notes but they move visually faster.
SONG_SCOREBAR_MS = 500
#Pixel Scaling
PIXEL_REDUCTION_FACTOR = 3 #What to divide the original screen resolution by.

#Colours
BACKGROUND_COLOUR = (9, 17, 20)
TRACK_BARRIER_COLOUR = (157, 157, 157)
TRACK_BARRIER_SHADE_COLOUR = (112, 112, 112)
NOTE_COLORS = {0: (83, 143, 0), 1: (192, 40, 52), 2: (243, 142, 0), 3: (39, 164, 244), 4: (204, 77, 0)}

#Board Variables
VANISHING_POINT_POSITION = Vector2(0.5, 0.2)
TRACK_CENTRE_POSITION = Vector2(0.5, 0.9)
TRACKS_MAX_WIDTH = 0.5
TRACK_MAX_WIDTH = 0.2
TRACK_FADEOFF_DISTANCE = 50 #Pixels to fadeoff.
TRACK_FADEOFF_GRADIENT = [0, *[i for i in range(0, 255)]] #Possible alphas, spread evenly through fadeoff.
TRACK_BOTTOM_FADEOFF_GRADIENT = [*[i for i in range(255, 0, -1)]]
TRACK_BOTTOM_FADEOFF_OFFSET = 10 #Pixels from the scoreline.
TRACK_BOTTOM_FADEOFF_DISTANCE = 50
TRACK_BOTTOM_BUFFER = 0.3

#Note Variables
NOTE_DEPTH_MS = 50 #ms
NOTE_GRACE_MS = 70 #ms
NOTE_WIDTH = 0.3 #Percentage to take off each side of track width.
NOTE_HEIGHT = 0.5 #Percentage of note width.
NOTE_SIDE_COLOUR_MULTIPLIER = 0.7
NOTE_TOP_COLOUR_MULTIPLIER = 1.3

#Track VFX Variables
TRACK_VFX_LENGTH = 0.6 #How far should the vfx be polled.
TRACK_VFX_NUM_POINTS = 50 #How many points should be generated.
TRACK_VFX_SPRING_CONSTANT = 0.005
TRACK_VFX_SPRING_CONSTANT_BASELINE = 1
TRACK_VFX_DAMPING = 0.98
TRACK_VFX_ITERATIONS = 5
TRACK_VFX_PRESS_STRENGTH = 0.03
TRACK_VFX_MAX_STRAY = 0.05
TRACK_VFX_SIN_X_MULTIPLIER = 20
TRACK_VFX_SIN_Y_MULTIPLIER = 0.5