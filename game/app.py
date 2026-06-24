# the main controller of the application goes here
import tkinter as tk 
import random
import config
from PIL import Image, ImageTk
from utils.image_loader import ImageLoader
from game.target import Target
from game.score import Score
from game.game_state import GameState
from game.gun import Gun
from utils.audio import play_sound, mute_sound

class GameApp:
    """
    Main controller class for the game application.

    This class manages the entire game lifecycle, including:
    - Window and canvas setup (Tkinter UI layer)
    - Player input handling (keyboard events)
    - Game state management (menu, playing, game over)
    - Spawning and updating game entities (gun, bullets, targets)
    - Collision detection and scoring
    - Level progression and difficulty scaling
    - Game loop scheduling

    Architecture role:
        Acts as the central game loop controller coordinating
        all game objects (Gun, Bullet, Target, Score).

    Game states:
        - MENU: Initial screen waiting for player action
        - PLAYING: Active gameplay state
        - GAME_OVER: End state after lives reach zero
    """
    def __init__(self, root:tk.Tk):
        self.root = root
        self.setup_window()
        self.create_canvas()
        self.create_background()
        self.score = Score(self.canvas)
        self.loader = ImageLoader()
        self.target_speed = config.TARGET_SPEED
        self.max_targets = 5
        self.lives = 3
        self.level = 1
        self.keys = set()
        #self.state = GameState.MENU
        self.level_text = self.canvas.create_text(
            200,
            20,
            text=f"Level: {self.level}",
            font=("Arial", 14,"bold"),
            fill="blue",
            tags="level_up"
        )
        self.lives_text = self.canvas.create_text(
            340,
            20,
            text=f"Lives: {self.lives}",
            font=("Arial", 14),
            fill="white"
        )
        self.gun = Gun(self.canvas, self.loader,350,550)
        self.root.bind("<KeyPress>", self.on_key_down)
        self.root.bind("<KeyRelease>", self.on_key_up)
        self.targets = []
        # for _ in range(5):
        #     self.spawn_target()
            
        self.slow_motion = False
        self.slow_motion_end = 0
        self.game_loop()
        
    def setup_window(self):
        self.root.title(config.TITLE)
        self.root.geometry(f"{config.WIDTH}x{config.HEIGHT}")
    
    def create_canvas(self):
        self.canvas = tk.Canvas(
            self.root,
            width=config.WIDTH,
            height=config.HEIGHT,
            bg="#F3EBEE"
        )
        self.canvas.pack(fill="both", expand=True)
        
    def create_background(self):
        # get the image
        self.sky_image_raw = Image.open("assets/images/sky.png")
        # resize it to fit canvas
        self.sky_image_raw = self.sky_image_raw.resize(
            (config.WIDTH, config.HEIGHT)
            )
        # get a polished image using the PIL library
        self.sky_image = ImageTk.PhotoImage(self.sky_image_raw)
        # create image as background
        self.sky_bg = self.canvas.create_image(0,0,image=self.sky_image,anchor="nw")
        self.canvas.tag_lower(self.sky_bg)
      
    def spawn_target(self):
        x = random.randint(0, config.WIDTH - 40)
        y = random.randint(-300, -50)

        # enable speed to be dependent on level ?
        speed = self.target_speed 
        
        target = Target(
            self.canvas,
            self.loader,
            x,
            y,
            speed=speed
        )

        self.targets.append(target)  
      
     
    def on_key_down(self, event):
        """
    Handle keyboard key-press events.

    Pressed keys are tracked in the active key set for use
    by the game loop. When the game is over, pressing 'R'
    restarts the game.

    Args:
        event (tk.Event):
            Tkinter keyboard event object.

    Side Effects:
        - Adds the pressed key to the active key set.
        - May restart the game.
    """
        self.keys.add(event.keysym)


    def on_key_up(self, event):
        
        """
    Handle keyboard key-release events.

    Removes released keys from the active key set to stop
    continuous actions such as movement.

    Args:
        event (tk.Event):
            Tkinter keyboard event object.

    Side Effects:
        - Removes the released key from the active key set.
    """
        self.keys.discard(event.keysym)
        if event.keysym in ("Left", "Right"):
            self.gun.aim_center()
            
    
    def game_loop(self):
        """
        Executes the main game loop
        The loop runs continuously by the time specified by
        the `config.FRAME_TIME`
        This is the central update scheduler of the game and handle state
        """
        
        # move bullets 
        
        # gun movement
        if "Left" in self.keys:
            self.gun.move_left()

        if "Right" in self.keys:
            self.gun.move_right()
        # move targets
        #play_sound("assets/sounds/start_game.mp3")
        if len(self.targets) < self.max_targets:
            self.spawn_target()
        for target in self.targets:
            state = target.update()

            if state == "escaped":
                target.reset()
                
        # check collisions

        self.root.after(30, self.game_loop)