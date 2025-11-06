import random
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog

EASY = {'rows': 9, 'cols': 9, 'mines': 10}
INTERMEDIATE = {'rows': 16, 'cols': 16, 'mines': 40}
EXPERT = {'rows': 16, 'cols': 30, 'mines': 99}
SCORE_FILE = 'highscores.txt'
BOARD_FILE = 'grid_matrix.txt' #board answer

class Board:
    """The game board mainly of 3 elements of the mines, mine count, flags and the reveal count"""

    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.mine_grid = make_empty_grid(rows, cols, False) #Turned to true if its a mine
        self.number_grid = make_empty_grid(rows, cols, 0) # how many mines are around count
        self.revealed = make_empty_grid(rows, cols, False) # cells revealed to and by a player
        self.flagged = make_empty_grid(rows, cols, False) # cells flagged by player
        self.game_over = False
        self.won = False


    def place_mines(self, safe_row, safe_col):   # to place the mines after first click (ensures a safe-click first criteria)
        placed = 0
        while placed < self.mines:
            row = random.randint(0, self.rows - 1) #to ensure boundary is not crossed as maximum allowed value is max row and column
            col = random.randint(0, self.cols - 1)

            flag_proceed_mine = 1  
            if row == safe_row and col == safe_col:  #dont place mine in first clicked sell
                flag_proceed_mine = 0
            elif self.mine_grid[row][col]: #dont place mine where mine already exists
                flag_proceed_mine = 0

            if flag_proceed_mine:  #check above conditions and if flag is 1 (above conditionsa re not true), place mine
                self.mine_grid[row][col] = True
                placed += 1

        self.calculate_numbers()  


    def calculate_numbers(self):  # to count number of mines next to a cell
        for row in range(self.rows):
            for col in range(self.cols):
                if not self.mine_grid[row][col]: #if cell isn't mine, search for adjacent mine
                    count = 0
                    #below dynamic allows us to check for left,right,top,bottom and diagonal mines since all are at a max distance of 1
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            
                            if not (dr == 0 and dc == 0): #doesnt count the cell in reference (0,0 coordinate)
                                r = row + dr
                                c = col + dc
                                # Check if they are not the first or last elements before checking neighbours
                                if (r >= 0) and (r < self.rows) and (c >= 0) and (c < self.cols):
                                    if self.mine_grid[r][c]: #if cell at row r column c has mine, increase the number in the cell at row row and column col by 1
                                        count += 1                   
                       
                    self.number_grid[row][col] = count
                else:
                    count = 'M'
                    self.number_grid[row][col] = count #add the count to mine as 'M'
        self.reveal_board()
    #by this point, board has been created. execute code to export board to txt file

    def reveal_board(self):
        with open(BOARD_FILE, 'w') as file:
            for row in range(self.rows):
                row_cells = []
                for col in range(self.cols):                    
                    row_cells.append(str(self.number_grid[row][col]))                    
                file.write(' '.join(row_cells) + '\n') #export board answer to txt file                                
                

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
    
    def reveal_cell(self, row, col):  #reveals content of the cell if appropriate
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
            i = i + 1

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
        if self.revealed[row][col]:    #cannot toggle a cell to be flagged if already revealed
            return
        self.flagged[row][col] = not self.flagged[row][col]  # Reverse a flag toggle

    def check_win(self):
        for row in range(self.rows):
            for col in range(self.cols):
                # If a non-mine cell remains hidden dont proceed to set the flag to win
                if (not self.mine_grid[row][col]) and (not self.revealed[row][col]):
                    return
        self.won = True
        self.game_over = True

# make a rows x cols grid with same default value
def make_empty_grid(total_rows, total_cols, default_value):
    grid_matrix = []
    for r in range(total_rows):
        row_list = []
        for c in range(total_cols):
            row_list.append(default_value)
        grid_matrix.append(row_list)
    return grid_matrix

def save_score(name, time_taken, difficulty):
    file = open(SCORE_FILE, 'a')
    line = name + " | " + str(time_taken) + " | " + difficulty + "\n" # writes name of user, time taken and difficulty in file
    file.write(line)
    file.close()

def load_scores(): #to load scores
    try:
        file = open(SCORE_FILE, 'r')
        lines = file.readlines()
        file.close()
        return lines
    except:
        return []

def calculate_statistics(board): #sample to calculate stats
    white_count = 0
    for row in range(board.rows):
        for col in range(board.cols):
            if not board.mine_grid[row][col] and board.number_grid[row][col] == 0:
                white_count += 1
    total_cells = board.rows * board.cols
    percentage = (white_count * 100) / total_cells
    return white_count, total_cells, percentage

def get_button_size(num_cols):  #to identify button size of various buttons
    if num_cols <= 9:
        return 3, 8
    elif num_cols <= 16:
        return 2, 6
    else:
        return 1, 4

