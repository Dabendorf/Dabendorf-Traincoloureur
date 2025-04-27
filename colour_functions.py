import numpy as np
import colorsys

def hsv2rgb(h, s, v):
	return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))


def normalised_rainbow1(distance_array, spectre_size):
	#spectre_size = number of iterations around rainbow, preferibly < 1.0

	midpoint=0.3
	steepness=10
	max_dist = np.amax(distance_array)
	min_dist = np.amin(distance_array)
	rangemm = max_dist - min_dist
	length = len(distance_array)
	colours = [None] * length
	start = 0

	for i in range(length):
		if distance_array[i] != 0:
			normed = (distance_array - np.min(distance_array)) / (np.max(distance_array) - np.min(distance_array))
			stretched = 1 / (1 + np.exp(-steepness * (normed - midpoint)))
			stretched_normed = (stretched - np.min(stretched)) / (np.max(stretched) - np.min(stretched))

			colours = []
			for val in stretched_normed:
				hue = ((val + (start / 360)) % 1) * spectre_size
				colours.append(hsv2rgb(hue, 1.0, 1.0))
		else:
			colours[i] = (51, 178, 0)  # DORgreen, 33b200
	return colours