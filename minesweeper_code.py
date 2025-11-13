import random
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog

EASY = {'rows': 9, 'cols': 9, 'mines': 10}
INTERMEDIATE = {'rows': 16, 'cols': 16, 'mines': 40}
EXPERT = {'rows': 16, 'cols': 30, 'mines': 99}
SCORE_FILE = 'highscores.txt'


class Board:
    """The game board mainly of 3 elements of the mines, mine count, flags and the reveal count"""
    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.mine_grid = make_empty_grid(rows, cols, False)  # Turned to true if its a mine
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
        self.calculate_numbers()

    def calculate_numbers(self):
        """count number of mines next to a cell"""
        for row in range(self.rows):
            for col in range(self.cols):
                if not self.mine_grid[row][col]:
                    count = 0
                    # below dynamic allows us to check for left, right, top, bottom and diagonal mines since all are at a max distance of 1
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if not (dr == 0 and dc == 0):  # doesn't count the cell in reference (0,0 coordinate)
                                r = row + dr
                                c = col + dc
                                # Check if they are not the first or lsat elements before checking neighbours
                                if (r >= 0) and (r < self.rows) and (c >= 0) and (c < self.cols):
                                    if self.mine_grid[r][c]:
                                        count += 1
                    self.number_grid[row][col] = count

    def reveal_cell(self, row, col):
        """reveals content of the cell if appropriate"""
        # Do nothing if already revealed or flagged
        if self.revealed[row][col]:
            return
        if self.flagged[row][col]:
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
        if self.revealed[row][col]:
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
    """crmake  a rows x cols grid with same default value"""
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
        self.board = None
        self.buttons = []
        self.game_started = False
        self.start_time = None
        self.difficulty = ""
        self.show_menu()

    def clear_screen(self):
        """#acts like a convenient function that simulates destroying and creating a new screen"""
        for widget in self.window.winfo_children():
            widget.destroy()

    def show_menu(self):
        """#shows all the possible menus (can think of it like an anchor that has all the operations in place)"""
        self.clear_screen()
        self.window.geometry("600x600")
        frame = tk.Frame(self.window, bg="white")
        frame.pack(padx=20, pady=20)
        title = tk.Label(frame, text="MINESWEEPER", font=("Arial", 20, "bold"), bg="white")
        title.pack(pady=20)
        play_button = tk.Button(frame, text="Play Game", width=20, height=2, command=self.show_difficulty)
        play_button.pack(pady=10)
        scores_button = tk.Button(frame, text="View Score", width=20, height=2, command=self.show_scores)
        scores_button.pack(pady=10)
        stats_button = tk.Button(frame, text="View Statistics", width=20, height=2, command=self.show_stats)
        stats_button.pack(pady=10)
        exit_button = tk.Button(frame, text="Exit", width=20, height=2, command=self.window.quit)
        exit_button.pack(pady=10)

    def show_difficulty(self):
        """#allows user to select difficulty"""
        self.clear_screen()
        self.window.geometry("800x800")
        frame = tk.Frame(self.window, bg="white")
        frame.pack(padx=20, pady=20)
        title = tk.Label(frame, text="Select Difficulty", font=("Arial", 16, "bold"), bg="white")
        title.pack(pady=20)
        easy_button = tk.Button(frame, text="Easy (9x9, 10 mines)", width=20, height=2,
                               command=lambda: self.start_game(EASY, "Easy"))
        easy_button.pack(pady=10)
        inter_button = tk.Button(frame, text="Intermediate (16x16, 40 mines)", width=20, height=2,
                                command=lambda: self.start_game(INTERMEDIATE, "Intermediate"))
        inter_button.pack(pady=10)
        expert_button = tk.Button(frame, text="Expert (16x30, 99 mines)", width=20, height=2,
                                command=lambda: self.start_game(EXPERT, "Expert"))
        expert_button.pack(pady=10)
        custom_button = tk.Button(frame, text="Custom", width=20, height=2, command=self.show_custom)
        custom_button.pack(pady=10)
        back_button = tk.Button(frame, text="Back", width=20, height=2, command=self.show_menu)
        back_button.pack(pady=10)

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
        self.game_started = False
        self.start_time = None
        self.difficulty = name
        self.draw_board()

    def draw_board(self):
        """#to create the visual elements of the Board"""
        self.clear_screen()# Hi! your clear screen friend again to save the day
        btn_width, font_size = get_button_size(self.board.cols)
        window_width = self.board.cols * (btn_width * 6 + 2) + 30  # calculation of window_width
        window_height = self.board.rows * 25 + 120  # calculation of window length
        self.window.geometry(f"{window_width}x{window_height}")
        info_text = "Left click: Reveals cell | Right click: To Flag cell"
        info = tk.Label(self.window, text=info_text, font=("Arial", 10), bg="lightgray")
        info.pack(pady=5)  # pady is for padding on y axis (length), padx is to pad on x axis (width)
        board_info = tk.Label(self.window, text=f"Board: {self.board.rows}x{self.board.cols} ({self.board.mines} mines)",
                             font=("Arial", 10), bg="lightgray")
        board_info.pack(pady=2)
        board_frame = tk.Frame(self.window, bg="black")
        board_frame.pack(padx=5, pady=5)
        self.buttons = []
        for row in range(self.board.rows):
            button_row = []
            for col in range(self.board.cols):  # IMPORRTANT: create the clickable buttons on the minesweeper board and bind left and right click
                btn = tk.Button(board_frame, width=btn_width, height=1, font=("Arial", font_size),
                                command=lambda r=row, c=col: self.left_click(r, c))
                btn.grid(row=row, column=col, padx=1, pady=1)
                btn.bind("<Button-3>", lambda event, r=row, c=col: self.right_click(event, r, c))
                button_row.append(btn)
            self.buttons.append(button_row)
        self.update_board()
        bottom_frame = tk.Frame(self.window, bg="white")
        bottom_frame.pack(pady=10)
        quit_button = tk.Button(bottom_frame, text="Back to Menu", width=20, height=1, command=self.show_menu)
        quit_button.pack()

    def left_click(self, row, col):
        """actions if left button is clicked"""
        if self.game_started == False:
            self.board.place_mines(row, col)  # place mines only after first button is clicked
            self.game_started = True
            self.start_time = time.time()  # start timer only after first click
        self.board.reveal_cell(row, col)  # reveal the cell on left click
        self.update_board()  # call update board after every left click
        if self.board.game_over == True:
            self.end_game()  # if Game over flag is turned true end the game

    def right_click(self, event, row, col):
        """right click for flag trigger"""
        if self.game_started == True:  # first click always has to be a left click
            self.board.toggle_flag(row, col)
            self.update_board()  # call update board for every right click

    def update_board(self):
        """handle outcome of every event/trigger (UI change based on every click in the game board)"""
        for row in range(self.board.rows):
            for col in range(self.board.cols):
                btn = self.buttons[row][col]
                if self.board.revealed[row][col]:
                    if self.board.mine_grid[row][col]:
                        btn.config(text="*", bg="red", fg="white", state="disabled")  # mine cell to red
                    else:
                        num = self.board.number_grid[row][col]
                        if num == 0:
                            btn.config(text="", bg="lightgray", state="disabled")  # empty cell with 0 mines -> light gray
                        else:
                            btn.config(text=str(num), bg="lightgray", state="disabled")  # cell has adjacent values
                elif self.board.flagged[row][col]:
                    btn.config(text="F", bg="yellow", fg="black", state="normal")  # if flagged row, turn it yellow
                else:
                    btn.config(text="", bg="gray", fg="black", state="normal")  # otherwise default

    def end_game(self):
        """outcome of a win or lose and display appropriate values"""
        if self.board.won == True:
            elapsed = time.time() - self.start_time  # if won, calculate elapsed
            name = simpledialog.askstring("You Won!", "Enter your name:")
            if name == None:
                name = "John Doe"  # default if no name entered
            save_score(name, elapsed, self.difficulty)
            messagebox.showinfo("You Won!", "Congratulations!\nTime: " + str(int(elapsed)) + " seconds")  # Congratulations
        else:
            messagebox.showinfo("Game Over", "You hit a mine!\nGame Over!")  # lost, hit a mine
        self.show_menu()

    def show_scores(self):
        """display scores"""
        self.clear_screen()
        self.window.geometry("500x400")
        frame = tk.Frame(self.window, bg="white")
        frame.pack(padx=20, pady=20)
        title = tk.Label(frame, text="Highscores", font=("Arial", 16, "bold"), bg="white")
        title.pack(pady=10)
        scores = load_scores()
        if len(scores) == 0:
            text = "No scores yet!"
        else:
            text = ""
            for i in range(len(scores)):
                text = text + scores[i]
        score_label = tk.Label(frame, text=text, font=("Arial", 10), bg="white", justify="left")
        score_label.pack(pady=10)
        back_button = tk.Button(frame, text="Back", width=20, height=2, command=self.show_menu)
        back_button.pack(pady=10)

    def show_stats(self):
        """show stats (to be enhanced)"""
        self.clear_screen()
        self.window.geometry("400x400")
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
        back_button.pack(pady=10)

