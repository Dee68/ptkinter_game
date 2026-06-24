import pygame

pygame.mixer.init()

# plays sound
def play_sound(path):
    sound = pygame.mixer.Sound(path)
    sound.play()
    
# stops sound  
def mute_sound():
    pygame.mixer.stop()
        