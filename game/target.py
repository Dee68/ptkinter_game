# the target can be any object of shape, it's properties and method s goes here
import tkinter as tk 
import random

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
        self.image = self.image_loader.load(random.choice(plane_images))
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
            image=self.image,
            anchor="center"
        )
        
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