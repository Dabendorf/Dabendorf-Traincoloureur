import numpy
import pygame
import math
import json
import ndjson
from collections import defaultdict

stations = dict()

class Graph:
	def __init__(self):
		self.nodes = set()
		self.edges = defaultdict(list)
		self.distances = {}

	def add_node(self, value):
		self.nodes.add(value)

	def add_edge(self, from_node, to_node, distance):
		self.edges[from_node].append(to_node)
		self.edges[to_node].append(from_node)
		self.distances[(from_node, to_node)] = distance
		self.distances[(to_node, from_node)] = distance


def dijsktra(graph, initial):
	visited = {initial: 0}
	path = {}

	nodes = set(graph.nodes)

	while nodes: 
		min_node = None
		for node in nodes:
			if node in visited:
				if min_node is None:
					min_node = node
				elif visited[node] < visited[min_node]:
					min_node = node

		if min_node is None:
			break

		nodes.remove(min_node)
		current_weight = visited[min_node]

		for edge in graph.edges[min_node]:
			weight = current_weight + graph.distances[(min_node, edge)]
			if edge not in visited or weight < visited[edge]:
				visited[edge] = weight
				path[edge] = min_node

	return visited, path


def colour_gradient_from_distance(distance_array):
	"""This function calculates the color gradient of an array of distances
	Parameter:
		distance_array - an array of floats
	============================================================================
	Returns:
		an array of colours with the format (r,g,b) where r,g and b are between 0 and 255
	============================================================================
	"""
	max = numpy.amax(distance_array)
	min = numpy.amin(distance_array)
	rangemm = max - min
	length = len(distance_array)
	colours = [None] * length
	print("test")
	for i in range(length):
		relative_colouring = (int((distance_array[i] - min) * 255 / rangemm))#linear colour-scaling
		relative_colouring = numpy.sqrt(relative_colouring)*16
		if distance_array[i] != 0:
			colours[i] = (relative_colouring, 255 - relative_colouring, 0)
		else:
			colours[i] = (0, 0, 255)
	return colours

def colour_gradient_from_positions(positions, root_position):
	"""This function calculates the color gradient of an array of positions
		given a root position from which the distances are to be measured
		Parameter:
			positions - an array of tuples giving positions as tuples
			root_position - a tuple
		============================================================================
		Returns:
			an array of colours with the format (r,g,b) where r,g and b are between 0 and 255
			going from green to red the farther the corresponding position is away from root
		============================================================================
	"""
	distances = []
	for position in positions:
		distances.append(
			numpy.sqrt(
				((position[0] - root_position[0]) ** 2)
				+ (position[1] - root_position[1]) ** 2
			)
		)
	return colour_gradient_from_distance(distances)



def gps_to_x_y(
	gps_values, screen_width, screen_height, off_screen_value=None, draw_border=20
):
	"""This function calculates the relative position of GPS-coordinates on a given screen
	Parameter:
		gps_values - an array of tuples (longnitude, latitude)
		!!!For the moment this is likely to only work for positive GPS-Values!!!
		screen_width - int
		screen_height - int
		off_screen_value - a gps tuple that needs to be comverted but
		not considered whe defining the dimensions
		draw_border - int that defines the width of the border that is left empty
		and not considered for calculations
	============================================================================
	Returns:
		an array of tuples (x,y) of integers assuming that top left is (0,0).
		the tuples range from (0,0) to (screen_width, screen_height)

		a tuple that is the converted coordinates of the off_screen_value
	============================================================================
	"""
	max_x, max_y = numpy.amax(gps_values, 0)
	min_x, min_y = numpy.amin(gps_values, 0)
	print(str(max_x)+" : "+str(min_x))
	print(str(max_y)+" : "+ str(min_y))
	print(draw_border)
	range_x = abs(max_x - min_x)
	range_y = abs(max_y - min_y)
	bordered_width = screen_width - 2 * draw_border
	bordered_height = screen_height - 2 * draw_border
	if off_screen_value == None:
		positions = [None] * len(gps_values)
		# We assume, that (0,0) is the top left of the screen
		# GPS rechts und oben wird größer bei uns recht und unten wird größer
		for i in range(len(gps_values)):	

				positions[i] = (
					int((bordered_width * (gps_values[i][0] - min_x)) / range_x)
					+ draw_border,
					bordered_height
					- int((bordered_height * (gps_values[i][1] - min_y)) / range_y)
					+ draw_border,
					)
		print("Es wurde kein offscreenvalue angegeben.")
		return positions
	else:
		positions = [None] * len(gps_values)
		# We assume, that (0,0) is the top left of the screen
		# GPS rechts und oben wird größer bei uns recht und unten wird größer
		for i in range(len(gps_values)):
			positions[i] = (
				int((bordered_width * (gps_values[i][0] - min_x)) / range_x)
				+ draw_border,
				bordered_height
				- int((bordered_height * (gps_values[i][1] - min_y)) / range_y)
				+ draw_border,
			)

		print("Es wurde ein offscreenvalue angegeben.")
		return (
			positions,
			(
				int((bordered_width * (off_screen_value[0] - min_x) )/ range_x)
				+ draw_border,
				bordered_height
				- int((bordered_height * (off_screen_value[1] - min_y)) / range_y)
				+ draw_border,
			),
		)


