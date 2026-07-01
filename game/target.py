# the target can be any object of shape, it's properties and method s goes here
import tkinter as tk 
import random
import math
from PIL import Image

plane_images = ["hell.png", "hell1.png", "hell2.png"]

class Target:
    """
    Represents a falling target in the game.

    The Target handles:
    - Rendering itself on the canvas.
    - Moving downward over time.
    - Detecting when it leaves the screen.
    - Respawning at a random location.
    - Providing collision boundaries.
    - Managing its active state.
    """
    def __init__(self, canvas:tk.Canvas, image_loader, x:int, y:int, speed: int =4):
        self.canvas = canvas
        self.image_loader = image_loader
        self.speed = speed
        self.active = True

        self.width = 30
        self.height = 30
        self.rotor_angle = 0
        self.body_angle = 0 #
        #self.image = self.image_loader.load(random.choice(plane_images))
        # self.body_image = self.image_loader.load_pil(
        #     "hell_body.png"
        # )

        # self.rotor_image = self.image_loader.load_pil(
        #     "rotor2.png"
        # )
        
        self.body_images = [
            self.image_loader.load_pil("hell_body_0.png"),
            self.image_loader.load_pil("hell_body_1.png"),
            self.image_loader.load_pil("hell_body_2.png"),
        ]

        self.rotor_images = [
            self.image_loader.load_pil("rotor_0.png"),
            self.image_loader.load_pil("rotor_1.png"),
            self.image_loader.load_pil("rotor_2.png"),
        ]
        
        self.body_image = random.choice(self.body_images)
        self.rotor_image = random.choice(self.rotor_images)
        self.tk_image = self.build_image()
        
        self.tilt_phase = random.random() * math.pi * 2 # controls oscillation over time
        
        # self.id = self.canvas.create_oval(
        #     x,
        #     y,
        #     x + self.width,
        #     y + self.height,
        #     fill="red",
        #     outline=""
        # )
        
        self.id = self.canvas.create_image(
            x,
            y,
            #image=self.image,
            image=self.tk_image,
            anchor="center"
        )
        
    # helper method
    def build_image(self):

        #helicopter = self.body_image.copy() # copy original image
        # rotates body of helicopter
        helicopter = self.body_image.rotate(
            self.body_angle,
            expand=True
        )
        # rotates the rotor/blade
        rotated_rotor = self.rotor_image.rotate(
            self.rotor_angle,
            expand=True
        )
        # generate a dynamic scaling factor to oscillate between -1 and 1
        scale = abs(math.cos(math.radians(self.rotor_angle))) # abs enables the value bwt 0 and 1
        scale = max(0.2, scale) # ensures that the min value can not be < 0.2(20%)
        # Adjust rotor height based on the scale value
        new_height = int(rotated_rotor.height * scale) # width remains unchanged causing animation effect like squash/stretch
        # resize rotor image and reduce aliasing artifacts/ quality downsampling filter
        rotated_rotor = rotated_rotor.resize(
            (
                rotated_rotor.width,
                new_height
            ),
            Image.Resampling.LANCZOS
        )
        # Paste rotor approximately over the mast.
        # helicopter.paste(
        #     rotated_rotor,
        #     (10, 0),
        #     rotated_rotor
        # )
        rotor_x = (helicopter.width - rotated_rotor.width) // 2
        rotor_y = 0

        helicopter.paste(
            rotated_rotor,
            (rotor_x, rotor_y),
            rotated_rotor
        )

        return self.image_loader.from_pil(helicopter)
        
    #-----movement -----------
    def update(self, slow_motion=False):
        """
        Update the target's position.

        The target moves downward by its speed value each frame.
        If slow motion is enabled, movement speed is reduced
        to 40% of its normal value.

        The method also checks whether the target has left
        the bottom of the canvas.

        Args:
            slow_motion (bool, optional):
                Whether slow-motion mode is active.
                Defaults to False.

        Returns:
            str:
                One of the following states:

                - "alive":
                  Target is still active and on screen.

                - "escaped":
                  Target has moved beyond the bottom
                  edge of the canvas.

                - "dead":
                  Target no longer exists on the canvas.
                  This acts as a safety guard when the
                  target has already been destroyed.
        """
        bbox = self.canvas.bbox(self.id)

        if not bbox:
            return "dead"   # safety guard

        speed = self.speed * (0.4 if slow_motion else 1)
      
        self.rotor_angle = (self.rotor_angle + 25) % 360
        self.tilt_phase += 0.05
        self.body_angle = 8 * math.sin(self.tilt_phase)
        self.tk_image = self.build_image()
        self.canvas.itemconfig(self.id, image=self.tk_image)
        self.canvas.move(self.id, 0, speed)
        
        x1, y1, x2, y2 = self.get_bbox()

        if y2 >= self.canvas.winfo_height():
            return "escaped"

        return "alive"

    # ---------------- respawn logic ----------------
    def reset(self):
        """
        Respawn the target at a random position above the canvas.

        The target is marked as active and moved to a new
        random horizontal position. The vertical position is
        chosen above the visible area so the target appears
        to fall into view naturally.

        Side Effects:
            - Sets active state to True.
            - Updates the target's canvas coordinates.
        """
        self.active = True
        x = random.randint(0, self.canvas.winfo_width() - self.width)
        y = random.randint(-300, -40)

        self.canvas.coords(
            self.id,
            x,
            y
            #x + self.width,
            #y + self.height
        )

    # ---------------- lifecycle ----------------
    def destroy(self):
        """
        Remove the target from the canvas.

        Once destroyed, the target is no longer visible
        and its active state is set to False.

        Side Effects:
            - Deletes the canvas object.
            - Marks the target as inactive.
        """
        self.canvas.delete(self.id)
        self.active = False

    # ---------------- collision helpers ----------------
    def get_bbox(self):
        """
        Get the target's bounding box coordinates.

        The bounding box can be used for collision detection
        against bullets, players, or other game objects.

        Returns:
            list[float]:
                Bounding box coordinates in the format:

                [x1, y1, x2, y2]

                where:
                - x1, y1 = top-left corner
                - x2, y2 = bottom-right corner
        """
        return self.canvas.bbox(self.id)