def validate_custom_config(rows, cols, mines):
    """Validate custom board configuration (with hard cap and warning)."""
    if not all(isinstance(x, int) for x in [rows, cols, mines]):
        return "All fields must be integers."
    if rows < 1 or cols < 1 or mines < 1:
        return "Rows, columns, and mines must be at least 1."
    if rows > 98 or cols > 100:
        return "Rows and columns must be at most 98 x 100."
    total = rows * cols
    if total < 3:
        return "Board must have at least 3 cells."
    if mines > total - 2:
        return f"Too many mines! Maximum: {total - 2} (need at least 2 safe cells)."
    return None

class CustomConfigDialog(tk.Toplevel):
    """
    Dialog for custom Minesweeper board configuration.
    Warns if board size >3600 cells, prevents above 9800.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Custom Board")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.result = None

        # --- Layout ---
        frame = tk.Frame(self, padx=15, pady=15)
        frame.pack()

        # Info label for warnings/hard limit
        warning_text = (
            "Max: 9800 cells. "
            "Warning: Selecting over 3600 cells may cause display or performance issues."
        )
        tk.Label(
            frame, text=warning_text, font=("Arial", 9), fg="red", wraplength=300
        ).grid(row=0, column=0, columnspan=2, pady=8, sticky="w")

        # Input fields: Rows, Columns, Mines
        self.rows_var = tk.IntVar(value=9)
        self.cols_var = tk.IntVar(value=9)
        self.mines_var = tk.IntVar(value=10)

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

        # Center dialog on parent window
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def on_ok(self):
        # Fetch inputs
        try:
            rows = self.rows_var.get()
            cols = self.cols_var.get()
            mines = self.mines_var.get()
        except Exception:
            messagebox.showerror("Error", "Please enter valid numbers.")
            return

        total_cells = rows * cols

        # dont allow more than 9800 cells
        if total_cells > 8000:
            messagebox.showerror(
                "Board Too Large",
                f"Maximum allowed is 9800 cells. You selected {total_cells}."
            )
            return

        # show dialog if more than 3600 cells
        if total_cells > 3600:
            proceed = messagebox.askyesno(
                "Warning: Large Board",
                (
                    f"Board size: {total_cells} cells.\n"
                    "This may break the game and cause display or performance issues.\n\n"
                    "Do you really want to proceed?"
                )
            )
            if not proceed:
                return

        # Validate all scenarios
        error = validate_custom_config(rows, cols, mines)
        if error:
            messagebox.showerror("Invalid Configuration", error)
            return

        self.result = {'rows': rows, 'cols': cols, 'mines': mines}
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()



# --- Run App ---
window = tk.Tk()
game = Game(window)
window.mainloop()