def draw_euclidean_distance_map(positions_gps, root_gps, display_width, display_height):
	"""This function draws a distance map using pygame
		Parameter:
			positions_gps - an array of tuples giving positions as gps_data
			!!!Proably only for positive coordinates!!!
			root_gps - a tuple of gps data for the root position
			display_width - int
			display_height - int
		============================================================================
	"""
	positions_x_y, root_x_y = gps_to_x_y(
		positions_gps, display_width, display_height, root_gps
	)
	colours = colour_gradient_from_positions(positions_x_y, root_x_y)
	pygame.init()
	screen = pygame.display.set_mode((display_width, display_height))
	running = True
	for i in range(len(positions_x_y)):
		pygame.draw.circle(screen, colours[i], positions_x_y[i], 1)
	pygame.display.flip()
	while running:
		# disposes of all events and possibly closes the programm
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False


def draw_distance_map(positions_gps, distances, display_width, display_height, point_size=1):
	"""This function draws a distance map using pygame
		Parameter:
			positions_gps - an array of tuples giving positions as gps_data
			!!!Proably only for positive coordinates!!!
			distances - an array fo distances according to the distance of the
			corrosponding position to something in some metric
			display_width - int
			display_height - int
		============================================================================
	"""
	positions_x_y = gps_to_x_y(positions_gps, display_width, display_height)
	colours = colour_gradient_from_distance(distances)
	pygame.init()
	screen = pygame.display.set_mode((display_width, display_height))
	pygame.display.set_caption('Berlin aus Sicht der Metropole')
	running = True
	for i in range(len(positions_x_y)):
		pygame.draw.circle(screen, colours[i], positions_x_y[i], point_size)
	pygame.display.flip()

	while running:
		# disposes of all events and possibly closes the programm
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

def getVBBdata():
	global stations
	g = Graph()
	with open('nodes.ndjson') as f:
		dataSta = ndjson.load(f)

	# convert to and from objects
	textSta = ndjson.dumps(dataSta)
	dataSta = ndjson.loads(textSta)
	for i in dataSta:
		#tupel = str(i['metadata']['x'])+","+str(i['metadata']['y'])
		x = float(i['metadata']['longitude'])
		y = float(i['metadata']['latitude'])
		idSt = str(i['id'])
		g.add_node(idSt)
		stations[idSt] = (x,y)
		#g.add_node(tupel)

	with open('edges.ndjson') as f:
		dataDist = ndjson.load(f)

	# convert to and from objects
	textDist = ndjson.dumps(dataDist)
	dataDist = ndjson.loads(textDist)
	for i in dataDist:
		stationA = str(i['source'])
		stationB = str(i['target'])
		distance = int(i['metadata']['time'])
		g.add_edge(stationA, stationB, distance)

	return dijsktra(g, '900000245024') #Nummer der Dabendorf Node

def main():
	graphVBB = getVBBdata()
	stations_with_distances = graphVBB[0]
	
	positions = []
	distances = []

	maxX = 13.908894
	minX = 13.067187
	maxY = 52.754362
	minY = 52.227264
	for i in stations_with_distances:
		if stations[i][0] >= minX and stations[i][0] <= maxX and stations[i][1] >= minY and stations[i][1] <= maxY:
			distances.append(stations_with_distances[i])
			positions.append(stations[i])

	width = 2400
	height = 1400
	point_size = 5
	draw_distance_map(positions, distances, width, height, point_size)
	testarray = [(1,1),(2,2),(3,3)]
	#draw_euclidean_distance_map(testarray, (0, 0), width, height)
	
	"""
	num1 = 100
	num2 = 20
	testarray = [None] * (num1 * num2)
	val = 0
	for i in range(num1):
		for j in range(num2):
			testarray[val] = (i, j)
			val = val + 1
	width = 900
	height = 900
	draw_euclidean_distance_map(testarray, (0, 0), width, height)
	"""

if __name__ == "__main__":
	main()

