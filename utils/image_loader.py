from PIL import Image, ImageTk
from pathlib import Path



class ImageLoader:
    def __init__(self):
        self.base = Path(__file__).resolve().parent.parent
        self.img_dir = self.base / "assets" / "images"

    def load(self, filename, size=(60, 60)):
        path = self.img_dir / filename
        # print("Loading:", path)
        # print("Exists:", path.exists())
        # img = Image.open("assets/images/gun_right.png")
        # img.show()
        image = Image.open(path).convert("RGBA").resize(size)
        return ImageTk.PhotoImage(image)