import board
import pieces
import Tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import IPython
import chess, chess.uci
import time
import io
import os
import shutil
import copy
import webbrowser
import h5py
import numpy as np
import random
import ast

class ELO_page(tk.Frame):
	def __init__(self, parent):
		tk.Frame.__init__(self, parent)
		self.parent = parent
		self.user_elo_rating = 0
		self.user_name = ''
		self.welcome_message = tk.Label(self.parent, text="Welcome to the best \n multi-agent chess training software", font=("Helvetica", 30))
		self.welcome_message.grid(row = 0, column = 0, columnspan = 2)

		self.namelabel = tk.Label(self.parent, text="Enter your username")
		self.namelabel.grid(row = 1, column = 0)
		self.namelabel.config(font=("Helvetica", 24))

		self.user_name1 = tk.Entry(self.parent, font=("Helvetica", 24))
		self.user_name1.grid(row = 1, column = 1)

		self.entrylabel = tk.Label(self.parent, text="Enter your ELO rating")
		self.entrylabel.grid(row = 2, column = 0)
		self.entrylabel.config(font=("Helvetica", 24))

		self.user_elo_rating1 = tk.Entry(self.parent, font=("Helvetica", 24))
		self.user_elo_rating1.grid(row = 2, column = 1)

		# self.welcome_message1 = tk.Label(self.parent, text="Click here to get your ELO rating estimate", font=("Helvetica", 24))
		# self.welcome_message1.grid(row = 2, column = 0, columnspan = 2)

		self.link = tk.Button(self.parent, command = self.call_back, text="Click here for ELO estimate", cursor="hand2", font=("Helvetica", 24))
		self.link.grid(row = 3, column = 0, columnspan = 2)

		self.but1 = tk.Button(self.parent, text='Quit', command=self.parent.quit,font=("Helvetica", 24)).grid(row=4, column=0)
		self.but2 = tk.Button(self.parent, text='Play', command=self.assign_value, font=("Helvetica", 24)).grid(row=4, column=1)

	def call_back(self):
		webbrowser.open_new('http://www.chessmaniac.com/ELORating/ELO_Chess_Rating.shtml')

	def assign_value(self):
		self.user_elo_rating = self.user_elo_rating1.get()
		self.user_name = self.user_name1.get()
		self.parent.destroy()


