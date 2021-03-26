from __future__ import absolute_import, division, print_function
import copy
import random
MOVES = {0: 'up', 1: 'left', 2: 'down', 3: 'right'}

class Gametree:
	"""main class for the AI"""
	# Hint: Two operations are important. Grow a game tree, and then compute minimax score.
	# Hint: To grow a tree, you need to simulate the game one step.
	# Hint: Think about the difference between your move and the computer's move.
	def __init__(self, root_state, depth_of_tree, current_score):
		self.depth = depth_of_tree
		self.ttlPoints = current_score
		self.rootNode = Node(copy.deepcopy(root_state), 0, self.ttlPoints)
	# function to grow the game tree starting from root node
	def growTree(self):
		root = self.rootNode
		# the depth 1 of the tree, chance players
		for m in range(0, 4):
			sim = Simulator()
			sim.total_points = self.ttlPoints
			sim.tileMatrix = copy.deepcopy(root.state)
			sim.move(m)
			# if it is a unique move
			if sim.tileMatrix != root.state:
				chanceP = Node(sim.tileMatrix, 1, sim.total_points)
				chanceP.direct = m
				root.children.append(chanceP)
		# the depth 2 of the tree, max players
		for mc in root.children:
			sim = Simulator()
			sim.total_points = mc.points
			sim.tileMatrix = copy.deepcopy(mc.state)
			empty = []
			# empty tiles in the grid
			for i in range(0, 4):
				for j in range(0, 4):
					if sim.tileMatrix[i][j] == 0:
						empty.append((i, j))
			# for each empty tile, add node
			for t in empty:
				mc_mat = copy.deepcopy(sim.tileMatrix)
				mc_mat[t[0]][t[1]] = 2
				mc.children.append(Node(mc_mat, 0, sim.total_points))
			# the depth 3 of the tree, chance players
			for cc in mc.children:
				for d in range(0, 4):
					ssim = Simulator()
					ssim.total_points = cc.points
					ssim.tileMatrix = copy.deepcopy(cc.state)
					ssim.move(d)
					# if it is a unique move
					if ssim.tileMatrix != cc.state:
						cchanceP = Node(ssim.tileMatrix, 1, ssim.total_points)
						cchanceP.direct = d
						cc.children.append(cchanceP)
	# expectimax for computing best move
	def expectimax(self, node):
		# if leaf node
		if not node.children:
			return self.payoff(node)
		# if max player
		elif node.player == 0:
			value = float("-inf")
			for n in node.children:
				value = max(value, self.expectimax(n))
			return value
		# if chance player
		elif node.player == 1:
			value = 0
			for n in node.children:
				value = value + self.expectimax(n) * (1 / len(node.children))
			return value

	# function that returns the leaf node's payoff
	def payoff(self, node):
		#weight = [[4**3, 4**2, 4, 1], [4**4, 4**5, 4**6, 4**7], [4**11, 4**10, 4**9, 4**8], [4**12, 4**13, 4**14, 4**15]]
		weight = [[-3, -2, 3, 6.5], [-3.5, -1.8, 1, 7], [-3.7, -1.5, 0.7, 8], [-3.8, -0.5, 0.5, 100]]
		neighbor = [(0,-1),(-1,0),(0,1),(1,0)]
		score = 0
		penalty = 0
		for i in range(0, 4):
			for j in range(0, 4):
				score += (weight[i][j] * node.state[i][j])
				for n in neighbor:
					if i + n[0] in range(0, 4) and j + n[1] in range(0, 4):
						penalty += abs(node.state[i][j] - node.state[i + n[0]][j + n[1]])
		# add the total points of current state
		score += node.points
		score -= penalty
		return score

	# function to return best decision to game
	def compute_decision(self):
		optimal_move = -1
		# grow the tree
		self.growTree()
		# after growing the tree, run expectimax algorithm to find optimal move
		highest = self.expectimax(self.rootNode)
		# get the move of the highest node
		for n in self.rootNode.children:
			if self.expectimax(n) == highest:
				optimal_move = n.direct
				break
		#change this return value when you have implemented the function
		return optimal_move

