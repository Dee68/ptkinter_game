import random
import tkinter as tk


class Particle:
    def __init__(self, canvas: tk.Canvas, x, y):
        self.canvas = canvas

        self.dx = random.uniform(-3, 3)
        self.dy = random.uniform(-3, 3)

        self.life = 40  # frames
        self.id = self.canvas.create_oval(
            x, y, x + 6, y + 6,
            fill="orange",
            outline=""
        )
        self.canvas.tag_raise(self.id)

    def update(self):
        if self.life <= 0:
            self.canvas.delete(self.id)
            return False

        self.canvas.move(self.id, self.dx, self.dy)

        self.dy += 0.15  # gravity effect
        self.life -= 1

        return True