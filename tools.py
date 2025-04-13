import colorsys
import json
import math
import os
import sys
from collections import defaultdict
import sys
import os
import colorsys
from enum import Enum
import pandas as pd
import numpy as np

import ndjson
import numpy
import pygame
from argparse import ArgumentParser

stations = dict()
station_types = dict()
global spectre_size


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


def hsv2rgb(h, s, v):
	return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))


def colour_gradient_from_distance(distance_array):
	global spectre_size	# number of iterations around rainbow, preferibly < 1.0

	max_dist = numpy.amax(distance_array)
	min_dist = numpy.amin(distance_array)
	rangemm = max_dist - min_dist
	length = len(distance_array)
	colours = [None] * length
	print("Dabendorf dankt")

	for i in range(length):
		if distance_array[i] != 0:
			start = 0 # 102.8
			hue = ((distance_array[i] - min_dist) / rangemm + (start / 360)) % 1 * spectre_size

			colours[i] = hsv2rgb(hue, 1.0, 1.0)
		else:
			colours[i] = (51, 178, 0)  # DORgreen, 33b200
	return colours


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
	#print(str(max_x)+" : "+str(min_x))
	#print(str(max_y)+" : " + str(min_y))
	# print(draw_border)
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
		#print("Es wurde keine Offscreen-Value angegeben.")
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

		#print("Es wurde keine Offscreen-Value angegeben.")
		return (
			positions,
			(
				int((bordered_width * (off_screen_value[0] - min_x)) / range_x)
				+ draw_border,
				bordered_height
				- int((bordered_height *
					(off_screen_value[1] - min_y)) / range_y)
				+ draw_border,
			),
		)



def draw_distance_map(positions_gps, distances, station_types_arr, display_width, display_height, point_size=1, save_as='screenshot'):
	"""This function draws a distance map using pygame
			Parameter:
				positions_gps - an array of tuples giving positions as gps_data
				!!!Probably only for positive coordinates!!! (which doesn't matter for European data)
				distances - an array fo distances according to the distance of the
				corrosponding position to something in some metric
				display_width - int
				display_height - int
	============================================================================
	"""
	positions_x_y = gps_to_x_y(positions_gps, display_width, display_height)
	colours = colour_gradient_from_distance(distances)
	try:
		os.environ["DISPLAY"]
	except:
		os.environ["SDL_VIDEODRIVER"] = "dummy"
	pygame.init()
	screen = pygame.display.set_mode((display_width, display_height))
	pygame.display.set_caption('Berlin aus Sicht der Metropole')
	running = True
	offset = (0, 0, 0)
	for i in range(len(positions_x_y)):
		if distances[i] == 0:
			# Red cross for the start point
			pygame.draw.line(screen, (255, 0, 0), 
								(positions_x_y[i][0] - 5, positions_x_y[i][1] - 5), 
								(positions_x_y[i][0] + 5, positions_x_y[i][1] + 5), 2)
			pygame.draw.line(screen, (255, 0, 0), 
								(positions_x_y[i][0] - 5, positions_x_y[i][1] + 5), 
								(positions_x_y[i][0] + 5, positions_x_y[i][1] - 5), 2)
		elif station_types_arr[i] == 1:
			pygame.draw.circle(
				screen, (255,255,255), positions_x_y[i], point_size[0]+offset[0])
			pygame.draw.circle(
				screen, colours[i], positions_x_y[i], point_size[0])			
		elif station_types_arr[i] == 2:
			pygame.draw.circle(
				screen, (255,255,255), positions_x_y[i], point_size[1]+offset[0])
			pygame.draw.circle(
				screen, colours[i], positions_x_y[i], point_size[1])
		else:
			pygame.draw.circle(
				screen, (255,255,255), positions_x_y[i], point_size[2]+offset[0])
			pygame.draw.circle(
				screen, colours[i], positions_x_y[i], point_size[2])
	pygame.display.flip()
	pygame.image.save(screen, save_as + '.png')
	
	print('Press q to terminate the programme')

	while running:
		# disposes of all events and possibly closes the programm
		for event in pygame.event.get():
			keys = pygame.key.get_pressed()
			if event.type == pygame.QUIT or keys[pygame.K_q] or keys[pygame.K_ESCAPE]:
				running = False
				pygame.display.quit()
				pygame.quit()


