# the gun object and it's properties and methods goes here

import tkinter as tk
import time

# ANGLE_MAP = {
#     "left": 120,
#     "center": 90,
#     "right": 60,
# }

class Gun:
    """
    Represents the player's gun in the game.

    The Gun handles:
    - Loading and displaying gun images.
    - Horizontal movement across the canvas.
    - Direction changes (left, right, center).
    - Creating bullets when firing.
    - Enforcing a fire-rate cooldown.
    """
    
    def __init__(self, canvas: tk.Canvas, image_loader, x: int, y: int):
        """
        Initialize a Gun object.

        Args:
            canvas (tk.Canvas):
                Canvas where the gun will be drawn.

            image_loader:
                Object responsible for loading image assets.

            x (int):
                Initial x-coordinate of the gun.

            y (int):
                Initial y-coordinate of the gun.
        """
        self.canvas = canvas
        self.image_loader = image_loader

        self.speed = 10
       

        # load images once
        self.images = {
            "left": self.image_loader.load("gun_left.png"),
            "center": self.image_loader.load("gun_center.png"),
            "right": self.image_loader.load("gun_right.png"),
        }
        self.width = 64
        self.height = 64

        self.direction = "center"
        self.current_image = self.images[self.direction]

        self.id = self.canvas.create_image(
            x,
            y,
            image=self.images[self.direction],
            anchor="center"
        )

    # ---------------- movement ----------------
   
    def move_left(self):
        """
        Move the gun to the left.

        The gun moves by the value stored in `self.speed`.
        Movement is restricted so the gun cannot move
        outside the left boundary of the canvas.
        """
        x, y = self.canvas.coords(self.id)

        if x - self.width / 2 > 0:
            self.canvas.move(self.id, -self.speed, 0)
            self.set_direction("left")
   
    def move_right(self):
        """
        Move the gun to the right.

        The gun moves by the value stored in `self.speed`.
        Movement is restricted so the gun cannot move
        outside the right boundary of the canvas.
        """
        x, y = self.canvas.coords(self.id)

        canvas_width = self.canvas.winfo_width()

        if x + self.width / 2 < canvas_width:
            self.canvas.move(self.id, self.speed, 0)
            self.set_direction("right")

    def aim_center(self):
        """
        Reset the gun sprite to its neutral (center) position.

        This is typically called when the player is no longer
        pressing a movement key.
        
        Side Effects:
            Updates the displayed gun image.
        """
        self.set_direction("center")

    # ---------------- direction handling ----------------
    def set_direction(self, direction: str):
        """
        Change the gun's facing direction and sprite.

        Args:
            direction (str):
                Direction key corresponding to an image.
                Expected values:
                - 'left'
                - 'center'
                - 'right'

        Side Effects:
            - Updates the current direction.
            - Changes the displayed image on the canvas.
        """
        self.direction = direction
        self.current_image = self.images[direction]
        self.canvas.itemconfig(self.id, image=self.images[direction])

    # ---------------- helpers ----------------
    def get_position(self):
        """
        Get the current position of the gun on the canvas.

        Returns:
            list[float]:
                The canvas coordinates in the format [x, y].
        """
        return self.canvas.coords(self.id)

    def get_center(self):
        """
        Get the center coordinates of the gun.

        Since the image is anchored at its center, this returns
        the exact position used for rendering and bullet spawning.

        Returns:
            tuple[float, float]:
                The x and y coordinates of the gun's center.
        """
        x, y = self.canvas.coords(self.id)
        return x, y
    
    #---------shooting--------------------
    
    def shoot(self):
        pass
       
    