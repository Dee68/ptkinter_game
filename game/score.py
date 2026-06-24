# the score management goes here

import tkinter as tk


class Score:
    """
    Manages and displays the player's score on a Tkinter canvas.

    Responsibilities:
    - Creating and rendering the score text.
    - Updating score values.
    - Resetting and rebuilding the display.
    - Synchronizing internal score state with canvas text.
    """
    
    def __init__(self, canvas: tk.Canvas, x=60, y=20):
        """
        Initialize the Score display.

        Args:
            canvas (tk.Canvas):
                Canvas where the score text will be rendered.

            x (int, optional):
                X-coordinate of the score display. Defaults to 60.

            y (int, optional):
                Y-coordinate of the score display. Defaults to 20.
        """
        
        self.canvas = canvas
        self.x = x
        self.y = y
        self.value = 0
        self.text_id = None
        self.create()

    def create(self):
        """
        Create the score text element on the canvas.

        Side Effects:
            - Creates a new text item on the canvas.
            - Stores its ID in `self.text_id`.
        """
        
        self.text_id = self.canvas.create_text(
            self.x, self.y,
            text="Score: 0",
            font=("Arial", 14),
            fill="black"
        )

    def add(self, points=1):
        """
        Increase the score by a given number of points.

        Args:
            points (int, optional):
                Number of points to add. Defaults to 1.

        Side Effects:
            - Updates internal score value.
            - Refreshes displayed score on the canvas.
        """
        self.value += points
        self.update()

    def reset(self):
        """
        Reset the score back to zero.

        Side Effects:
            - Sets score value to 0.
            - Updates displayed score.
        """
        self.value = 0
        self.update()

    def destroy(self):
        """
        Remove the score display from the canvas.

        Side Effects:
            - Deletes the canvas text item if it exists.
        """
        if self.text_id:
            self.canvas.delete(self.text_id)

    def rebuild(self):
        """
        Recreate the score display after it has been destroyed.

        This is useful when resetting the UI or restarting the game.

        Side Effects:
            - Recreates the canvas text item.
            - Updates display to current score value.
        """
        
        self.create()
        self.update()

    def update(self):
        """
        Refresh the displayed score text to match internal value.

        Side Effects:
            - Updates the canvas text item with current score.
        """
        self.canvas.itemconfig(
            self.text_id,
            text=f"Score: {self.value}"
        )