class BoardGuiTk(tk.Frame):
	pieces = {}
	selected = None
	selected_piece = None
	hilighted = None
	icons = {}

	color1 = "grey"
	color2 = "white"

	rows = 8
	columns = 8

	@property
	def canvas_size(self):
		return (self.columns * self.square_size,
				self.rows * self.square_size)

	def __init__(self, parent, chessboard, engm, main_board, eng1, a1_board, eng2, a2_board, info1, info2, user_elo, comp_elo, square_size=64):

		self.chessboard = chessboard
		self.square_size = square_size
		self.parent = parent
		self.TURN = 'user' # user or engine or suggest or decide
		# Coordinate dictionary
		self.CD = {}
		self.axisx = ['a','b','c','d','e','f','g','h']
		self.axisy = ['8','7','6','5','4','3','2','1']
		for count,i in enumerate(self.axisx):
			self.CD[i] = 17+35*(count)
		for count,i in enumerate(self.axisy):
			self.CD[i] = 17+35*(count)
		self.a1_move = 0
		self.a2_move = 0
		self.move_history = []
		# Board information
		self.engine_m = engm
		self.main_board = main_board
		self.engine_1 = eng1 
		self.a1_board = a1_board
		self.engine_2 = eng2
		self.a2_board = a2_board
		# Store data
		self.DB = []
		self.W_moves = []
		self.B_moves = []
		self.A1_moves = []
		self.A2_moves = []
		self.U_moves = []

		canvas_width = self.columns * square_size
		canvas_height = self.rows * square_size

		tk.Frame.__init__(self, parent)

		# Chess board
		self.canvas = tk.Canvas(self, width=canvas_width, height=canvas_height, background="grey")
		self.canvas.grid(row = 1, column = 1)
		self.canvas.bind("<Configure>", self.refresh)
		self.canvas.bind("<Button-1>", self.click)

		# Agent 1 suggested move canvas
		self.canvas1 = tk.Canvas(self, width=280, height=280, background="grey")
		self.canvas1.grid(row = 1, column = 0)
		self.canvas1.bind("<Configure>", self.refresh)	
		full_image1 = Image.open('./Main_board_state.jpg')
		full_image1.thumbnail((280,280), Image.ANTIALIAS)
		img1 = ImageTk.PhotoImage(full_image1)
		self.parent.img1 = img1
		self.image_on_canvas1 = self.canvas1.create_image(140, 140, image = img1)

		# Agent 2 suggested move canvas
		self.canvas2 = tk.Canvas(self, width=280, height=280, background="grey")
		self.canvas2.grid(row = 1, column = 3)
		self.canvas2.bind("<Configure>", self.refresh)	
		full_image2 = Image.open('./Main_board_state.jpg')
		full_image2.thumbnail((280,280), Image.ANTIALIAS)
		img2 = ImageTk.PhotoImage(full_image2)
		self.parent.img2 = img2
		self.image_on_canvas2 = self.canvas2.create_image(140, 140, image = img2)

		# # Agent 1 proposed moves 
		# self.agent1 = tk.Text(self, width=40, height=36, background="grey")
		# self.agent1.tag_configure('bold_italics', font=('Arial', 12, 'bold', 'italic'))
		# self.agent1.tag_configure('big', font=('Verdana', 20, 'bold'))
		# self.agent1.tag_configure('color', foreground='#476042', font=('Tempus Sans ITC', 12, 'bold'))
		# self.agent1.tag_configure("center", justify='center')
		# self.agent1.insert(tk.END,'\n Agent 1 \n', 'big')
		# self.agent1.tag_add("center", "1.0", "end")
		# self.agent1.grid(row = 1, column = 0)
		
		# # Agent 2 proposed moves 
		# self.agent2 = tk.Text(self, width=40, height=36, background="grey")
		# self.agent2.tag_configure('bold_italics', font=('Arial', 12, 'bold', 'italic'))
		# self.agent2.tag_configure('big', font=('Verdana', 20, 'bold'))
		# self.agent2.tag_configure('color', foreground='#476042', font=('Tempus Sans ITC', 12, 'bold'))
		# self.agent2.tag_configure("center", justify='center')
		# self.agent2.insert(tk.END,'\n Agent 2 \n', 'big')
		# self.agent2.tag_add("center", "1.0", "end")
		# self.agent2.grid(row = 1, column = 3)

		# Agent 1 information
		self.agent1i = tk.Text(self, width=40, height=18, background="grey", wrap='word')
		self.agent1i.tag_configure('bold_italics', font=('Arial', 20, 'bold', 'italic'))
		self.agent1i.tag_configure('big', font=('Verdana', 20, 'bold'))
		self.agent1i.tag_configure('color', foreground='#476042', font=('Tempus Sans ITC', 12, 'bold'))
		Statement1 = info1
		self.agent1i.insert(tk.END, Statement1, 'bold_italics')
		self.agent1i.grid(row = 3, column = 0)

		# Agent 2 information
		self.agent2i = tk.Text(self, width=40, height=18, background="grey", wrap='word')
		self.agent2i.tag_configure('bold_italics', font=('Arial', 20, 'bold', 'italic'))
		self.agent2i.tag_configure('big', font=('Verdana', 20, 'bold'))
		self.agent2i.tag_configure('color', foreground='#476042', font=('Tempus Sans ITC', 12, 'bold'))
		Statement2 = info2
		self.agent2i.insert(tk.END, Statement2, 'bold_italics')
		self.agent2i.grid(row = 3, column = 3)

		# Scroll bar 
		self.yscrollbar = tk.Scrollbar(self)
		self.yscrollbar.grid(row=3, column=2, sticky='ns')
		# Move history
		self.comp = tk.Text(self, width=72, height=18, background="grey", wrap = 'word')
		self.comp.tag_configure('big', font=('Verdana', 20, 'bold'))
		self.comp.tag_configure('color', foreground='black', font=('Verdana', 12, 'bold'))
		self.comp.tag_configure("center", justify='center')
		self.comp.insert(tk.END,'\n Move history \n', 'big')
		self.comp.tag_add("left", "1.0", "end")
		self.comp.grid(row = 3, column = 1)	
		self.yscrollbar.config(command=self.comp.yview)

		# Computer rating bar at the top
		self.cratingsbar = tk.Frame(self, height=64)
		self.label_status1 = tk.Label(self.cratingsbar, text="  Computer ELO rating is {}".format(comp_elo), fg="black")
		self.label_status1.grid(in_=self.cratingsbar)
		self.cratingsbar.grid(row = 0, column = 0, columnspan = 4)

		# Human rating bar at the bottom
		self.hratingsbar = tk.Frame(self, height=64)
		self.label_status2 = tk.Label(self.hratingsbar, text="  Player ELO rating is {}".format(user_elo), fg="black")
		self.label_status2.grid(in_=self.hratingsbar)
		self.hratingsbar.grid(row = 2, column = 0, columnspan = 4)

		# Status bar at the bottom
		self.statusbar = tk.Frame(self, height=64)
		# Quit button
		self.button_quit = tk.Button(self.statusbar, text="New", fg="black", command=self.reset)
		self.button_quit.pack(side=tk.LEFT, in_=self.statusbar)
		# Save button
		self.button_save = tk.Button(self.statusbar, text="Save", fg="black", command=self.chessboard.save_to_file)
		self.button_save.pack(side=tk.LEFT, in_=self.statusbar)
		# Status of play
		self.label_status = tk.Label(self.statusbar, text="   White's turn  ", fg="black")
		self.label_status.pack(side=tk.LEFT, expand=0, in_=self.statusbar)
		# Agent 1
		self.button_a1 = tk.Button(self.statusbar, text="Agent 1", fg="black", command=self.move_a1)
		self.button_a1.pack(side=tk.LEFT, in_=self.statusbar)
		# Retain Move
		self.button_m = tk.Button(self.statusbar, text="My move", fg="black", command=self.no_change)
		self.button_m.pack(side=tk.LEFT, in_=self.statusbar)
		# Agent 2
		self.button_a2 = tk.Button(self.statusbar, text="Agent 2", fg="black", command=self.move_a2)
		self.button_a2.pack(side=tk.LEFT, in_=self.statusbar)
		# Quit button
		self.button_quit = tk.Button(self.statusbar, text="Quit", fg="black", command=self.parent.destroy)
		self.button_quit.pack(side=tk.RIGHT, in_=self.statusbar)
		self.statusbar.grid(row = 4, column = 0, columnspan = 4, sticky=tk.N+tk.E+tk.S+tk.W)

	def get_coords(self, cur_mov):
		result = []
		for i in cur_mov:
			result.append(self.CD[i])
		return result

	def click(self, event):
		if self.TURN == 'user':
			# Figure out which square we've clicked
			# Make copy of chessboard
			self.old_chessboard = copy.deepcopy(self.chessboard)

			col_size = row_size = event.widget.master.square_size

			current_column = event.x / col_size
			current_row = 7 - (event.y / row_size)

			position = self.chessboard.letter_notation((current_row, current_column))
			piece = self.chessboard[position]
			succ = False

			if self.selected_piece:
				succ = self.move(self.selected_piece[1], position)
				if succ:
					# Send the engine the move for internal chessboard update
					self.curr_move = self.selected_piece[1] + position
					self.curr_move = self.curr_move.lower()
					print('User move is {}'.format(self.curr_move))
					self.main_board.push(chess.Move.from_uci(self.curr_move))
					self.U_moves.append(str(self.curr_move).upper())
					self.TURN = 'suggest'
				self.selected_piece = None
				self.hilighted = None
				self.pieces = {}
				self.refresh()
				self.draw_pieces()

			self.hilight(position)
			self.refresh()

	def eng_response(self):
		# Perform engine move right after user move
		if ((len(self.chessboard.history)%2) > 0) and self.TURN == 'engine':
			self.engine_m.position(self.main_board)
			next_move = self.engine_m.go(movetime=2000)
			if next_move.bestmove == None:
				print(self.main_board)
				print('It returned None check again')
				next_move = self.engine_m.go(depth = 20)
			print('The computers move is {}'.format(next_move.bestmove))
			self.main_board.push(chess.Move.from_uci(str(next_move.bestmove.uci())[:4]))
			self.a1_board.push(chess.Move.from_uci(str(next_move.bestmove.uci())[:4]))
			self.a2_board.push(chess.Move.from_uci(str(next_move.bestmove.uci())[:4]))
			next_move = next_move.bestmove.uci()
			next_move = str(next_move).upper()[:4]
			self.move_history.append(next_move)
			self.B_moves.append(next_move)
			self.move(next_move[:2], next_move[2:])
			self.selected_piece = None
			self.hilighted = None
			self.pieces = {}
			self.refresh()
			self.draw_pieces()
			# Save current board state for agent suggestions
			self.save_board_state()
			full_image = Image.open('./Main_board_state.jpg')
			full_image.thumbnail((280,280), Image.ANTIALIAS)
			img = ImageTk.PhotoImage(full_image)
			self.parent.img = img
			self.canvas1.itemconfig(self.image_on_canvas1, image = img)
			self.canvas2.itemconfig(self.image_on_canvas2, image = img)
			self.TURN = 'user'

		elif ((len(self.chessboard.history)%2) > 0) and self.TURN == 'suggest':
			self.engine_1.position(self.a1_board)
			next_move = self.engine_1.go(movetime=2000)
			if next_move.bestmove == None:
				print(self.a1_board)
				print('It returned None check again')
				next_move = self.engine_1.go(depth = 20)
			self.a1_move = next_move.bestmove
			self.A1_moves.append(str(self.a1_move.uci()).upper())
			print('The agent 1 best move suggestion is {}'.format(next_move.bestmove))			
			full_image = Image.open('./Main_board_state.jpg')
			full_image.thumbnail((280,280), Image.ANTIALIAS)
			# draw = ImageDraw.Draw(full_image)
			points = self.get_coords(str(next_move.bestmove)) 
			# draw.line((points[0],points[1],points[2],points[3]), fill=128, width=5)
			self.ID1 = self.canvas1.create_line(points[0],points[1],points[2],points[3], arrow=tk.LAST, fill = 'red',width = 5)
			img1 = ImageTk.PhotoImage(full_image)
			self.parent.img1 = img1
			self.canvas1.itemconfig(self.image_on_canvas1, image = img1)

			self.engine_2.position(self.a2_board)
			next_move = self.engine_2.go(movetime=2000)
			if next_move.bestmove == None:
				print(self.a2_board)
				print('It returned None check again')
				next_move = self.engine_2.go(depth = 20)
			self.a2_move = next_move.bestmove
			self.A2_moves.append(str(self.a2_move.uci()).upper())
			print('The agent 2 best move suggestion is {}'.format(next_move.bestmove))	
			full_image = Image.open('./Main_board_state.jpg')
			full_image.thumbnail((280,280), Image.ANTIALIAS)
			# draw = ImageDraw.Draw(full_image)
			points = self.get_coords(str(next_move.bestmove)) 
			# draw.line((points[0],points[1],points[2],points[3]), fill=128, width=5)
			self.ID2 = self.canvas2.create_line(points[0],points[1],points[2],points[3], arrow=tk.LAST, fill = 'red',width = 5)
			img2 = ImageTk.PhotoImage(full_image)
			self.parent.img2 = img2
			self.canvas2.itemconfig(self.image_on_canvas2, image = img2)

			self.TURN = 'decide'
			self.label_status["text"] = 'Your decision here -->'
		self.parent.after(500,self.eng_response)			

	def move_a1(self):
		if self.TURN == 'decide':
			last_move = self.chessboard.history[-1]
			print('Last move is {}'.format(self.chessboard.history))
			del self.chessboard.history[-1]
			self.main_board.pop()
			self.main_board.push(self.a1_move)
			self.a1_board.push(self.a1_move)
			self.a2_board.push(self.a1_move)
			self.chessboard = self.old_chessboard
			next_move = str(self.a1_move).upper()
			print('Next move is {}'.format(next_move))
			self.move_history.append(next_move)
			self.W_moves.append(next_move)
			temp = self.move(next_move[:2], next_move[2:])
			print('Check this {}'.format(temp))
			self.selected_piece = None
			self.hilighted = None
			self.pieces = {}
			self.refresh()
			self.draw_pieces()
			# Save current board state for agent suggestions
			self.save_board_state()
			full_image = Image.open('./Main_board_state.jpg')
			full_image.thumbnail((280,280), Image.ANTIALIAS)
			img3 = ImageTk.PhotoImage(full_image)
			self.parent.img3 = img3
			self.canvas1.itemconfig(self.image_on_canvas1, image = img3)
			self.canvas2.itemconfig(self.image_on_canvas2, image = img3)
			self.TURN = 'engine'	
			self.canvas1.delete(self.ID1)
			self.canvas2.delete(self.ID2)		

	def move_a2(self):
		if self.TURN == 'decide':
			last_move = self.chessboard.history[-1]
			print('Last move is {}'.format(self.chessboard.history))
			del self.chessboard.history[-1]
			self.main_board.pop()
			self.main_board.push(self.a2_move)
			self.a1_board.push(self.a2_move)
			self.a2_board.push(self.a2_move)
			self.chessboard = self.old_chessboard
			next_move = str(self.a2_move).upper()
			self.move_history.append(next_move)
			self.W_moves.append(next_move)
			print('Next move is {}'.format(next_move))
			temp = self.move(next_move[:2], next_move[2:])
			print('Check this {}'.format(temp))
			self.selected_piece = None
			self.hilighted = None
			self.pieces = {}
			self.refresh()
			self.draw_pieces()
			# Save current board state for agent suggestions
			self.save_board_state()
			full_image = Image.open('./Main_board_state.jpg')
			full_image.thumbnail((280,280), Image.ANTIALIAS)
			img4 = ImageTk.PhotoImage(full_image)
			self.parent.img4 = img4
			self.canvas1.itemconfig(self.image_on_canvas1, image = img4)
			self.canvas2.itemconfig(self.image_on_canvas2, image = img4)
			self.TURN = 'engine'
			self.canvas1.delete(self.ID1)
			self.canvas2.delete(self.ID2)

	def no_change(self):
		if self.TURN == 'decide':
			self.a1_board.push(chess.Move.from_uci(self.curr_move))
			self.a2_board.push(chess.Move.from_uci(self.curr_move))
			tep = self.curr_move
			self.move_history.append(str(tep).upper())
			self.W_moves.append(str(tep).upper())
			# Save current board state for agent suggestions
			self.save_board_state()
			full_image = Image.open('./Main_board_state.jpg')
			full_image.thumbnail((280,280), Image.ANTIALIAS)
			img5 = ImageTk.PhotoImage(full_image)
			self.parent.img5 = img5
			self.canvas1.itemconfig(self.image_on_canvas1, image = img5)
			self.canvas2.itemconfig(self.image_on_canvas2, image = img5)
			self.TURN = 'engine'
			self.canvas1.delete(self.ID1)
			self.canvas2.delete(self.ID2)

	def move(self, p1, p2):
		# Before you perform a move check for checkmate
		if self.main_board.is_game_over():
			self.label_status["text"] = 'Game over'
		move_done = False
		piece = self.chessboard[p1]
		dest_piece = self.chessboard[p2]
		if dest_piece is None or dest_piece.color != piece.color:
			try:
				move_done = self.chessboard.move(p1, p2)
			except board.ChessError as error:
				self.label_status["text"] = error.__class__.__name__
			else:
				self.label_status["text"] = " " + piece.color.capitalize() +": "+ p1 + p2
		# Process the move history appropriately
		String_hist = ''
		for move_count, i in enumerate(self.move_history):
			if (move_count%2) > 0:
				self.comp.delete('1.0','end')
				self.comp.insert('end','\n Move history \n', 'big')
				String_hist = String_hist + ' {} {} {}  '.format(str(((move_count-1)/2)+1) + '.',self.move_history[move_count-1],i)
				self.comp.insert('end', String_hist, 'color')
		return move_done

	def hilight(self, pos):
		piece = self.chessboard[pos]
		if piece is not None and (piece.color == self.chessboard.player_turn):
			self.selected_piece = (self.chessboard[pos], pos)
			self.hilighted = map(self.chessboard.number_notation, (self.chessboard[pos].possible_moves(pos)))

	def addpiece(self, name, image, row=0, column=0):
		'''Add a piece to the playing board'''
		self.canvas.create_image(0,0, image=image, tags=(name, "piece"), anchor="c")
		self.placepiece(name, row, column)

	def placepiece(self, name, row, column):
		'''Place a piece at the given row/column'''
		self.pieces[name] = (row, column)
		x0 = (column * self.square_size) + int(self.square_size/2)
		y0 = ((7-row) * self.square_size) + int(self.square_size/2)
		self.canvas.coords(name, x0, y0)

	def refresh(self, event={}):
		'''Redraw the board'''
		if event:
			xsize = int((event.width-1) / self.columns)
			ysize = int((event.height-1) / self.rows)
			self.square_size = min(xsize, ysize)

		self.canvas.delete("square")
		color = self.color2
		for row in range(self.rows):
			color = self.color1 if color == self.color2 else self.color2
			for col in range(self.columns):
				x1 = (col * self.square_size)
				y1 = ((7-row) * self.square_size)
				x2 = x1 + self.square_size
				y2 = y1 + self.square_size
				if (self.selected is not None) and (row, col) == self.selected:
					self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="orange", tags="square")
				elif(self.hilighted is not None and (row, col) in self.hilighted):
					self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="spring green", tags="square")
				else:
					self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color, tags="square")
				color = self.color1 if color == self.color2 else self.color2
		for name in self.pieces:
			self.placepiece(name, self.pieces[name][0], self.pieces[name][1])
		self.canvas.tag_raise("piece")
		self.canvas.tag_lower("square")

	def draw_pieces(self):
		self.canvas.delete("piece")
		for coord, piece in self.chessboard.iteritems():
			x,y = self.chessboard.number_notation(coord)
			if piece is not None:
				filename = "img/%s%s.png" % (piece.color, piece.abbriviation.lower())
				piecename = "%s%s%s" % (piece.abbriviation, x, y)

				if(filename not in self.icons):
					self.icons[filename] = ImageTk.PhotoImage(file=filename, width=32, height=32)

				self.addpiece(piecename, self.icons[filename], x, y)
				self.placepiece(piecename, x, y)

	def reset(self):
		self.chessboard.load(board.FEN_STARTING)
		self.refresh()
		self.draw_pieces()
		self.refresh()

	def save_board_state(self):
		ps = self.canvas.postscript(colormode='color')
		img = Image.open(io.BytesIO(ps.encode('utf-8')))
		img.save('./Main_board_state.jpg')

