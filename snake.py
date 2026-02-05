

import tkinter as tk
import random
import os

HIGH_SCORE_FILE = "snake_highscore.txt"

class SnakeGame(tk.Tk):
    def __init__(self, cell_size=20, cols=30, rows=20, initial_speed=120):
        super().__init__()
        self.title("Snake — Friendly GUI")
        self.resizable(False, False)

     
        self.cell_size = cell_size
        self.cols = cols
        self.rows = rows
        self.width = cols * cell_size
        self.height = rows * cell_size
        self.speed = initial_speed  

      
        self.direction = "Right"
        self.next_direction = self.direction
        self.snake = []
        self.food = None
        self.running = False
        self.paused = False
        self.score = 0
        self.high_score = self.load_high_score()

       
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bg="#0c1021", highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        self.score_var = tk.StringVar(value=f"Score: {self.score}")
        self.high_var = tk.StringVar(value=f"High: {self.high_score}")
        self.status_var = tk.StringVar(value="Press ▶ Start")

        tk.Label(self, textvariable=self.score_var, font=("Helvetica", 12)).grid(row=1, column=0, sticky="w", padx=10)
        tk.Label(self, textvariable=self.high_var, font=("Helvetica", 12)).grid(row=1, column=1, sticky="w")
        tk.Label(self, textvariable=self.status_var, font=("Helvetica", 12)).grid(row=1, column=2, columnspan=2, sticky="e", padx=10)

        self.start_button = tk.Button(self, text="▶ Start", width=10, command=self.start_game)
        self.start_button.grid(row=2, column=0, pady=(6, 10), padx=6)

        self.pause_button = tk.Button(self, text="⏸ Pause", width=10, command=self.toggle_pause, state="disabled")
        self.pause_button.grid(row=2, column=1, pady=(6, 10), padx=6)

        self.restart_button = tk.Button(self, text="↺ Restart", width=10, command=self.restart_game, state="disabled")
        self.restart_button.grid(row=2, column=2, pady=(6, 10), padx=6)

        tk.Label(self, text="Speed:", font=("Helvetica", 10)).grid(row=3, column=0, sticky="w", padx=10)
        self.speed_slider = tk.Scale(self, from_=40, to=250, orient="horizontal", command=self.change_speed, length=200)
        self.speed_slider.set(self.speed)
        self.speed_slider.grid(row=3, column=1, columnspan=2, pady=(0,10))

        tk.Label(self, text="Controls: Arrows or WASD", font=("Helvetica", 9, "italic")).grid(row=4, column=0, columnspan=4, pady=(0,10))

        
        self.bind_all("<Key>", self.on_key_press)

        
        self.draw_grid_lines()

    
    def load_high_score(self):
        if os.path.exists(HIGH_SCORE_FILE):
            try:
                with open(HIGH_SCORE_FILE, "r") as f:
                    return int(f.read().strip() or 0)
            except Exception:
                return 0
        return 0

    def save_high_score(self):
        try:
            with open(HIGH_SCORE_FILE, "w") as f:
                f.write(str(self.high_score))
        except Exception:
            pass

    
    def draw_grid_lines(self):
        
        for c in range(0, self.width, self.cell_size):
            self.canvas.create_line(c, 0, c, self.height, fill="#0f1626")
        for r in range(0, self.height, self.cell_size):
            self.canvas.create_line(0, r, self.width, r, fill="#0f1626")

    def cell_to_xy(self, cell):
        """Convert (col,row) to canvas coords of rectangle corners"""
        c, r = cell
        x1 = c * self.cell_size
        y1 = r * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size
        return x1, y1, x2, y2

    def draw_cell(self, cell, fill="#4ee39b", outline=""):
        x1, y1, x2, y2 = self.cell_to_xy(cell)
        return self.canvas.create_rectangle(x1+1, y1+1, x2-1, y2-1, fill=fill, outline=outline)

    def start_game(self):
        if self.running:
            return
        self.running = True
        self.paused = False
        self.start_button.config(state="disabled")
        self.pause_button.config(state="normal")
        self.restart_button.config(state="normal")
        self.status_var.set("Playing")
        self.reset_state()
        self.game_loop()

    def reset_state(self):
        
        mid_c = self.cols // 2
        mid_r = self.rows // 2
        self.snake = [(mid_c - 1, mid_r), (mid_c, mid_r), (mid_c + 1, mid_r)]  # head is last
        self.direction = "Right"
        self.next_direction = self.direction
        self.score = 0
        self.update_score_labels()
        self.canvas.delete("snake")
        self.canvas.delete("food")
        self.spawn_food()

    def restart_game(self):
        self.running = True
        self.paused = False
        self.status_var.set("Playing")
        self.reset_state()
        self.game_loop()

    def toggle_pause(self):
        if not self.running:
            return
        self.paused = not self.paused
        if self.paused:
            self.status_var.set("Paused")
            self.pause_button.config(text="▶ Resume")
        else:
            self.status_var.set("Playing")
            self.pause_button.config(text="⏸ Pause")
            self.game_loop()

    def game_over(self):
        self.running = False
        self.paused = False
        self.status_var.set("Game Over! Press Restart.")
        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled", text="⏸ Pause")
        if self.score > self.high_score:
            self.high_score = self.score
            self.high_var.set(f"High: {self.high_score}")
            self.save_high_score()

    
    def on_key_press(self, event):
        k = event.keysym.lower()
        mapping = {
            "up": "Up", "w": "Up",
            "down": "Down", "s": "Down",
            "left": "Left", "a": "Left",
            "right": "Right", "d": "Right",
            "space": "toggle_pause",
            "p": "toggle_pause",
            "r": "restart"
        }
        action = mapping.get(k)
        if action in ("Up","Down","Left","Right"):
            self.set_direction(action)
        elif action == "toggle_pause":
            self.toggle_pause()
        elif action == "restart":
            self.restart_game()

    def set_direction(self, new_dir):
        
        opposites = {"Up":"Down","Down":"Up","Left":"Right","Right":"Left"}
        if opposites.get(new_dir) == self.direction:
            return
        self.next_direction = new_dir

    def change_speed(self, val):
        try:
            v = int(val)
            self.speed = v
        except:
            pass

    
    def spawn_food(self):
        empty_cells = {(c, r) for c in range(self.cols) for r in range(self.rows)} - set(self.snake)
        if not empty_cells:
          
            self.status_var.set("You Win! Full board.")
            self.running = False
            return
        self.food = random.choice(list(empty_cells))
        self.canvas.delete("food")
        self.draw_cell(self.food, fill="#ff7b7b")
        self.canvas.addtag_withtag("food", "current")

   
    def draw_snake(self):
        self.canvas.delete("snake")
        
        for idx, cell in enumerate(self.snake):
            if idx == len(self.snake) - 1:
                # head
                self.draw_cell(cell, fill="#e3f9ff")
            else:
                self.draw_cell(cell, fill="#50c6a0")
        
        for item in self.canvas.find_all():
            self.canvas.addtag_withtag("snake", item)

    
    def step(self):
       
        self.direction = self.next_direction

        head = self.snake[-1]
        c, r = head
        if self.direction == "Up":
            r -= 1
        elif self.direction == "Down":
            r += 1
        elif self.direction == "Left":
            c -= 1
        elif self.direction == "Right":
            c += 1

        new_head = (c, r)

       
        if not (0 <= c < self.cols and 0 <= r < self.rows):
            self.game_over()
            return

       
        if new_head in self.snake:
            self.game_over()
            return

        
        self.snake.append(new_head)

       
        if self.food and new_head == self.food:
            self.score += 10
            self.update_score_labels()
            self.spawn_food()
        else:
           
            self.snake.pop(0)

        self.draw_snake()

    def update_score_labels(self):
        self.score_var.set(f"Score: {self.score}")
        self.high_var.set(f"High: {self.high_score}")

    def game_loop(self):
        if not self.running or self.paused:
            return
        self.step()
        if self.running:
            
            self.after(self.speed, self.game_loop)

if __name__ == "__main__":
    game = SnakeGame(cell_size=22, cols=30, rows=20, initial_speed=120)
    game.mainloop()