def get_vbb_data(centre):
	global stations
	global station_types
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
		stations[idSt] = (x, y)
		# g.add_node(tupel)

	with open('edges.ndjson') as f:
		dataDist = ndjson.load(f)

	# convert to and from objects
	textDist = ndjson.dumps(dataDist)
	dataDist = ndjson.loads(textDist)

	for i in dataDist:
		stationA = str(i['source'])
		stationB = str(i['target'])
		distance = int(i['metadata']['time'])
		line_type = i['relation']
		
		"""if line.startswith('RB') or line.startswith('RB'):
			station_types[stationA] = 1
			station_types[stationB] = 1
		elif line.startswith('U') or line.startswith('S'):
			if stationA in station_types:
				if station_types[stationA] > 1:
					station_types[stationA] = 2
			else:
				station_types[stationA] = 2
			if stationB in station_types:
				if station_types[stationB] > 1:
					station_types[stationB] = 2
			else:
				station_types[stationB] = 2
		else:
			if stationA in station_types:
				if station_types[stationA] > 2:
					station_types[stationA] = 3
			else:
				station_types[stationA] = 3

			if stationB in station_types:
				if station_types[stationB] > 2:
					station_types[stationB] = 3
			else:
				station_types[stationB] = 3"""
		"""
		100 <= x <= 199 => train
		200 <= x <= 299 => bus
		700 <= x <= 799 => bus
		900 <= x <= 999 => tramway
		1000 <= x <= 1099 => ferry
		1300 <= x <= 1399 => funicular
		TODO find better concept https://developers.google.com/transit/gtfs/reference/extended-route-types
		"""
		if line_type == "train":
			station_types[stationA] = 1
			station_types[stationB] = 1
		elif line_type == "tramway" or line_type == "ferry" or line_type == "funicular":
			if stationA in station_types:
				if station_types[stationA] > 1:
					station_types[stationA] = 2
			else:
				station_types[stationA] = 2
			if stationB in station_types:
				if station_types[stationB] > 1:
					station_types[stationB] = 2
			else:
				station_types[stationB] = 2
		else:
			if stationA in station_types:
				if station_types[stationA] > 2:
					station_types[stationA] = 3
			else:
				station_types[stationA] = 3

			if stationB in station_types:
				if station_types[stationB] > 2:
					station_types[stationB] = 3
			else:
				station_types[stationB] = 3

		g.add_edge(stationA, stationB, distance)

	return dijsktra(g, centre)  # Station name of Dabendorf node: 900000245024

def parse_args():
	parser = ArgumentParser(description="Python3 programme which visualises\
										public transport distances in Berlin.")

	parser.add_argument("-s", "--start", default="dabendorf", type=str,
						help="Changes the start station from where distances are calculated")
	parser.add_argument("-p", "--size", default="7,5,2", type=str,
						help="Alters the size of the stations on the map; \
							\nRequires three comma seperated arguments: \
								\nRE,S/U,Bus/Tram")
	parser.add_argument("-height", "--height", default="1000", type=int,
						help="Height of the programme window")
	parser.add_argument("-b", "--boundary", default="berlin", type=str,
						help="Boundary box for the shown geographical area; \
							\nFormat: min_x,max_x,min_y,min_y (x=longitude, y=latitude); \
							\nDefault: 13.067187,13.908894,52.227264,52.754362 (Berlin ABC); \
							\nParams also possible: berlin, abc, brandenburg, brb, vbb")
	parser.add_argument("-i", "--iterations", default="0.8", type=float,
						help="Describes the number of iterations around the default rainbow scale. Default 0.8")

	return parser.parse_args()


def main():
	args = parse_args()
	global station_types

	# stations_dict = pd.read_csv('shortcuts.csv', header=0, index_col=0, squeeze=True).to_dict()
	stations_dict = pd.read_csv('shortcuts.csv', header=0, index_col=0).squeeze().to_dict()

	input_station = str(stations_dict[args.start])

	global spectre_size
	spectre_size = args.iterations

	boundary_str = args.boundary
	boundary_edges = boundary_str.split(",")

	sizes_str = args.size
	sizes = sizes_str.split(",")

	if len(sizes) != 3:
		print('\nSize parameter requires three integer\
				\nRE,S/U,Bus/Tram')
		sys.exit(0)

	if boundary_str == "berlin" or boundary_str == "abc":
		min_x = 13.067187
		max_x = 13.908894
		min_y = 52.227264
		max_y = 52.754362
	elif boundary_str == "brandenburg" or boundary_str == "brb" or boundary_str == "vbb":
		min_x = 11.268720
		max_x = 14.765748
		min_y = 51.359064
		max_y = 53.559119
	elif len(boundary_edges) != 4:
		print("\nBoundary parameter requires four integer\
				\nFormat: min_x,max_x,min_y,min_y (x=longitude, y=latitude)")
		sys.exit(0)
	else:
		min_x = float(boundary_edges[0])
		max_x = float(boundary_edges[1])
		min_y = float(boundary_edges[2])
		max_y = float(boundary_edges[3])

	graph_vbb = get_vbb_data(input_station)
	stations_with_distances = graph_vbb[0]

	positions = []
	distances = []
	station_types_arr = []

	for i in stations_with_distances:
		if stations[i][0] >= min_x and stations[i][0] <= max_x and stations[i][1] >= min_y and stations[i][1] <= max_y:
			distances.append(stations_with_distances[i])
			positions.append(stations[i])
			station_types_arr.append(station_types[i])

	delta_x = max_x-min_x
	delta_y = max_y-min_y
	
	height = args.height
	width = int(height * (delta_x/delta_y))

	point_size = (int(sizes[0]), int(sizes[1]), int(sizes[2]))
	draw_distance_map(positions, distances, station_types_arr,
					  width, height, point_size)


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print('\nFamoses Dabendorfprogramm beendet.')
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)