def get_info(state, a1, a2, agent_num):
	if agent_num == 1:
		en_num = 2
	else:
		en_num = 1

	if state[-1] == 'B':
		str3 = ' Consider both agent suggestions for the best outcome.'
	else:
		str3 = ' Consider my suggestions alone for the best outcome.'

	if (state[-2] == 'F') and (a1>a2):
		str2 =  ' My competence is higher than agent {}.'.format(en_num) + str3
	elif (state[-2] == 'F') and (a1<a2):
		str2 =  ' My competence is lower than agent {}.'.format(en_num) + str3
	elif (state[-2] == 'NF') and (a1>a2):
		str2 =  ' My competence is higher than agent {}.'.format(en_num) + str3
	elif (state[-2] == 'NF') and (a1<a2):
		str2 =  ' My competence is higher than agent {}.'.format(en_num) + str3

	if (state[-3] == 'H'):
		str1 = 'I am agent {} with ELO rating {}.'.format(agent_num,a1) + str2
	elif (state[-3] == 'NH') and (state[-2] == 'F'):
		str1 = 'I am agent {} with ELO rating {}.'.format(agent_num,int(a1+((a2-a1)*0.9))) + str2
	elif (state[-3] == 'NH') and (state[-2] == 'NF'):
		if a1>a2:
			str1 = 'I am agent {} with ELO rating {}.'.format(agent_num,int(a1+((a2-a1)*0.9))) + str2
		else:
			str1 = 'I am agent {} with ELO rating {}.'.format(agent_num,int(a2+((a2-a1)*0.9))) + str2

	return str1

