from game.app import GameApp
import tkinter as tk 


def main():
    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()
    

if __name__ == "__main__":
    main()