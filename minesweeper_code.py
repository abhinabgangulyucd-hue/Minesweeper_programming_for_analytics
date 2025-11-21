import random
import time
from datetime import datetime
import csv
#import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
#from scipy.ndimage import label
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog

EASY = {'rows': 9, 'cols': 9, 'mines': 10}
INTERMEDIATE = {'rows': 16, 'cols': 16, 'mines': 40}
EXPERT = {'rows': 16, 'cols': 30, 'mines': 99}
SCORE_FILE = 'highscores.txt'
#BOARD_FILE = "grid_matrix.txt"
BOARD_FILE_CSV = "grid_matrix.csv" #board answer


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
                    #by this point, board has been created. execute code to export board(s) to csv file
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
        '''Depricated
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
        back_button.pack(pady=10)'''

        self.window.geometry("800x800")
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

        #after closing csv file and clicking OK, starts generating charts
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
        pdf_filename = f"analytics_{timestamp}_{self.n_board_analysis_rows}x{self.n_board_analysis_columns}_" \
                           f"{self.n_board_analysis_mines}mines.pdf"
        self.generate_analytics(BOARD_FILE_CSV, output_pdf=pdf_filename, show_plots=True, radius=1)
        

    def load_boards_from_csv(self, csvboardfile):
        #Ayaan (Nov 20th fix:) Simplified logic for reading the boards from csv given structure is fixed
        boards = []
        current_board = []
        
        with open(csvboardfile, "r", newline="") as file: #reads CSV file Board by Board and then Row by Row
            reader = csv.reader(file)
            for row in reader:
                if not row:
                    continue
                    
                if row[0] == "Output:":
                    if current_board:
                        boards.append(current_board)
                        current_board = []
                else:
                    new_row = []
                    for cell in row:
                        if cell == "M":
                            new_row.append("M")
                        else:
                            new_row.append(int(cell))
                    current_board.append(new_row)
            
            if current_board:
                boards.append(current_board)
            
        return boards
    
    def count_white_cells(self, board):
        """Count cells with value 0 (no adjacent mines)."""
        count = 0
        for row in board:
            for cell in row:
                if isinstance(cell, (int)) and int(cell) == 0:
                    count += 1
        return count  #Ayaan (Nov 20th fix:) now returns white cells count for entire board instead of single row for each board

    def get_number_distribution(self, boards):
        """Distribution of numbers 0 to 8 across all boards"""
        distribution = {i: 0 for i in range(9)}#creating a dictionary
        print(distribution)
        for board in boards:
            for row in board:
                for cell in row:
                    if cell == "M":
                        continue
                    try:
                        v = int(cell)
                    except Exception:
                        continue
                    if 0 <= v <= 8:
                        distribution[v] += 1
        return distribution

    def count_mine_clusters(self, board):
        """Count mine clusters using while with clear exit condition"""
        rows = len(board)
        cols = len(board[0])
        #print(board[0])
        
        visited = set()
        clusters = 0
        
        for i in range(rows):
            for j in range(cols):
                if board[i][j] == "M" and (i, j) not in visited: #enters this loop if the mine detected in a cell and if that cell is not previously visited
                    clusters += 1
                    
                    stack = [(i, j)]  
                    while len(stack) > 0:  # While there are still mines to process in this cluster
                        x, y = stack.pop()
                        visited.add((x, y))
                        
                       
                        for dx in (-1, 0, 1): # This Checks all 8 neighbors
                            for dy in (-1, 0, 1):
                                if dx == 0 and dy == 0:
                                    continue
                                nx, ny = x + dx, y + dy
                                #  add to stack if neighbor is a new mine
                                if (0 <= nx < rows and 0 <= ny < cols and
                                    board[nx][ny] == "M" and 
                                    (nx, ny) not in visited and
                                    (nx, ny) not in stack):
                                    stack.append((nx, ny))
            
        return clusters

    def calculate_mine_density(self, boards, radius=1):
        """Calculate how dense mines are around each position across all boards"""
        if not boards:
            return None
            
        rows = len(boards[0])
        cols = len(boards[0][0])
          
        heatmap = [[0.0 for z in range(cols)] for z in range(rows)] #stores average mine counts
        
        # count mines around every cell for every board
        for board in boards:
            for i in range(rows):
                for j in range(cols):
                    mine_count = 0
                    # check cells for mine within the radius
                    for dx in range(-radius, radius + 1):
                        for dy in range(-radius, radius + 1):
                            ni, nj = i + dx, j + dy
                            # looks if the neighbouring cells consist of mine
                            if 0 <= ni < rows and 0 <= nj < cols and board[ni][nj] == "M":
                                mine_count += 1
                    heatmap[i][j] += mine_count                
        board_count = len(boards) #totals to averages conversions
        for i in range(rows):
            for j in range(cols):
                heatmap[i][j] /= board_count
        
        return heatmap
      
    def create_analytics_charts(self, boards, radius=1):
        """Charts creation"""
        rows = len(boards[0])
        cols = len(boards[0][0])

        white_counts = [self.count_white_cells(b) for b in boards]
        num_dist = self.get_number_distribution(boards)
        cluster_counts = [self.count_mine_clusters(b) for b in boards]
        mine_density = self.calculate_mine_density(boards, radius)
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10)) #figure with 2X2 layout

        # Chart 1-White cells per board
        ax = axes[0, 0]
        if white_counts:
            ax.hist(white_counts, bins=8, edgecolor="black", alpha=0.7)
        ax.set_title("Empty Cells Per Board", fontsize=13)
        ax.set_xlabel("Number of Empty Cells")
        ax.set_ylabel("Number of Boards")
        ax.grid(True, alpha=0.3)

        # Chart 2-Number distribution
        ax = axes[0, 1]
        numbers = list(num_dist.keys())
        counts = list(num_dist.values())
        bars = ax.bar(numbers, counts, edgecolor="black", alpha=0.7)
        
        for bar, count in zip(bars, counts): #adding counts on top of the bars
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), 
                   str(count), ha='center', va='bottom')
        ax.set_title("How Often Each Number Appears", fontsize=13)
        ax.set_xlabel("Number on Cell")
        ax.set_ylabel("Total Appearances")
        ax.set_xticks(numbers)
        ax.grid(True, alpha=0.3)
       
        # Chart 3-Mine clusters histogram
        ax = axes[1, 0]
        if cluster_counts:
            ax.hist(cluster_counts, bins=8, edgecolor="black", alpha=0.7)
        ax.set_title("Mine Clusters Per Board")
        ax.set_xlabel("Number of Mine Clusters")
        ax.set_ylabel("Number of Boards")
        ax.grid(True, alpha=0.3)

        # Chart 4-Mine density heatmap
        ax = axes[1, 1]
        # Create heatmap without numpy - use pcolormesh instead of imshow
        img = ax.pcolormesh(mine_density, cmap="viridis")
        ax.set_title("Where Mines Usually Appear")
        ax.set_xlabel("Column")
        ax.set_ylabel("Row")
               
        plt.colorbar(img, ax=ax, label='Average Nearby Mines') #adding color bar to explain the colors
        
        #labels the rows and columns with numbers
        cols = len(mine_density[0])
        rows = len(mine_density)
        ax.set_xticks(range(cols))
        ax.set_yticks(range(rows))
        ax.set_xticklabels([str(i+1) for i in range(cols)])
        ax.set_yticklabels([str(i+1) for i in range(rows)])
        
        plt.tight_layout() #to fit with page
        return fig

    #Ayaan(20th November Fix:) Removed redundant functions and made below code simpler
    def generate_analytics(self, csv_file, output_pdf=None, show_plots=True, radius=1):
        """Analyze all boards and create summary charts"""
        print(f"Reading boards from {csv_file}...")
        boards = self.load_boards_from_csv(csv_file)
        
        if not boards:
            print("No boards found to analyze")
            messagebox.showwarning("No Data", "No boards were found to analyze")
            return None

        print(f"Analyzing {len(boards)} boards")
        rows = len(boards[0])
        cols = len(boards[0][0])
        print(f"Each board: {rows} rows x {cols} columns")

        #stats
        white_counts = [self.count_white_cells(board) for board in boards]
        cluster_counts = [self.count_mine_clusters(board) for board in boards]
        num_dist = self.get_number_distribution(boards)

        figure = self.create_analytics_charts(boards, radius)

        # Ask about saving PDF
        save_pdf = messagebox.askyesno("Save Results", "Save charts as PDF file?")
        
        if save_pdf and output_pdf:
            try:
                with PdfPages(output_pdf) as pdf:
                    pdf.savefig(figure, bbox_inches="tight")
                messagebox.showinfo("Success", f"Saved as {output_pdf}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save: {str(e)}")
               
        if show_plots: #shows chart
            plt.show()

        # calc summary numbers
        def calculate_stats(numbers):
            if not numbers:
                return 0, 0, 0
            mean = sum(numbers) / len(numbers)
            median = sorted(numbers)[len(numbers) // 2]
            std = (sum((x - mean) ** 2 for x in numbers) / len(numbers)) ** 0.5
            return mean, median, std

        white_mean, white_median, white_std = calculate_stats(white_counts)
        cluster_mean, cluster_median, cluster_std = calculate_stats(cluster_counts)

        print("ANALYSIS RESULTS")
        print("=" * 50)
        print(f"Boards analyzed: {len(boards)}")
        print(f"Board size: {rows} x {cols}")
        print("\nEmpty cells (0 mines around):")
        print(f"  Average: {white_mean:.1f} per board")
        print(f"  Middle: {white_median} per board") 
        print(f"  Variation: {white_std:.1f}")
        print("\nMine clusters:")
        print(f"  Average: {cluster_mean:.1f} per board")
        print(f"  Middle: {cluster_median} per board")
        print(f"  Variation: {cluster_std:.1f}")

        return {
            "num_boards": len(boards),
            "board_size": (rows, cols),
            "white_cells_avg": white_mean,
            "white_cells_median": white_median, 
            "white_cells_std": white_std,
            "clusters_avg": cluster_mean,
            "clusters_median": cluster_median,
            "clusters_std": cluster_std,
        }

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