def get_agent_information(ELO):
	user_elo = ELO
	const_dir = '/home/adi/Documents/Michigan_courses/EECS598_HCI/Final_project/Chess_stockfish/'
	# Build Agent dictionary
	engines = ['stockfish_1','stockfish_2','stockfish_3','stockfish_5','stockfish_6','stockfish_7','stockfish_8','stockfish_9']
	elo_ratings = [3113,3079,3097,3194,3226,3246,3301,3369]
	engine_path = [const_dir + 'stockfish_1/Linux/stockfish-191-32-ja',
				   const_dir + 'stockfish_2/Linux/stockfish-231-64-ja',
				   const_dir + 'stockfish_3/Linux/stockfish-3-64-ja',
				   const_dir + 'stockfish_5/Linux/stockfish_14053109_x64',
				   const_dir + 'stockfish_6/Linux/stockfish_6_x64',
				   const_dir + 'stockfish_7/Linux/stockfish7x64',
				   const_dir + 'stockfish_8/Linux/stockfish_8_x64',
				   const_dir + 'stockfish_9/Linux/stockfish_9_64']
   	idx = (np.abs(np.asarray(elo_ratings)-user_elo)).argmin()
   	comp_elo = elo_ratings[idx]
   	m_agent_path = engine_path[idx]
   	elo_ratings_new = elo_ratings
   	del elo_ratings_new[idx]
   	idx_n = (np.abs(np.asarray(elo_ratings_new)-user_elo)).argmin()
	idx = elo_ratings.index(elo_ratings_new[idx_n])
	agent1_path = engine_path[idx]	
	a1_rating = elo_ratings[idx]

   	del elo_ratings_new[idx]
   	idx_n = (np.abs(np.asarray(elo_ratings_new)-user_elo)).argmin()
	idx = elo_ratings.index(elo_ratings_new[idx_n])
	agent2_path = engine_path[idx]
	a2_rating = elo_ratings[idx]

	Trust_options = [['H','F','B'],['H','F','NB'],['H','NF','B'],['H','NF','NB'],['NH','F','B'],['NH','F','NB'],['NH','NF','B'],['NH','NF','NB']]
	agent1_state = random.choice(Trust_options)
	agent2_state = random.choice(Trust_options)

	#Agent 1 information
	agent1_info = get_info(agent1_state,a1_rating,a2_rating,1)
	agent2_info = get_info(agent2_state,a2_rating,a1_rating,2)

	print(agent1_state)
	print(a1_rating)
	print(agent1_info)
	print(agent2_state)
	print(a2_rating)
	print(agent2_info)
	information_vector = [m_agent_path,agent1_path, agent2_path, agent1_info, agent2_info, a1_rating, a2_rating, agent1_state, agent2_state, comp_elo]
	return information_vector

