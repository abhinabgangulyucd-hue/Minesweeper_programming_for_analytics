import random
import time
from datetime import datetime
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy.ndimage import label
from scipy.ndimage import gaussian_filter
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog

EASY = {'rows': 9, 'cols': 9, 'mines': 10}
INTERMEDIATE = {'rows': 16, 'cols': 16, 'mines': 40}
EXPERT = {'rows': 16, 'cols': 30, 'mines': 99}
SCORE_FILE = 'highscores.txt'
#BOARD_FILE = "grid_matrix.txt"
BOARD_FILE_CSV = "grid_matrix.csv" #board answer

# adaptive Tile Sizing
MAX_TILE_SIZE = 32        # normal size
MIN_TILE_SIZE = 14        # smallest readable tile size


class Board:
    """The game board mainly of 3 elements of the mines, mine count, flags and the reveal count"""
    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.mine_grid = make_empty_grid(rows, cols, False)  # Turned to true if it's a mine
        self.number_grid = make_empty_grid(rows, cols, 0)  # how many mines are around count
        self.revealed = make_empty_grid(rows, cols, False)  # cells revealed to and by a player
        self.flagged = make_empty_grid(rows, cols, False)  # cells flagged by player
        self.game_over = False
        self.won = False

    def place_mines(self, safe_row, safe_col):
        """to place the mines after first click (ensures a safe-click first criteria)"""
        placed = 0
        while placed < self.mines:
            row = random.randint(0, self.rows - 1)  # to ensure boundary is not crossed as maximum allowed value is max row and column
            col = random.randint(0, self.cols - 1)
            flag_proceed_mine = 1
            if row == safe_row and col == safe_col:  # dont place mine in first clicked cell
                flag_proceed_mine = 0
            elif self.mine_grid[row][col]:  # don't place mine where mine already exists
                flag_proceed_mine = 0
            if flag_proceed_mine:  # check above conditions, and if flag is 1 (above conditions are not true), place mine
                self.mine_grid[row][col] = True
                placed += 1
        """Depricated
        with open(BOARD_FILE, "w") as file:
            file.write('') #write the txt file with nothing, just to clear it then append with boards"""
        with open(BOARD_FILE_CSV, "w") as file_csv:
            writer = csv.writer(file_csv) #write the csv file with nothing, just to clear it then append with boards
        self.calculate_numbers()  


    def calculate_numbers(self):
        """count number of mines next to a cell"""
        for row in range(self.rows):
            for col in range(self.cols):
                if not self.mine_grid[row][col]: #a number cell isn't a mine cell, search for adjacent mines
                    count = 0
                    # below dynamic allows us to check for left, right, top, bottom and diagonal mines since all are at a max distance of 1
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:                            
                            if not (dr == 0 and dc == 0): #doesn't count the cell in reference (0,0 coordinate)
                                r = row + dr
                                c = col + dc
                                # Check if they are not the first or lsat elements before checking neighbours
                                if (r >= 0) and (r < self.rows) and (c >= 0) and (c < self.cols):
                                    if self.mine_grid[r][c]:
                                        count += 1
                    self.number_grid[row][col] = count
                    #by this point, board has been created. execute code to export board(s) to txt file
                else: #a mine cell
                    count = "M"
                    self.number_grid[row][col] = count #add the count to mine as 'M'
        
        self.reveal_board()

    def reveal_board(self):        
        """Depricated
        with open(BOARD_FILE, "a") as file: #use "a" type because of the analytics part
            file.write("Output:\n")
            for row in range(self.rows):
                row_cells = []
                for col in range(self.cols):                    
                    row_cells.append(str(self.number_grid[row][col]))                                    
                file.write(" ".join(row_cells) + '\n') #export board answer to txt file"""
        with open(BOARD_FILE_CSV, "a", newline="") as file_csv: #use "a" type because of the analytics part
            writer = csv.writer(file_csv)
            writer.writerow(["Output:"])  #Optional header row
            for row in range(self.rows):
                writer.writerow([self.number_grid[row][col] for col in range(self.cols)])                      

                

    #keeping below reveal_cell function commented if problems are identified with the flooding logic
    '''def reveal_cell(self, row, col):  #to reveal a cell/block
        if self.revealed[row][col]:  # dont do anything if its already revealed (return and abort from function)
            return
        if self.flagged[row][col]: #dont do anything if it is already flagged (return and abort from function)
            return
        self.revealed[row][col] = True  #otherwise set reveal of function to True
        if self.mine_grid[row][col]: 
            self.game_over = True   #check if revealed is same column as a mine and if so set game_over flag to True
            return
        self.check_win()   #otherwise see if user has won'''
    
   
    def reveal_cell(self, row, col):
        """reveals content of the cell if appropriate"""
        # Do nothing if already revealed or flagged
        if self.revealed[row][col] or self.flagged[row][col]:
            return
        # If this is a mine, reveal it and end the game
        if self.mine_grid[row][col]:
            self.revealed[row][col] = True
            self.game_over = True
            return
        cells = [(row, col)]
        i = 0
        while i < len(cells):
            r, c = cells[i]
            i += 1
            # Process only safe, unrevealed, unflagged cells
            if (not self.revealed[r][c]) and (not self.flagged[r][c]) and (not self.mine_grid[r][c]):
                # Reveal current cell
                self.revealed[r][c] = True
                # If zero neighbour mines, add all valid neighbors to keep expanding
                if self.number_grid[r][c] == 0:
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if not (dr == 0 and dc == 0):
                                nr = r + dr
                                nc = c + dc
                                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                                    if (not self.revealed[nr][nc]) and (not self.flagged[nr][nc]) and (not self.mine_grid[nr][nc]):
                                        cells.append((nr, nc))
        # After revealing, check for a win
        self.check_win()

    def toggle_flag(self, row, col):
        """cannot toggle a cell to be flagged if already revealed"""
        if self.revealed[row][col] or self.game_over:
            return
        self.flagged[row][col] = not self.flagged[row][col]  # Reverse a flag toggle

    def check_win(self):
        """If a non-mine cell remains hidden don't proceed to set the flag to win"""
        for row in range(self.rows):
            for col in range(self.cols):
                if (not self.mine_grid[row][col]) and (not self.revealed[row][col]):
                    return
        self.won = True
        self.game_over = True

