# the main controller of the application goes here
import tkinter as tk 
import random
import config
from PIL import Image, ImageTk
from utils.image_loader import ImageLoader
from game.game_state import GameState
from game.target import Target
from game.bullet import Bullet
from game.score import Score
from game.game_state import GameState
from game.gun import Gun
from utils.audio import play_sound, mute_sound
from utils.collision import check_collision
from game.particle import Particle
import time

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
        self.sound_enabled = True
        self.score = Score(self.canvas)
        self.loader = ImageLoader()
        self.target_speed = config.TARGET_SPEED
        self.spawn_delay = 1200 # milliseconds
        self.last_spawn_time = 0
        self.max_targets = config.MAX_TARGETS
        self.lives = config.STARTING_LIVES
        self.level = config.START_LEVEL
        # set up an empty set of keys
        self.keys = set()
        # set default state of game
        self.state = GameState.MENU
        # display the level text
        self.level_text = self.canvas.create_text(
            200,
            20,
            text=f"Level: {self.level}",
            font=("Arial", 14,"bold"),
            fill="blue",
            tags="level_up"
        )
        # display the lives text
        self.lives_text = self.canvas.create_text(
            340,
            20,
            text=f"Lives: {self.lives}",
            font=("Arial", 14),
            fill="white"
        )
        # bind key actions to methods
        self.root.bind("<KeyPress>", self.on_key_down)
        self.root.bind("<KeyRelease>", self.on_key_up)
        # declare empty list for targets
        self.targets = []
        # declare empty list for bullets
        self.bullets = []
        self.particles = []  
        self.slow_motion = False
        self.slow_motion_end = 0
        # call the brain(manager) of the app
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
        
        if self.state == GameState.GAME_OVER and event.keysym.lower() == "r":
            self.start_game()
        elif event.keysym == "Escape":
            self.root.destroy()



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
            
    
    def shoot(self):
        """
        Fire a bullet from the player's gun.

        A shooting sound effect is played regardless of whether a bullet
        is created. If the gun's fire-rate cooldown has expired, a new
        Bullet object is created and added to the active bullet list.

        Side Effects:
            - Plays the gun-shot sound effect.
            - May create and store a new Bullet instance.
            - Updates the gun's internal firing cooldown.
        """
        bullet = self.gun.shoot()
        play_sound("assets/sounds/gun_shot.mp3")
        if bullet is not None:
            self.bullets.append(bullet)
        
    
    
    
    def maybe_spawn_target(self):
        """
        Spawn a target when spawning conditions are met.

        A new target is created only when:
            - The game is in the PLAYING state.
            - The maximum target limit has not been reached.
            - The configured spawn delay has elapsed.

        Side Effects:
            - May create a new Target object.
            - Updates the last target spawn timestamp.
        """
        if self.state != GameState.PLAYING:
            return
        now = time.time() * 1000

        if (
            len(self.targets) < self.max_targets and
            now - self.last_spawn_time > self.spawn_delay
        ):
            self.spawn_target()
            self.last_spawn_time = now
    
    
    def handle_escape(self, target):
        """
        Handle a target reaching the bottom of the screen.

        The player loses one life when a target escapes. If no lives
        remain, the game transitions to the GAME_OVER state. Otherwise,
        the escaped target is reset and returned to play.

        Args:
            target (Target):
                The target that escaped the play area.

        Side Effects:
            - Decrements the player's lives.
            - Updates the lives display.
            - Shows a life-loss warning message.
            - May change the game state to GAME_OVER.
            - May reset the target's position.
        """
        self.lives -= 1
        self.update_lives_ui()
        self.show_life_warning()

        if self.lives <= 0:
            self.state = GameState.GAME_OVER
            self.show_game_over()
            return

        target.reset()
      
      
    def update_lives_ui(self):
        """
        Update the lives display on the canvas.

        Synchronizes the lives text element with the current
        value of the player's remaining lives.

        Side Effects:
            - Updates the lives text displayed on the canvas.
        """
        self.canvas.itemconfig(
            self.lives_text,
            text=f"Lives: {self.lives}"
        )
        
    def show_life_warning(self):
        """
        Display a temporary life-loss warning message.

        A visual warning is shown when the player loses a life.
        The message is automatically removed after one second.

        Side Effects:
            - Creates a temporary text element on the canvas.
            - Schedules automatic removal of the warning message.
        """
        self.canvas.create_text(
            config.WIDTH // 2,
            80,
            text="-1 LIFE!",
            font=("Arial", 20, "bold"),
            fill="red",
            tags="life_warning"
        )

        self.root.after(
            1000,
            lambda: self.canvas.delete("life_warning")
        )
    
    def update_menu(self):
            """
        Update the main menu state.

        Displays the start screen prompt when the menu is first
        shown. Pressing the space bar starts a new game.

        Side Effects:
            - Creates menu UI elements.
            - May clear the canvas.
            - May transition the game into the PLAYING state.
        """
            if not hasattr(self, "menu_text"):
                self.canvas.delete("all")
                
                # Title
                self.canvas.create_text(
                    config.WIDTH // 2,
                    120,
                    text="SHOOTING GAME",
                    font=("Arial", 28, "bold"),
                    fill="darkgreen"
                )
                # start message
                self.menu_text = self.canvas.create_text(
                    config.WIDTH // 2,
                    #config.HEIGHT // 2,
                    200,
                    text="PRESS SPACE TO START",
                    font=("Arial", 24),
                    fill="darkgreen"
                )
                
               
            self.canvas.create_rectangle(
                150,
                250,
                550,
                470,
                fill="white",
                outline="darkgreen",
                width=3
            )
            self.canvas.create_text(
                config.WIDTH // 2,
                360,
                text=(
                    "HOW TO PLAY\n\n"
                    "← Move Left\n"
                    "→ Move Right\n"
                    "SPACE = Shoot\n\n"
                    "Hit targets to earn points.\n"
                    "Every 5 points advances a level.\n"
                    "Don't let targets reach the bottom.\n"
                    "You have 5 lives."
                ),
                font=("Arial", 14),
                fill="darkgreen",
                justify="center"
            )
            # space key starts game a fresh
            if "space" in self.keys:
                self.canvas.delete("all")
                self.start_game()
                self.keys.discard("space")
      
      
    def start_game(self):
        """
        Start a new game session.

        Resets game progress, score, lives, difficulty settings,
        active entities, and user interface elements. A new gun
        is created and an initial set of targets is spawned.

        Side Effects:
            - Sets the game state to PLAYING.
            - Resets score, level, and lives.
            - Clears and rebuilds the game UI.
            - Recreates the player's gun.
            - Removes existing bullets and targets.
            - Spawns the initial wave of targets.
        """
        
        self.state = GameState.PLAYING
        self.lives = 5
        self.level = 1
        if self.sound_enabled:
            play_sound("assets/sounds/start_game.mp3")
        else:
           mute_sound() 
       
        self.score.reset()
        
        self.canvas.delete("all")
       
        self.create_background()
        self.score.rebuild()    
        self.level_text = self.canvas.create_text(
            200, 20,
            text=f"Level: {self.level}",
            font=("Arial", 14, "bold"),
            fill="blue"
        )

        self.lives_text = self.canvas.create_text(
            340, 20,
            text=f"Lives: {self.lives}",
            font=("Arial", 14),
            fill="black"
        )

        # recreate gun
        #loader = ImageLoader()
        self.gun = Gun(self.canvas, self.loader, 350, 550)

        # spawn initial targets
        for _ in range(5):
            self.spawn_target()
      
    def update_game(self):
        """
        Update all gameplay systems for a single frame.

        This method is executed repeatedly by the main game loop
        while the game is in the PLAYING state.

        Responsibilities include:
            - Processing player input.
            - Updating gun movement.
            - Handling shooting actions.
            - Updating bullets and targets.
            - Managing slow-motion effects.
            - Detecting target escapes.
            - Performing collision detection.
            - Updating score and level progression.
            - Spawning new targets when required.

        Side Effects:
            - Modifies positions of game objects.
            - Creates and removes bullets and targets.
            - Updates score, lives, and level state.
            - May trigger game-over conditions.
            - May increase game difficulty.
        """
    
    
        if self.state != GameState.PLAYING:
            self.sound_enabled = False
            mute_sound()
            return
        # slow motion handling, keeps it inactive unless level changes
        if self.slow_motion and time.time() > self.slow_motion_end:
            self.slow_motion = False
        # movement
        if "Left" in self.keys:
            self.gun.move_left()

        if "Right" in self.keys:
            self.gun.move_right()
       

        # shooting
        if "space" in self.keys:
            self.shoot()
            self.keys.discard("space")

        # bullets
        for bullet in self.bullets:
            if self.slow_motion:
                bullet.speed = 4
            else:
                bullet.speed = 12
            bullet.update()
        self.bullets = [b for b in self.bullets if b.active]

        # targets
        for target in self.targets:
            state = target.update(self.slow_motion)

            if state == "escaped":
                self.handle_escape(target)

        # collisions
        for bullet in self.bullets:
            for target in self.targets:

                if not bullet.active or not target.active:
                    continue

                if check_collision(bullet.get_bbox(), target.get_bbox()):
                    bx1, by1, bx2, by2 = bullet.get_bbox()
                    cx = (bx1 + bx2) / 2
                    cy = (by1 + by2) / 2
                    bullet.destroy()
                    target.reset()
                    
                    for _ in range(12):
                        self.particles.append(Particle(self.canvas, cx, cy))

                    
                    self.score.add(1)
                    # add sound effect for score = 10
                    if self.score.value == 10:
                        play_sound("assets/sounds/doing_great.mp3")
                    self.update_level()
                   
                    
        
        self.particles = [p for p in self.particles if p.update()]
                    
        self.maybe_spawn_target()  
        
    
    def show_game_over(self):
        """
        Display the game-over screen.

        Clears the current game view and displays a game-over message
        along with restart instructions. All active targets and bullets
        are removed, and a short delay is applied before restarting
        becomes available.

        Side Effects:
            - Clears all canvas items.
            - Rebuilds the score display.
            - Displays game-over UI elements.
            - Removes all active targets and bullets.
            - Temporarily disables restarting.
            - Schedules restart availability after a delay.
        """
        self.sound_enabled = False
        mute_sound()
        self.canvas.delete("all")
        self.score.rebuild()
        self.canvas.create_text(
            config.WIDTH // 2,
            config.HEIGHT // 2 - 40,
            text="GAME OVER",
            font=("Arial", 30),
            fill="red"
        )
        
        self.canvas.create_text(
            config.WIDTH // 2,
            config.HEIGHT // 2,
            text=f"Final Score: {self.score.value}",
            font=("Arial", 20, "bold"),
            fill="blue"
        )
        
        self.canvas.create_text(
            config.WIDTH // 2,
            config.HEIGHT // 2+40,
            text=f"Highest Level: {self.level}",
            font=("Arial",20,"bold"),
            fill="blue"
        )
        
        self.canvas.create_text(
            config.WIDTH // 2,
            config.HEIGHT // 2 + 70,
            text="Press R to restart",
            font=("Arial", 16),
            fill="Black"
        )
        
        self.canvas.create_text(
            config.WIDTH // 2,
            config.HEIGHT // 2 + 100,
            text="Press ESC to quit",
            font=("Arial", 16,"bold"),
            fill="Black"
        )
        self.targets.clear()
        self.bullets.clear()
        self.restart_allowed = False
        self.root.after(500, lambda: setattr(self, "restart_allowed", True))
     
    def update_game_over(self):
        """
        Update the game-over state.

        Gameplay is paused while the game is in the GAME_OVER state.
        Input handling for restarting the game is managed separately
        through keyboard event handlers.

        Side Effects:
            None.
        """
        # game is paused here; we only listen for restart input
        pass
     
     
    def increase_difficulty(self):
        """
        Increase the game's difficulty.

        Called when the player advances to a new level. Difficulty is
        increased by allowing more simultaneous targets and reducing
        the delay between target spawns.

        The spawn delay is capped at a minimum value to prevent
        targets from spawning excessively fast.

        Side Effects:
            - Increases the maximum number of active targets.
            - Reduces the target spawn delay.
        """
    
        self.max_targets += 1

        # faster spawn rate
        self.spawn_delay = max(400, self.spawn_delay - 100)
        #self.spawn_target()
     
    def update_level(self):
        """
        Check for level progression and apply level-up effects.

        The player's level increases every five points scored. When a
        new level is reached, the level display is updated, a temporary
        level-complete message is shown, slow-motion mode is activated,
        and the game's difficulty is increased.

        Side Effects:
            - Updates the current level.
            - Updates the level UI display.
            - Displays a temporary level-complete message.
            - Enables slow-motion mode.
            - Increases game difficulty.
        """
    
        #new_level = (self.score // 5) + 1
        new_level = (self.score.value // config.LEVEL_SCORE) + 1
        # to debug the level variable
        #print(f"Score={self.score}, New Level={new_level}")
        if new_level > self.level:
            self.level = new_level

            self.canvas.itemconfig(
                self.level_text,
                text=f"Level: {self.level}"
            )
    
            
            self.canvas.create_text(
            config.WIDTH // 2,
            config.HEIGHT // 2,
            text="LEVEL COMPLETE!",
            font=("Arial", 28, "bold"),
            fill="green",
            tags="level_complete"
        )

        self.root.after(
            1000,
            lambda: self.canvas.delete("level_complete")
        )

        # SLOW MOTION START
        self.slow_motion = True
        self.slow_motion_end = time.time() + 1  # 1 second

        self.increase_difficulty()
     
    def game_loop(self):
        """
        Executes the main game loop
        The loop runs continuously by the time specified by
        the `config.FRAME_TIME`
        This is the central update scheduler of the game and handle state
        """
        
        if self.state == GameState.MENU:
            self.update_menu()

        elif self.state == GameState.PLAYING:
            self.update_game()

        elif self.state == GameState.GAME_OVER:
            self.sound_enabled = False
            self.update_game_over()
        # Schedule the next frame.
       
        self.root.after(config.FRAME_TIME, self.game_loop)