def display(chessboard):
	root1 = tk.Tk()
	root1.title('ELO rating')
	# Get ELO rating of the user
	elo_page = ELO_page(root1)
	root1.mainloop()

	print('The user ELO rating is {}'.format(elo_page.user_elo_rating))
	agent_info = get_agent_information(int(elo_page.user_elo_rating))

	Info_dict = {}
	Info_dict['Name'] = elo_page.user_name
	Info_dict['ELO rating'] = elo_page.user_elo_rating
	Info_dict['Agent 1 rating'] = agent_info[5]
	Info_dict['Agent 2 rating'] = agent_info[6]
	Info_dict['Agent 1 state'] = agent_info[7]
	Info_dict['Agent 2 state'] = agent_info[8]
	Info_dict['Agent 1 info'] = agent_info[3]
	Info_dict['Agent 2 info'] = agent_info[4]

	User_ID = 1
	hf = h5py.File('User_{}.h5'.format(User_ID),'w')
	hf.create_dataset('Information', data=str(Info_dict))

	root = tk.Tk()
	root.title("Multi-agent Python Chess")
	# Make a copy of the initial board state
	if os.path.exists('./Main_board_state.jpg'):
 		os.remove('./Main_board_state.jpg')
	shutil.copy('./Init_state.jpg', './Main_board_state.jpg')
	# Choice of what engines to choose and display will be made here
	# Opponent
	engm = chess.uci.popen_engine(agent_info[0])
	engm.uci()
	main_board = chess.Board()
	main_board.castling_rights = False
	# Agent 1
	eng1 = chess.uci.popen_engine(agent_info[1])
	eng1.uci()
	a1_board = chess.Board()
	a1_board.castling_rights = False
	# Agent 2
	eng2 = chess.uci.popen_engine(agent_info[2])
	eng2.uci()
	a2_board = chess.Board()
	a2_board.castling_rights = False

	gui = BoardGuiTk(root, chessboard, engm, main_board, eng1, a1_board, eng2, a2_board, agent_info[3], agent_info[4],elo_page.user_elo_rating, agent_info[9])
	gui.pack(side="top", fill="both", expand="true", padx=4, pady=4)
	gui.draw_pieces()
	gui.eng_response()
	#root.resizable(0,0)
	root.mainloop()
	gui.DB.extend((gui.W_moves,gui.B_moves,gui.A1_moves,gui.A2_moves,gui.U_moves))
	hf = h5py.File('User_{}.h5'.format(User_ID),'a')
	hf.create_dataset('White_moves', data=gui.DB[0])
	hf.create_dataset('Black_moves', data=gui.DB[1])
	hf.create_dataset('A1_moves', data=gui.DB[2])
	hf.create_dataset('A2_moves', data=gui.DB[3])
	hf.create_dataset('User_moves', data=gui.DB[4])
if __name__ == "__main__":
	display()