#Game class to create initial window which has all options
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

    def clear_screen(self): #acts like a convenient function that simulates destroying and creating a new screen
        for widget in self.window.winfo_children():
            widget.destroy()

    def show_menu(self): #shows all the possible menus (can think of it like an anchor that has all the operations in place)
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

    def show_difficulty(self): #allows user to select difficulty
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

        # Custom board button
        custom_button = tk.Button(frame, text="Custom", width=20, height=2, command=self.show_custom)
        custom_button.pack(pady=10)

        back_button = tk.Button(frame, text="Back", width=20, height=2, command=self.show_menu)
        back_button.pack(pady=10)

    def show_custom(self): #function for handling custom board scenarios
        rows = simpledialog.askinteger("Custom Board", "Enter rows (5-30):", minvalue=5, maxvalue=30)
        if rows is None:
            return
        cols = simpledialog.askinteger("Custom Board", "Enter columns (5-30):", minvalue=5, maxvalue=30)
        if cols is None:
            return
        max_mines = (rows * cols) - 1
        mines = simpledialog.askinteger("Custom Board", f"Enter mines (1-{max_mines}):", minvalue=1, maxvalue=max_mines)
        if mines is None:
            return
        config = {'rows': rows, 'cols': cols, 'mines': mines}
        difficulty_text = f"Custom ({rows}x{cols}, {mines} mines)"
        self.start_game(config, difficulty_text)

    def start_game(self, difficulty, name):
        self.board = Board(difficulty['rows'], difficulty['cols'], difficulty['mines']) #Class call for Board with parameters of rows,cols and mines (from difficulty list) 
        self.game_started = False
        self.start_time = None
        self.difficulty = name
        self.draw_board()

    def draw_board(self): #to create the visual elements of the Board
        self.clear_screen() # Hi! your clear screen friend again to save the day
        btn_width, font_size = get_button_size(self.board.cols)
        window_width = self.board.cols * (btn_width * 6 + 2) + 30 #arbitary calculation of window_width (needs to be fixed based on UI)
        window_height = self.board.rows * 25 + 120 #arbitary calculation of window length (needs to be fixed/changed based on UI)
        self.window.geometry(f"{window_width}x{window_height}")

        info_text = "Left click: Reveals cell | Right click: To Flag cell" 
        info = tk.Label(self.window, text=info_text, font=("Arial", 10), bg="lightgray")
        info.pack(pady=5) #pady is for padding on y axis (length), padx is to pad on x axis (width)

        board_info = tk.Label(self.window, text=f"Board: {self.board.rows}x{self.board.cols} ({self.board.mines} mines)",
                             font=("Arial", 10), bg="lightgray")
        board_info.pack(pady=2)

        board_frame = tk.Frame(self.window, bg="black")
        board_frame.pack(padx=5, pady=5)

        self.buttons = []
        for row in range(self.board.rows):
            button_row = []
            for col in range(self.board.cols): # IMPORTANT: Code to create the clickable buttons on the minesweeper board and bind both left click and right click (little GPT help used here)
                btn = tk.Button(board_frame, width=btn_width, height=1, font=("Arial", font_size),
                              command=lambda r=row, c=col: self.left_click(r, c))
                btn.grid(row=row, column=col, padx=1, pady=1)
                btn.bind("<Button-3>", lambda event, r=row, c=col: self.right_click(event, r, c))
                button_row.append(btn)
            self.buttons.append(button_row) #appends button to button row

        self.update_board()

        bottom_frame = tk.Frame(self.window, bg="white")
        bottom_frame.pack(pady=10)
        quit_button = tk.Button(bottom_frame, text="Back to Menu", width=20, height=1, command=self.show_menu)
        quit_button.pack()

    def left_click(self, row, col):  #actions if left button is clicked
        if self.game_started == False:
            self.board.place_mines(row, col) #place mines only after first button is clicked by initializing flag to False
            self.game_started = True 
            self.start_time = time.time() #start timer only after first click
        self.board.reveal_cell(row, col) #reveal the cell on left click
        self.update_board() #call update board after every left click
        if self.board.game_over == True:   
            self.end_game()  #if Game over flag is turned true end the game

    def right_click(self, event, row, col): #remember right click is for triggering
        if self.game_started == True: #first click always has to be a left click
            self.board.toggle_flag(row, col) 
            self.update_board() #call update board for every right click

    def update_board(self):  #mastermind code for handling the outcome of every event/trigger (UI change based on every click in the game bloard)
        for row in range(self.board.rows): 
            for col in range(self.board.cols):
                btn = self.buttons[row][col]
                if self.board.revealed[row][col]:
                    if self.board.mine_grid[row][col]:
                        btn.config(text="*", bg="red", fg="white", state="disabled") #turn mine cell to red
                    else:
                        num = self.board.number_grid[row][col]
                        if num == 0:
                            btn.config(text="", bg="lightgray", state="disabled") #if empty cell (surrounding mine is 0, turn to light gray without any print)
                        else:
                            btn.config(text=str(num), bg="lightgray", state="disabled") #if cell has adjacent values, turn it into light-gray and text to be the count
                elif self.board.flagged[row][col]:
                    btn.config(text="F", bg="yellow", fg="black", state="normal")  #if flagged row, turn it yellow
                else:
                    btn.config(text="", bg="gray", fg="black", state="normal") #otherwise do nothing (not really needed but kept to ensure integrity of code)

    def end_game(self): #function to define outcome of a win or lose and display appropriate values
        if self.board.won == True:
            elapsed = time.time() - self.start_time #if won, calculate win time and lost time
            name = simpledialog.askstring("You Won!", "Enter your name:")
            if name == None: 
                name = "John Doe" #if no name entered, default to John Doe 
            save_score(name, elapsed, self.difficulty)
            messagebox.showinfo("You Won!", "Congratulations!\nTime: " + str(int(elapsed)) + " seconds") #Congratulations text
        else:
            messagebox.showinfo("Game Over", "You hit a mine!\nGame Over!") #if lost, you hit a mine
        self.show_menu()

    def show_scores(self): #function to display scores
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

    def show_stats(self): #function to show stats (to be enhanced)
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

window = tk.Tk()
game = Game(window)
window.mainloop()
