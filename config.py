from pygame import Vector2

#Song Data
CHART_PATH = "Songs/badguy.chart" #Path to chart file.
DIFFICULTY_PREF = "MediumSingle" #Preffered difficulty, easiest available will be selected if not present.
SONG_LOOKAHEAD_MS = 1500 #Lower number means larger gaps between notes but they move visually faster.

#Pixel Scaling
PIXEL_REDUCTION_FACTOR = 3 #What to divide the original screen resolution by.

#Colours
BACKGROUND_COLOUR = (0, 18, 25)
TRACK_BARRIER_COLOUR = (148, 210, 189)

#Board Variables
VANISHING_POINT_POSITION = Vector2(0.5, 0.2)
TRACK_CENTRE_POSITION = Vector2(0.5, 0.9)
TRACKS_MAX_WIDTH = 0.5
TRACK_MAX_WIDTH = 0.2
TRACK_FADEOFF_DISTANCE = 50 #Pixels to fadeoff
TRACK_FADEOFF_GRADIENT = [0, 0, 150, 255] #Possible alphas, spread evenly through fadeoff

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