class Node:
	def __init__(self, state, player, points):
		self.children = []
		self.state = state
		self.player = player
		self.direct = -1
		self.points = points

class Simulator:
	def __init__(self):
		self.total_points = 0
		self.default_tile = 2
		self.board_size = 4
		#pygame.init()
		#self.surface = pygame.display.set_mode((400, 500), 0, 32)
		#pygame.display.set_caption("2048")
		#self.myfont = pygame.font.SysFont("arial", 40)
		#self.scorefont = pygame.font.SysFont("arial", 30)
		self.tileMatrix = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
		self.undoMat = []
	def loop(self, fromLoaded = False):
		auto = False
		if not fromLoaded:
			self.placeRandomTile()
			self.placeRandomTile()
		self.printMatrix()
		while True:
			if auto:
				if self.checkIfCanGo():
					#Hint: Check the use of deepcopy
					ai = Gametree(copy.deepcopy(self.tileMatrix), 3, self.total_points)
					direction = ai.compute_decision()
					self.move(direction)
				else:
					auto = False
					self.printGameOver()
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					sys.exit()
				if event.type == KEYDOWN and event.key == K_RETURN:
					auto = not auto
				if self.checkIfCanGo():
					if event.type == KEYDOWN:
						if self.isArrow(event.key):
							direction = self.getRotations(event.key)
							self.move(direction)
				else:
					self.printGameOver()
				if event.type == KEYDOWN:
					if event.key == pygame.K_r:
						self.reset()
					if 50 < event.key and 56 > event.key:
						self.board_size = event.key - 48
						self.reset()
					if event.key == pygame.K_s:
						self.saveGameState()
					elif event.key == pygame.K_l:
						self.loadGameState()
					elif event.key == pygame.K_u:
						self.undo()
			pygame.display.update()
	def move(self, direction):
		#self.addToUndo()
		for i in range(0, direction):
			self.rotateMatrixClockwise()
		if self.canMove():
			self.moveTiles()
			self.mergeTiles()
		#	self.placeRandomTile()
		for j in range(0, (4 - direction) % 4):
			self.rotateMatrixClockwise()
		#self.printMatrix()
	def printMatrix(self):
		self.surface.fill(BLACK)
		for i in range(0, self.board_size):
			for j in range(0, self.board_size):
				pygame.draw.rect(self.surface, COLORS[self.tileMatrix[i][j]],
	                (i*(400/self.board_size), j*(400/self.board_size) + 100, 400/self.board_size, 400/self.board_size))
				label = self.myfont.render(str(self.tileMatrix[i][j]), 1, (255,255,255))
				label2 = self.scorefont.render("Score:" + str(self.total_points), 1, (255, 255, 255))
				self.surface.blit(label, (i*(400/self.board_size) + 30, j*(400/self.board_size) + 130))
				self.surface.blit(label2, (10, 20))
	def printGameOver(self):
		self.surface.fill(BLACK)
		label = self.scorefont.render("Game Over!", 1, (255,255,255))
		label2 = self.scorefont.render("Score:" + str(self.total_points), 1, (255,255,255))
		label3 = self.myfont.render("Press r to restart!", 1, (255,255,255))
		self.surface.blit(label, (50, 100))
		self.surface.blit(label2, (50, 200))
		self.surface.blit(label3, (50, 300))
	def placeRandomTile(self):
		while True:
			i = random.randint(0,self.board_size-1)
			j = random.randint(0,self.board_size-1)
			if self.tileMatrix[i][j] == 0:
				break
		self.tileMatrix[i][j] = 2
	def moveTiles(self):
		tm = self.tileMatrix
		for i in range(0, self.board_size):
			for j in range(0, self.board_size - 1):
				while tm[i][j] == 0 and sum(tm[i][j:]) > 0:
					for k in range(j, self.board_size - 1):
						tm[i][k] = tm[i][k + 1]
					tm[i][self.board_size - 1] = 0
	def mergeTiles(self):
		tm = self.tileMatrix
		for i in range(0, self.board_size):
			for k in range(0, self.board_size - 1):
				if tm[i][k] == tm[i][k + 1] and tm[i][k] != 0:
					tm[i][k] = tm[i][k] * 2
					tm[i][k + 1] = 0
					self.total_points += tm[i][k]
					self.moveTiles()
	def checkIfCanGo(self):
		tm = self.tileMatrix
		for i in range(0, self.board_size ** 2):
			if tm[int(i / self.board_size)][i % self.board_size] == 0:
				return True
		for i in range(0, self.board_size):
			for j in range(0, self.board_size - 1):
				if tm[i][j] == tm[i][j + 1]:
					return True
				elif tm[j][i] == tm[j + 1][i]:
					return True
		return False
	def reset(self):
		self.total_points = 0
		self.surface.fill(BLACK)
		self.tileMatrix = [[0 for i in range(self.board_size)] for j in range(self.board_size)]
		self.loop()
	def canMove(self):
		tm = self.tileMatrix
		for i in range(0, self.board_size):
			for j in range(1, self.board_size):
				if tm[i][j-1] == 0 and tm[i][j] > 0:
					return True
				elif (tm[i][j-1] == tm[i][j]) and tm[i][j-1] != 0:
					return True
		return False
	def saveGameState(self):
		f = open("savedata", "w")
		line1 = " ".join([str(self.tileMatrix[int(x / self.board_size)][x % self.board_size])
	                    for x in range(0, self.board_size**2)])
		f.write(line1 + "\n")
		f.write(str(self.board_size)  + "\n")
		f.write(str(self.total_points))
		f.close()
	def loadGameState(self):
		f = open("savedata", "r")
		m = (f.readline()).split(' ', self.board_size ** 2)
		self.board_size = int(f.readline())
		self.total_points = int(f.readline())
		for i in range(0, self.board_size ** 2):
			self.tileMatrix[int(i / self.board_size)][i % self.board_size] = int(m[i])
		f.close()
		self.loop(True)
	def rotateMatrixClockwise(self):
		tm = self.tileMatrix
		for i in range(0, int(self.board_size/2)):
			for k in range(i, self.board_size- i - 1):
				temp1 = tm[i][k]
				temp2 = tm[self.board_size - 1 - k][i]
				temp3 = tm[self.board_size - 1 - i][self.board_size - 1 - k]
				temp4 = tm[k][self.board_size - 1 - i]
				tm[self.board_size - 1 - k][i] = temp1
				tm[self.board_size - 1 - i][self.board_size - 1 - k] = temp2
				tm[k][self.board_size - 1 - i] = temp3
				tm[i][k] = temp4
	def isArrow(self, k):
		return(k == pygame.K_UP or k == pygame.K_DOWN or k == pygame.K_LEFT or k == pygame.K_RIGHT)
	def getRotations(self, k):
		if k == pygame.K_UP:
			return 0
		elif k == pygame.K_DOWN:
			return 2
		elif k == pygame.K_LEFT:
			return 1
		elif k == pygame.K_RIGHT:
			return 3
	def convertToLinearMatrix(self):
		m = []
		for i in range(0, self.board_size ** 2):
			m.append(self.tileMatrix[int(i / self.board_size)][i % self.board_size])
		m.append(self.total_points)
		return m
	def addToUndo(self):
		self.undoMat.append(self.convertToLinearMatrix())
	def undo(self):
		if len(self.undoMat) > 0:
			m = self.undoMat.pop()
			for i in range(0, self.board_size ** 2):
				self.tileMatrix[int(i / self.board_size)][i % self.board_size] = m[i]
			self.total_points = m[self.board_size ** 2]
			self.printMatrix()
