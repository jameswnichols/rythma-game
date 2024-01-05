import pygame
from pygame import Vector2
import config
import perspective
import chart_parser
import math

pygame.init()

screenSize = Vector2(800, 600)

pixelScreenSize = screenSize/config.PIXEL_REDUCTION_FACTOR

KEYS = {pygame.K_a:[0, 1],pygame.K_s:[1, 2],pygame.K_d:[2, 3],pygame.K_SEMICOLON:[3, 4],pygame.K_QUOTE:[4, 5]}

if __name__ == "__main__":
    screen = pygame.display.set_mode(screenSize,pygame.RESIZABLE)
    clock = pygame.time.Clock()
    pixelScreen = pygame.Surface(pixelScreenSize)
    song = chart_parser.Song(config.CHART_PATH)
    board = perspective.Board(pixelScreen, tracks=5)

    running = True
    dt = 0
    elapsedTime = 0

    #pygame.mixer.music.play()

    while running:
        screen.fill(config.BACKGROUND_COLOUR)
        pixelScreen.fill(config.BACKGROUND_COLOUR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.VIDEORESIZE:
                screenSize = Vector2(event.w, event.h)
                pixelScreenSize = screenSize/config.PIXEL_REDUCTION_FACTOR
                screen = pygame.display.set_mode(screenSize,pygame.RESIZABLE)
                pixelScreen = pygame.Surface(pixelScreenSize)
        
        keysPressed = pygame.key.get_pressed()

        for key in KEYS:
            if keysPressed[key]:
                for b in KEYS[key]:
                    board.addWave(b,config.TRACK_VFX_SIN_Y_MULTIPLIER * math.sin(config.TRACK_VFX_SIN_X_MULTIPLIER * elapsedTime) * config.TRACK_VFX_PRESS_STRENGTH)

        #Get Screen "time" and render board + notes
        frontTime = elapsedTime
        endTime = frontTime + config.SONG_LOOKAHEAD_MS / 1000
        foundNotes = song.getNotes(frontTime, endTime)

        board.update(pixelScreenSize)
        board.updateBarrierPoints([i for i in range(board.tracks+1)])
        board.render(pixelScreen, foundNotes, frontTime, endTime)

        #Upscale Pixel Screen
        pygame.transform.scale(pixelScreen,screenSize, screen)

        pygame.display.flip()
        dt = clock.tick_busy_loop(60)/1000
        elapsedTime += dt

        pygame.display.set_caption(f"FPS - {round(clock.get_fps(), 1)} Seconds Elapsed - {int(frontTime)} Notes Rendered - {len(foundNotes)}")

    pygame.quit()