def make_empty_grid(total_rows, total_cols, default_value):
    """make a rows x cols grid with same default value"""
    grid_matrix = []
    for r in range(total_rows):
        row_list = []
        for c in range(total_cols):
            row_list.append(default_value)
        grid_matrix.append(row_list)
    return grid_matrix

def save_score(name, time_taken, difficulty):
    """writes name of user, time taken and difficulty in file"""
    file = open(SCORE_FILE, "a")
    line = name + " | " + str(time_taken) + " | " + difficulty + "\n"
    file.write(line)
    file.close()

def load_scores():
    """to load scores"""
    try:
        file = open(SCORE_FILE, "r")
        lines = file.readlines()
        file.close()
        return lines
    except:
        return []

def calculate_statistics(board):
    """sample to calculate stats"""
    white_count = 0
    for row in range(board.rows):
        for col in range(board.cols):
            if not board.mine_grid[row][col] and board.number_grid[row][col] == 0:
                white_count += 1
    total_cells = board.rows * board.cols
    percentage = (white_count * 100) / total_cells
    return white_count, total_cells, percentage

def get_button_size(num_cols):
    """identify button size of various buttons"""
    if num_cols <= 9:
        return 3, 8
    elif num_cols <= 16:
        return 2, 6
    else:
        return 1, 4

