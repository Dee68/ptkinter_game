# the bullet object and it's properties and methods goes here
import tkinter as tk 
import math

class Bullet:
    """
    Represents a projectile fired by the player's gun.

    The Bullet handles:
    - Rendering itself on the canvas.
    - Moving upward each frame.
    - Removing itself when it leaves the screen.
    - Providing collision boundaries.
    - Tracking whether it is active.
    """
    def __init__(self, canvas: tk.Tk, x: int, y: int, angle=90, speed: int = 12):
        """
        Initialize a Bullet object.

        Args:
            canvas (tk.Canvas):
                Canvas where the bullet will be drawn.

            x (float):
                Initial x-coordinate of the bullet's center.

            y (float):
                Initial y-coordinate of the bullet.

            speed (int, optional):
                Number of pixels the bullet moves upward
                each update cycle. Defaults to 12.
        """
        
        self.canvas = canvas
        self.speed = speed
        self.angle = angle
        
        radians = math.radians(angle)
        
        self.dx = speed*math.cos(radians)
        self.dy = -speed*math.sin(radians)
        
        self.width = 6
        self.height = 10
        
        # visual to show bullet
        self.id = self.canvas.create_rectangle(
            x - self.width / 2,
            y - self.height,
            x + self.width / 2,
            y,
            fill="yellow",
            outline=""
        )

        self.active = True
        
    
    # ---------------- movement ----------------
    def update(self):
        """
        Update the bullet's position.

        The bullet moves upward by its speed value.
        If the bullet leaves the visible canvas area,
        it is automatically destroyed.

        Returns:
            None

        Side Effects:
            - Updates the bullet's position.
            - May destroy the bullet if it moves off-screen.
        """
        
        if not self.active:
            return
        # moves the bullet by dx=0, dy= -speed
        #self.canvas.move(self.id, 0, -self.speed)
        self.canvas.move(self.id,self.dx,self.dy)
        # gets the bullet coordinates
        x1, y1, x2, y2 = self.canvas.coords(self.id)

        # off-screen cleanup
        if y2 < 0:
            self.destroy()

    # ---------------- lifecycle ----------------
    def destroy(self):
        """
        Remove the bullet from the canvas.

        The bullet is deleted only if it is currently active.
        After destruction, the bullet can no longer be updated
        or used for collision detection.

        Side Effects:
            - Deletes the canvas object.
            - Sets active to False.
        """
        
        if self.active:
            self.canvas.delete(self.id)
            self.active = False

    # ---------------- collision helpers ----------------
   
    def get_bbox(self):
        """
        Get the bullet's bounding box coordinates.

        The bounding box is typically used for collision
        detection against targets or other game objects.

        Returns:
            list[float]:
                Bounding box coordinates in the format
                [x1, y1, x2, y2].

            list:
                An empty list if the bullet is inactive
                or the canvas item no longer exists.
        """
        
        if not self.active:
            return []

        coords = self.canvas.coords(self.id)

        if len(coords) != 4:
            return []

        return coords

        
    