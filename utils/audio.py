# import pygame

# pygame.mixer.init()

# # plays sound
# def play_sound(path):
#     sound = pygame.mixer.Sound(path)
#     sound.play()
    
# def play_sound_continue(path):
#     sound = pygame.mixer.Sound(path)
#     sound.play(-1)
    
# # stops sound  
# def mute_sound():
#     pygame.mixer.stop()
        
import pygame

pygame.mixer.init()


# ---------------- Sound Effects ----------------

def play_sound(path):
    effect = pygame.mixer.Sound(path)
    effect.play()


def mute_sound():
    pygame.mixer.stop()

# ---------------- Music ----------------

def play_music(path, loop=-1):
    pygame.mixer.music.load(path)
    pygame.mixer.music.play(loop)


def stop_music():
    pygame.mixer.music.stop()