# --- Main Game UI Class ---
class Game:
    def __init__(self, window):
        self.window = window
        self.window.title("Minesweeper")
        # Game state
        self.board = None
        self.buttons = []
        self.clicked_mine = None
        self.difficulty = ""
        self.game_started = False
        self.start_time = None
        self.timer_running = False

        # UI references
        self.timer_label = None
        self.mines_label = None
        self.scaled_images = {}

        # Load base images once
        self.images = {
            "hidden": tk.PhotoImage(file="Grid.png"),
            "empty": tk.PhotoImage(file="empty.png"),
        }
        for i in range(1, 9):
            self.images[f"num{i}"] = tk.PhotoImage(file=f"grid{i}.png")
        self.images["mine"] = tk.PhotoImage(file="mine.png")
        self.images["mineClicked"] = tk.PhotoImage(file="mineClicked.png")
        self.images["mineFalse"] = tk.PhotoImage(file="mineFalse.png")
        self.images["flag"] = tk.PhotoImage(file="flag.png")

        self.show_menu()

    def clear_screen(self):
        """#acts like a convenient function that simulates destroying and creating a new screen"""
        for widget in self.window.winfo_children():
            widget.destroy()

    def show_menu(self):
        """#shows all the possible menus (can think of it like an anchor that has all the operations in place)"""
        self.clear_screen()
        self.window.geometry("400x400")
        frame = tk.Frame(self.window, bg="white")
        frame.pack(expand=True)
        
        tk.Label(frame, text="MINESWEEPER", font=("Arial", 20, "bold"), bg="white").pack(pady=20)
        tk.Button(frame, text="Play Game", width=20, height=2,
                  command=self.show_difficulty).pack(pady=10)
        tk.Button(frame, text="View Scores", width=20, height=2,
                  command=self.show_scores).pack(pady=10)
        tk.Button(frame, text="View Statistics", width=20, height=2,
                  command=self.show_stats).pack(pady=10)
        tk.Button(frame, text="Exit", width=20, height=2,
                  command=self.window.quit).pack(pady=10)

    def show_difficulty(self):
        """#allows user to select difficulty"""
        self.clear_screen()
        self.window.geometry("400x400")
        frame = tk.Frame(self.window, bg="white")
        frame.pack(expand=True)
        tk.Label(frame, text="Select Difficulty", font=("Arial", 16, "bold"),
                 bg="white").pack(pady=20)

        tk.Button(frame, text="Easy (9x9, 10 mines)", width=25, height=2,
                  command=lambda: self.start_game(EASY, "Easy")).pack(pady=5)
        tk.Button(frame, text="Intermediate (16x16, 40 mines)", width=25, height=2,
                  command=lambda: self.start_game(INTERMEDIATE, "Intermediate")).pack(pady=5)
        tk.Button(frame, text="Expert (16x30, 99 mines)", width=25, height=2,
                  command=lambda: self.start_game(EXPERT, "Expert")).pack(pady=5)
        tk.Button(frame, text="Custom", width=25, height=2,
                  command=self.show_custom).pack(pady=5)
        tk.Button(frame, text="Back", width=25, height=2,
                  command=self.show_menu).pack(pady=5)

    def show_custom(self):
        """#function for handling custom board scenarios"""
        dialog = CustomConfigDialog(self.window)
        self.window.wait_window(dialog)
        if dialog.result is None:
            return
        rows = dialog.result['rows']
        cols = dialog.result['cols']
        mines = dialog.result['mines']
        config = {'rows': rows, 'cols': cols, 'mines': mines}
        difficulty_text = f"Custom ({rows}x{cols}, {mines} mines)"
        self.start_game(config, difficulty_text)

    def start_game(self, difficulty, name):
        """initialize board with given difficulty and start game"""
        self.board = Board(difficulty['rows'], difficulty['cols'], difficulty['mines'])  # Class call for Board with parameters of rows, cols and mines (from difficulty list)
        self.difficulty = name
        self.game_started = False
        self.timer_running = False
        self.clicked_mine = None
        self.draw_board()

    def compute_tile_size(self):
        """Compute dynamic tile size based on board size and screen limits."""
        cols = self.board.cols
        rows = self.board.rows

        # Get actual screen size
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()

        # Limit the usable area (header + footer)
        usable_h = screen_h - 200

        # Tile sizes that would fit the whole board on screen
        fit_tile_w = screen_w // cols
        fit_tile_h = usable_h // rows

        tile_size = min(fit_tile_w, fit_tile_h, MAX_TILE_SIZE)

        # Determine if board actually fits on screen
        fits_by_width = (cols * tile_size) <= screen_w
        fits_by_height = (rows * tile_size) <= usable_h

        fits_screen = fits_by_width and fits_by_height

        # If too big → scroll mode with minimum tile size
        if not fits_screen:
            return MIN_TILE_SIZE, True

        return max(tile_size, MIN_TILE_SIZE), False


    def draw_board(self):
        """#to create the visual elements of the Board"""
        self.clear_screen()# Hi! your clear screen friend again to save the day
        # compute tile size + scroll behavior
        tile_size, use_scroll = self.compute_tile_size()

        # Set reasonable window size
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        win_w = min(screen_w - 100, max(400, self.board.cols * tile_size + 100))
        win_h = min(screen_h - 100, max(300, self.board.rows * tile_size + 150))
        self.window.geometry(f"{win_w}x{win_h}")

        # scale all images to tile_size
        self.scaled_images = {}
        for key, img in self.images.items():
            base_w = img.width()
            if base_w <= tile_size:
                # use original (or could zoom)
                self.scaled_images[key] = img
            else:
                factor = max(1, base_w // tile_size)
                self.scaled_images[key] = img.subsample(factor)

        # header
        header = tk.Frame(self.window, bg="#dddddd")
        header.pack(fill="x")

        self.mines_label = tk.Label(header, text="Mines: 000", font=("Arial", 11, "bold"),
                                    bg="#dddddd")
        self.mines_label.pack(side="left", padx=10, pady=5)

        title_label = tk.Label(header, text="Minesweeper", font=("Arial", 13, "bold"),
                               bg="#dddddd")
        title_label.pack(side="left", expand=True)

        self.timer_label = tk.Label(header, text="Time: 000", font=("Arial", 11, "bold"),
                                    bg="#dddddd")
        self.timer_label.pack(side="right", padx=10)
        
        # if scrollbars needed
        if use_scroll:
            outer = tk.Frame(self.window)
            outer.pack(fill="both", expand=True)

            canvas = tk.Canvas(outer, bg="black")
            canvas.pack(side="left", fill="both", expand=True)

            scroll_y = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
            scroll_y.pack(side="right", fill="y")

            scroll_x = tk.Scrollbar(outer, orient="horizontal", command=canvas.xview)
            scroll_x.pack(side="bottom", fill="x")

            # link scrollbars to canvas
            canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)


            board_frame = tk.Frame(canvas)
            canvas.create_window((0, 0), window=board_frame, anchor="nw")

            def on_config(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
            board_frame.bind("<Configure>", on_config)
        else:
            # normal mode — no scrollbars
            board_frame = tk.Frame(self.window, bg="black")
            board_frame.pack(padx=5, pady=5)

        
        # Build buttons
        self.buttons = []
        for row in range(self.board.rows):
            button_row = []
            for col in range(self.board.cols):
                btn = tk.Button(
                    board_frame,
                    image=self.scaled_images["hidden"],
                    width=tile_size,
                    height=tile_size,
                    command=lambda r=row, c=col: self.left_click(r, c)
                )
                btn.grid(row=row, column=col, padx=0, pady=0)
                # Windows & most mice
                btn.bind("<Button-3>", lambda event, r=row, c=col: self.right_click(event, r, c))

                # macOS trackpad secondary click (two-finger click)
                btn.bind("<Button-2>", lambda event, r=row, c=col: self.right_click(event, r, c))

                # macOS Control + Click (treated as right-click)
                btn.bind("<Control-Button-1>", lambda event, r=row, c=col: self.right_click(event, r, c))

                button_row.append(btn)
            self.buttons.append(button_row)

        # footer
        footer = tk.Frame(self.window, bg="white")
        footer.pack(fill="x", pady=5)

        info_text = "Left click: Reveal | Right click: Flag"
        tk.Label(footer, text=info_text, font=("Arial", 9), bg="white").pack(pady=2)

        tk.Button(footer, text="Back to Menu", width=18,
                  command=self.show_menu).pack(pady=3)

        self.update_board()

    def start_timer(self):
        """live timer after 1st click"""
        self.timer_running = True
        self.start_time = time.time()
        self._tick_timer()

    def _tick_timer(self):
        if not self.timer_running or self.board is None:
            return
        elapsed = int(time.time() - self.start_time)
        if self.timer_label is not None:
            self.timer_label.config(text=f"Time: {elapsed:03d}")
        if not self.board.game_over:
            self.window.after(1000, self._tick_timer)

    def left_click(self, row, col):
        """actions if left button is clicked"""
        if self.board is None or self.board.game_over:
            return

        if not self.game_started:
            self.board.place_mines(row, col)
            self.game_started = True
            if not self.timer_running:
                self.start_timer()

        # BEFORE revealing: check if the clicked cell is a mine
        if self.board.mine_grid[row][col]:
            self.clicked_mine = (row, col)

        self.board.reveal_cell(row, col)
        self.update_board()

        # if the game is over, reveal all mines, wrong flags, then update UI again
        if self.board.game_over:
            self.reveal_all_mines()
            self.mark_wrong_flags()
            self.update_board()
            self.end_game()
            
    def right_click(self, event, row, col):
        """for counting remained flags/mines"""
        if self.board is None or self.board.game_over or not self.game_started:
            return
        self.board.toggle_flag(row, col)
        self.update_board()

    def update_board(self):
        if self.board is None:
            return
        
        for row in range(self.board.rows):
            for col in range(self.board.cols):
                btn = self.buttons[row][col]

                # revealed cell
                if self.board.revealed[row][col]:
                    if self.board.mine_grid[row][col]:
                        # clicked mine
                        if self.clicked_mine == (row, col) and not self.board.won:
                            btn.config(image=self.scaled_images["mineClicked"])
                        else:
                            btn.config(image=self.scaled_images["mine"])
                    else:
                        if (self.board.game_over and
                            self.board.flagged[row][col] and
                            not self.board.mine_grid[row][col]):
                            btn.config(image=self.scaled_images["mineFalse"])
                        else:
                            num = self.board.number_grid[row][col]
                            if num == 0:
                                btn.config(image=self.scaled_images["empty"])
                            else:
                                btn.config(image=self.scaled_images[f"num{num}"])

                elif self.board.flagged[row][col]:
                    # Hidden but flagged
                    btn.config(image=self.scaled_images["flag"])

                else:
                    # Hidden and not flagged
                    btn.config(image=self.scaled_images["hidden"])

        # Update mine counter
        flags = sum(row.count(True) for row in self.board.flagged)
        remaining = self.board.mines - flags
        if self.mines_label is not None:
            self.mines_label.config(text=f"Mines: {remaining:03d}")

    def reveal_all_mines(self):
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if self.board.mine_grid[r][c]:
                    self.board.revealed[r][c] = True

    def mark_wrong_flags(self):
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if self.board.flagged[r][c] and not self.board.mine_grid[r][c]:
                    # mark incorrect flags as revealed so update_board() draws mineFalse.png
                    self.board.revealed[r][c] = True

    def end_game(self):
        """outcome of a win or lose and display appropriate values"""
        self.timer_running = False
        self.window.update_idletasks()
        if self.board.won == True:
            elapsed = time.time() - self.start_time if self.start_time else 0
            name = simpledialog.askstring("You Won!", "Enter your name:")
            if not name:
                name = "Player"
            save_score(name, elapsed, self.difficulty)
            messagebox.showinfo("You Won!",
                                f"Congratulations!\nTime: {int(elapsed)} seconds")
        else:
            messagebox.showinfo("Game Over", "You hit a mine!\nGame Over!")

    def show_scores(self):
        """display scores"""
        self.clear_screen()
        self.window.geometry("400x400")
        frame = tk.Frame(self.window, bg="white")
        frame.pack(expand=True, padx=20, pady=20)

        tk.Label(frame, text="Highscores", font=("Arial", 16, "bold"),
                 bg="white").pack(pady=10)

        scores = load_scores()
        if len(scores) == 0:
            text = "No scores yet!"
        else:
            text = ""
            for i in range(len(scores)):
                text = text + scores[i]
        tk.Label(frame, text=text, font=("Arial", 10), bg="white",
                 justify="left").pack(pady=10)
        tk.Button(frame, text="Back", width=20, height=2,
                  command=self.show_menu).pack(pady=10)

    def show_stats(self):
        """show stats (to be enhanced)"""
        self.clear_screen()
        self.window.geometry("500x400")
        '''Depricated       
        frame = tk.Frame(self.window, bg="white")
        frame.pack(padx=20, pady=20)
        title = tk.Label(frame, text="Statistics", font=("Arial", 16, "bold"), bg="white")
        title.pack(pady=10)
        sample_board = Board(9, 9, 10)
        placed = 0
        while placed < 10:
            r = random.randint(0, 8)
            c = random.randint(0, 8)
            if sample_board.mine_grid[r][c] == False:
                sample_board.mine_grid[r][c] = True
                placed = placed + 1
        sample_board.calculate_numbers()
        white, total, percent = calculate_statistics(sample_board)
        stats_text = "Sample Board: 9x9 with 10 mines\n"
        stats_text = stats_text + "\nWhite cells (0 adjacent): " + str(white)
        stats_text = stats_text + "\nPercentage: " + str(int(percent)) + "%"
        stats_text = stats_text + "\nTotal cells: " + str(total)
        stats_text = stats_text + "\nMine density: " + str(int((10/total)*100)) + "%"
        stats_label = tk.Label(frame, text=stats_text, font=("Arial", 10), bg="white")
        stats_label.pack(pady=10)
        back_button = tk.Button(frame, text="Back", width=20, height=2, command=self.show_menu)
        back_button.pack(pady=10)'''

        frame = tk.Frame(self.window, bg="white")
        frame.pack(padx=20, pady=20)

        title1 = tk.Label(frame, text="ANALYTICS", font=("Arial", 21, "bold"), bg="white")
        title1.pack(pady=4)
        title2 = tk.Label(frame, text="Select Difficulty", font=("Arial", 16, "bold"), bg="white")
        title2.pack(pady=3)

        easy_button = tk.Button(frame, text="Easy (9x9, 10 mines)", width=20, height=2,
                               command=lambda: self.default_analysis(EASY, "Easy"))
        easy_button.pack(pady=10)

        inter_button = tk.Button(frame, text="Intermediate (16x16, 40 mines)", width=20, height=2,
                                command=lambda: self.default_analysis(INTERMEDIATE, "Intermediate"))
        inter_button.pack(pady=10)

        expert_button = tk.Button(frame, text="Expert (16x30, 99 mines)", width=20, height=2,
                                 command=lambda: self.default_analysis(EXPERT, "Expert"))
        expert_button.pack(pady=10)

        # Custom board button
        custom_button = tk.Button(frame, text="Custom", width=20, height=2, command=self.custom_board_analysis)
        custom_button.pack(pady=10)

        back_button = tk.Button(frame, text="Back", width=20, height=2, command=self.show_menu)
        back_button.pack(pady=10)
        
    def default_analysis(self, difficulty, name):
        self.n_board_analysis_iter = simpledialog.askinteger(f"N-board analysis: {name}", "Enter the number of generated boards")
        if self.n_board_analysis_iter is None:
            return
        else:            
            self.n_board_analysis_rows = difficulty["rows"]
            self.n_board_analysis_columns = difficulty["cols"]
            self.n_board_analysis_mines = difficulty["mines"] #take the values of the keys in the dict
        self.start_analysis()

    def custom_board_analysis(self): #needs changing to accomodate the new board validity check function
        self.n_board_analysis_iter = simpledialog.askstring("N-board analysis: Custom", "Enter the number of generated boards") #asks for number of generated boards
        #print(self.n_board_analysis_iter)
        if self.n_board_analysis_iter is None:
            return
        else:
            try:
                int(self.n_board_analysis_iter)
            except Exception:
                messagebox.showerror("Error", "Please enter a valid integer.") #if not integer, throw an error
                return self.custom_board_analysis() #and return to the custom menu (by executing the function again)
        
        self.n_board_analysis_iter = int(self.n_board_analysis_iter)
        if self.n_board_analysis_iter <= 0:
            messagebox.showerror("Error", "Please enter a positive number.") #if <= 0, throw an error
            return self.custom_board_analysis() #and return to the custom menu (by executing the function again)

        """Depricated
        self.n_board_analysis_rows = simpledialog.askinteger("N-board analysis: Custom", "Enter rows")
        if self.n_board_analysis_rows is None:
            return
        self.n_board_analysis_columns = simpledialog.askinteger("N-board analysis: Custom", "Enter columns")
        if self.n_board_analysis_columns is None:
            return
        max_mines = (self.n_board_analysis_rows * self.n_board_analysis_columns) - 1
        self.n_board_analysis_mines = simpledialog.askinteger("N-board analysis: Custom", f"Enter mines (1-{max_mines}):", minvalue=1, maxvalue=max_mines)
        if self.n_board_analysis_mines is None:
            return"""
        #then asks for the number of rows, columns, and mines
        dialog = CustomConfigDialog(self.window) #facilitates the class CustomConfigDialog
        self.window.wait_window(dialog)
        if dialog.result is None:
            return
        
        self.start_analysis()

    def start_analysis(self):
        #with open(BOARD_FILE, "w") as file, open(BOARD_FILE_CSV, "w") as file_csv:
        with open(BOARD_FILE_CSV, "w") as file_csv:
            for n in range(self.n_board_analysis_iter): #export n_board_analysis_iter number of boards
                n_board = Board(self.n_board_analysis_rows, self.n_board_analysis_columns, self.n_board_analysis_mines)
                placed = 0                                
                while placed < self.n_board_analysis_mines:
                    r = random.randint(0, self.n_board_analysis_rows - 1)
                    c = random.randint(0, self.n_board_analysis_columns - 1)
                    if not n_board.mine_grid[r][c]:
                        n_board.mine_grid[r][c] = True
                        placed += 1 #do the add mines part again, but without the safe first click, and n times
                n_board.calculate_numbers() #export n boards to csv file via the calculate_numbers() function
        
        messagebox.showinfo("Success!", "Your boards have been exported. Click OK to generate analytics charts.")

        #after closing csv file, starts generating charts
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
        pdf_filename = f"analytics_{self.n_board_analysis_rows}x{self.n_board_analysis_columns}_" \
                           f"{self.n_board_analysis_mines}mines_{timestamp}.pdf"
        self.generate_analytics(BOARD_FILE_CSV, output_pdf=pdf_filename, show_plots=True, radius=1)
        

    def load_boards_from_csv(self, csvboardfile):
        """Load all boards from CSV file. Returns list of 2D numpy arrays (dtype=object)."""
        # Create empty list to store all loaded boards
        boards = []
        # Create empty list to store current board being loaded
        current_board = []
        
        # Open the CSV file for reading
        with open(csvboardfile, "r", newline="") as file:
            # Create CSV reader object
            reader = csv.reader(file)
            # Read each row in the CSV file
            for row in reader:
                # Skip empty rows
                if not row:
                    continue
                # Get the first value in the row and remove extra spaces
                first = str(row[0]).strip()
                # Check if this row marks the start of a new board
                if first in ("Output:", "Output"):
                    # If we have a current board, save it to the boards list
                    if current_board:
                        try:
                            # Convert the board to a numpy array
                            boards.append(np.array(current_board, dtype=object))
                        except Exception:
                            # If conversion fails, add as regular array
                            boards.append(np.array(current_board))
                        # Reset current board for next board
                        current_board = []
                    else:
                        # Initialize empty current board
                        current_board = []
                else:
                    # This is a row of board data
                    parsed_row = []
                    # Check if row needs special parsing (space-separated values)
                    if len(row) == 1 and isinstance(row[0], str) and (" " in row[0]) and ("," not in row[0]):
                        # Split row by spaces if it's space-separated
                        split_cells = row[0].split()
                    else:
                        # Use row as-is if comma-separated
                        split_cells = row
                    # Process each cell in the row
                    for cell in split_cells:
                        # Remove extra spaces from cell value
                        cell_str = str(cell).strip()
                        # Skip empty cells
                        if cell_str == "":
                            continue
                        # Check if cell contains a mine
                        if cell_str == "M":
                            parsed_row.append("M")
                        else:
                            try:
                                # Try to convert cell to integer (number of adjacent mines)
                                parsed_row.append(int(cell_str))
                            except ValueError:
                                # Keep as string if not a number
                                parsed_row.append(cell_str)
                    # Add parsed row to current board if not empty
                    if parsed_row:
                        current_board.append(parsed_row)
            # Add the last board if it exists
            if current_board:
                try:
                    boards.append(np.array(current_board, dtype=object))
                except Exception:
                    boards.append(np.array(current_board))
        return boards
    
    def count_white_cells(self, board):
        """Count cells with value 0 (no adjacent mines)."""
        # Start counting at zero
        count = 0
        # Get board dimensions
        rows, cols = board.shape
        # Check every cell on the board
        for i in range(rows):
            for j in range(cols):
                # Get cell value
                cell = board[i][j]
                # Check if cell is a number and equals zero (empty cell)
                if isinstance(cell, (int, np.integer)) and int(cell) == 0:
                    # Count this white cell
                    count += 1
        # Return total count of white cells
        return count

    def get_number_distribution(self, boards):
        """Distribution of numbers 0..8 across all boards."""
        # Create dictionary to count occurrences of each number (0-8)
        distribution = {i: 0 for i in range(9)}
        # Check every board
        for board in boards:
            # Get board dimensions
            rows, cols = board.shape
            # Check every cell on the board
            for i in range(rows):
                for j in range(cols):
                    # Get cell value
                    cell = board[i][j]
                    # Skip mine cells
                    if cell == "M":
                        continue
                    try:
                        # Try to convert cell to integer
                        v = int(cell)
                    except Exception:
                        # Skip if not a number
                        continue
                    # Count if number is between 0 and 8
                    if 0 <= v <= 8:
                        distribution[v] += 1
        # Return counts for each number
        return distribution

    def count_mine_clusters(self, board):
        """Count connected mine clusters (8-connectivity)."""
        # Get board dimensions
        rows, cols = board.shape
        # Create array of zeros (0 = no mine, 1 = mine)
        mine_array = np.zeros((rows, cols), dtype=int)
        # Fill the mine array based on board data
        for i in range(rows):
            for j in range(cols):
                if board[i][j] == "M":
                    # Mark cell as containing mine
                    mine_array[i][j] = 1
        # Define connectivity pattern (check all 8 surrounding cells)
        structure = np.array([[1, 1, 1],
                            [1, 1, 1],
                            [1, 1, 1]])
        try:
            # Use scipy to find connected mine groups
            labeled_array, num_clusters = label(mine_array, structure=structure)
            # Return number of distinct mine clusters
            return int(num_clusters)
        except Exception:
            # If clustering fails, return total mine count as fallback
            return int(np.sum(mine_array))

    def calculate_mine_heatmap_raw(self, boards, radius=1):
        """Return average raw mine count in a (2*radius+1)^2 window around each cell."""
        
        # Get board dimensions from first board
        rows, cols = boards[0].shape
        # Create array to store heatmap values
        heatmap = np.zeros((rows, cols), dtype=float)
        # Process each board
        for board in boards:
            # Check each cell on the board
            for i in range(rows):
                for j in range(cols):
                    # Start counting mines around this cell
                    mine_count = 0
                    # Check cells within the specified radius
                    for di in range(-radius, radius + 1):
                        for dj in range(-radius, radius + 1):
                            # Calculate coordinates of neighboring cell
                            ni, nj = i + di, j + dj
                            # Check if neighboring cell is within board boundaries
                            if 0 <= ni < rows and 0 <= nj < cols:
                                # Check if neighboring cell has a mine
                                if board[ni][nj] == "M":
                                    # Count this mine
                                    mine_count += 1
                    # Add mine count to heatmap for this position
                    heatmap[i][j] += mine_count
        # Calculate average mine count across all boards
        heatmap /= float(len(boards))
        # Return the completed heatmap
        return heatmap

    def calculate_mine_density_heatmap(self, boards, radius=1):
        """Return density (0..1) - average mines divided by window size."""
        # Get raw mine counts
        raw = self.calculate_mine_heatmap_raw(boards, radius)
        # Return None if no data
        if raw is None:
            return None
        # Calculate total number of cells in the checking window
        window_cells = (2 * radius + 1) ** 2
        # Convert counts to density (proportion of mines in window)
        return raw / float(window_cells)

    def calculate_mine_variance_heatmap(self, boards, radius=1):
        """Return variance across boards of the mine count in each window."""
        # Need at least 2 boards to calculate variance
        if len(boards) < 2:
            return None
        # Get board dimensions
        rows, cols = boards[0].shape
        # Create 3D array to store mine counts for each board
        counts = np.zeros((len(boards), rows, cols), dtype=float)
        # Process each board
        for b_idx, board in enumerate(boards):
            # Check each cell on the board
            for i in range(rows):
                for j in range(cols):
                    # Start counting mines around this cell
                    c = 0
                    # Check cells within specified radius
                    for di in range(-radius, radius + 1):
                        for dj in range(-radius, radius + 1):
                            # Calculate coordinates of neighboring cell
                            ni, nj = i + di, j + dj
                            # Check if neighboring cell is within board
                            if 0 <= ni < rows and 0 <= nj < cols:
                                # Check if neighboring cell has mine
                                if board[ni][nj] == "M":
                                    # Count this mine
                                    c += 1
                    # Store mine count for this position and board
                    counts[b_idx, i, j] = c
        # Calculate variance across all boards for each position
        return np.var(counts, axis=0)

    def calculate_mine_heatmap_smoothed(self, boards, radius=1, sigma=2.0):
        """Return Gaussian-smoothed version of the raw heatmap."""
        # Get raw mine counts
        raw = self.calculate_mine_heatmap_raw(boards, radius)
        # Return None if no data
        if raw is None:
            return None
        
        return gaussian_filter(raw, sigma=sigma)
        
    def generate_combined_analytics_figure(self, boards, radius=1):
        """Create a 2×2 analytics figure."""
        
        # Get board dimensions
        rows, cols = boards[0].shape

        # Prepare data for all four charts
        # Count white cells (zeros) for each board
        white_counts = [self.count_white_cells(b) for b in boards]
        # Get distribution of numbers 0-8 across all boards
        num_dist = self.get_number_distribution(boards)
        # Count mine clusters for each board
        cluster_counts = [self.count_mine_clusters(b) for b in boards]
        # Calculate raw mine heatmap
        raw_heatmap = self.calculate_mine_heatmap_raw(boards, radius)

        # Create figure with 2 rows and 2 columns of charts
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # (1) TOP-LEFT — White Cell Histogram
        ax = axes[0, 0]
        # Create histogram of white cell counts
        ax.hist(white_counts, bins=10, edgecolor="black")
        # Set chart title
        ax.set_title("Histogram of Number of White Cells per Board", fontsize=13)
        # Set x-axis label
        ax.set_xlabel("White Cells", fontsize=11)
        # Set y-axis label
        ax.set_ylabel("# Boards", fontsize=11)

        # (2) TOP-RIGHT — Number Distribution
        ax = axes[0, 1]
        # Get numbers 0-8 for x-axis
        nums = list(num_dist.keys())
        # Get counts for each number for y-axis
        counts = list(num_dist.values())
        # Create bar chart of number distribution
        ax.bar(nums, counts, edgecolor="black")
        # Set chart title
        ax.set_title("Distribution of Number of Cells with Values", fontsize=13)
        # Set x-axis label
        ax.set_xlabel("Value Indicated", fontsize=11)
        # Set y-axis label
        ax.set_ylabel("# Cells", fontsize=11)

        # (3) BOTTOM-LEFT — Mine Cluster Histogram
        ax = axes[1, 0]
        # Create histogram of mine cluster counts
        ax.hist(cluster_counts, bins=10, edgecolor="black")
        # Set chart title
        ax.set_title("Number of Mine Clusters per Board", fontsize=13)
        # Set x-axis label
        ax.set_xlabel("# Mine Clusters", fontsize=11)
        # Set y-axis label
        ax.set_ylabel("# Boards", fontsize=11)

        # (4) BOTTOM-RIGHT — Heatmap
        ax = axes[1, 1]
        # Display heatmap as colored image
        hm = ax.imshow(raw_heatmap, cmap="viridis", interpolation="nearest")
        # Set chart title
        ax.set_title(f"Average Number of Mines (radius {radius})", fontsize=13)
        # Set x-axis ticks (column numbers starting from 1)
        ax.set_xticks(np.arange(cols))
        ax.set_yticks(np.arange(rows))
        ax.set_xticklabels(np.arange(1, cols + 1))
        ax.set_yticklabels(np.arange(1, rows + 1))
        # Set axis labels
        ax.set_xlabel("Column", fontsize=11)
        ax.set_ylabel("Row", fontsize=11)
        # Add color bar to show value scale
        cbar = fig.colorbar(hm, ax=ax)
        cbar.ax.tick_params(labelsize=10)

        # Adjust spacing between charts
        fig.tight_layout()
        # Return the complete figure
        return fig

    def generate_analytics(self, csvboardfile, output_pdf=None, show_plots=True, radius=1):
        """Generate all analytics from CSV file and optionally save to PDF."""
        # Print loading message
        print(f"Loading boards from {csvboardfile}...")
        # Load boards from CSV file
        boards = self.load_boards_from_csv(csvboardfile)
        #print(boards)
        # Check if any boards were loaded
        if not boards:
            print("No boards found!")
            return None

        # Print loading summary
        print(f"Loaded {len(boards)} boards.")
        # Get dimensions of first board
        rows, cols = boards[0].shape
        print(f"Board dimensions: {rows} × {cols}")

        # Generate the combined analytics figure
        print("Generating combined analytics figure...")
        combined_figure = self.generate_combined_analytics_figure(boards, radius=radius)

        # Create list of figures (only one in this case)
        figures = [combined_figure]

        # Save to PDF if requested
        save_pdf = messagebox.askyesno(
                            "Save plot PDF",
                             "Do you want to save the plot as a PDF?"
        )

        if save_pdf:
            
            # Create PDF file
            with PdfPages(output_pdf) as pdf:
                # Save each figure to the PDF
                for fig in figures:
                    pdf.savefig(fig, bbox_inches="tight")
            
            messagebox.showinfo("Success!", "PDF saved successfully! Click OK to show plot.")
            plt.show()
        else:
            plt.show()

        # Calculate statistics for summary
        white_cells = [self.count_white_cells(board) for board in boards]
        clusters = [self.count_mine_clusters(board) for board in boards]

        # Create summary dictionary with key statistics
        summary = {
            "num_boards": len(boards),
            "board_dimensions": (rows, cols),
            "white_cells_mean": float(np.mean(white_cells)),
            "white_cells_median": float(np.median(white_cells)),
            "white_cells_std": float(np.std(white_cells)),
            "clusters_mean": float(np.mean(clusters)),
            "clusters_median": float(np.median(clusters)),
            "clusters_std": float(np.std(clusters)),
        }

        # Print formatted summary statistics
        print("=" * 60)
        print("SUMMARY STATISTICS")
        print("=" * 60)
        print(f"Number of boards analyzed: {summary['num_boards']}")
        print(f"Board dimensions: {summary['board_dimensions'][0]} × {summary['board_dimensions'][1]}")
        print("White cells (0 adjacent mines):")
        print(f"  Mean: {summary['white_cells_mean']:.2f}")
        print(f"  Median: {summary['white_cells_median']:.2f}")
        print(f"  Std Dev: {summary['white_cells_std']:.2f}")
        print("Mine clusters:")
        print(f"  Mean: {summary['clusters_mean']:.2f}")
        print(f"  Median: {summary['clusters_median']:.2f}")
        print(f"  Std Dev: {summary['clusters_std']:.2f}")
        print("=" * 60 + "\n")

        # Return summary statistics
        return summary

def validate_custom_config(rows, cols, mines):
    """Validate custom board configuration (with hard cap and warning)."""
    if (rows < 1) or (cols < 1) or (mines < 1):
        return "Rows, columns, and mines must be at least 1."
    if (rows > 98) and (cols > 100):
        return "Rows and columns must be at most 98 x 100."
    total = rows * cols
    if total < 3:
        return "Board must have at least 3 cells."
    
    if mines > total - 2:
        return f"Too many mines! Maximum: {total - 2} (need at least 2 safe cells)."
    return None

#Abhinab Update(15th November 2025): added comments to customconfigdialog
class CustomConfigDialog(tk.Toplevel):
    """
    Dialog for custom Minesweeper board configuration.
    Warns if board size >3600 cells, prevents above 9800.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Custom Board") 
        self.resizable(False, False)
        self.transient(parent) #makes the dialogbox always appear above the parent window
        self.grab_set() #makes behind layers inaccesible untill this one is either closed or entered
        self.result = None
        frame = tk.Frame(self, padx=15, pady=15)
        frame.pack()
        self.game = game #to accept class game arguments


        warning_text = (
            "Max: 9800 cells."
            "Warning: Selecting over 3600 cells may cause display or performance issues."
        )
        tk.Label(
            frame, text=warning_text, font=("Arial", 9), fg="red"
        ).grid(row=0, column=0, columnspan=2, pady=8, sticky="w")

        #Abhinab Update (15th November 2025): Converted IntVar to StringVar to avoid implicit conversion to Integer and enable usage of isdigit() function
        self.rows_var = tk.StringVar(value="9") #default value to be displayed
        self.cols_var = tk.StringVar(value="9")
        self.mines_var = tk.StringVar(value="10")
        tk.Label(frame, text="Rows:").grid(row=1, column=0, sticky="e", pady=8)
        tk.Entry(frame, textvariable=self.rows_var, width=10).grid(row=1, column=1, pady=8)
        tk.Label(frame, text="Columns:").grid(row=2, column=0, sticky="e", pady=8)
        tk.Entry(frame, textvariable=self.cols_var, width=10).grid(row=2, column=1, pady=8)
        tk.Label(frame, text="Mines:").grid(row=3, column=0, sticky="e", pady=8)
        tk.Entry(frame, textvariable=self.mines_var, width=10).grid(row=3, column=1, pady=8)

        # Start and Cancel buttons
        btns = tk.Frame(frame)
        btns.grid(row=4, column=0, columnspan=2, pady=15)
        tk.Button(btns, text="Start", width=8, command=self.on_ok).pack(side="left", padx=5)
        tk.Button(btns, text="Cancel", width=8, command=self.on_cancel).pack(side="left", padx=5)

        # Keyboard shortcuts for Enter/Esc
        self.bind("<Return>", lambda e: self.on_ok())
        self.bind("<Escape>", lambda e: self.on_cancel())

        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    ##Abhinab Update (15th November 2025): Fixed logic of checking decimal values
    def on_ok(self):
        rows_str = self.rows_var.get() #to retrieve rows val
        cols_str = self.cols_var.get() #to retrieve column val
        mines_str = self.mines_var.get() #to retrieve mines val
        
        # Validate that all are integer strings
        for val, label in ((rows_str, "Rows"), (cols_str, "Columns"), (mines_str, "Mines")):
            if not (val.isdigit()):
                messagebox.showerror("Error", f"{label} must be an integer greater than 0 (no decimals or letters).")
                return

        rows = int(rows_str)
        cols = int(cols_str)
        mines = int(mines_str)
        
        error = validate_custom_config(rows, cols, mines)
        if error:
            messagebox.showerror("Invalid Configuration", error)
            return

        self.game.n_board_analysis_rows = rows
        self.game.n_board_analysis_columns = cols
        self.game.n_board_analysis_mines = mines #for the analytics part
        
        self.result = {'rows': rows, 'cols': cols, 'mines': mines}
        self.destroy()


    def on_cancel(self):
        self.result = None
        self.destroy()



# --- Run App ---
window = tk.Tk()
game = Game(window)
window.mainloop()
