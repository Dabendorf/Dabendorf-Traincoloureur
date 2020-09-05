# Traincoloureur
## Preamble
![Example](examples/Dabendorf2.png)

The aim of that little python programme is the colourful visualisation of public transport distances in Berlin and Brandenburg.
It shows distances from a certain station (by default _Dabendorf Centralstation_) represented by a rainbow scale.

## Prerequisites
The programme runs on Python 3, using the _pygame_ framework.
```
python3 -m pip install -U pygame --user
```

### Load vbb data
One needs to obtain the official VBB station data and distances first. We thankfully use the [Generate-vbb-graph](https://github.com/derhuerst/generate-vbb-graph/) javascript framework by [derhuerst](https://github.com/derhuerst/).
Please run the following installation commands.

Installing nodejs and generate-vbb-graph
```
sudo apt install npm
sudo npm install -g generate-vbb-graph
sudo npm install vbb-graph
```

Now, its possible to obtain the station data by running the following command:
```
generate-vbb-graph -p suburban,subway,regional,tram,ferry,bus
```

Please insert the _edges.ndjson_ and _nodes.ndjson_ into the main folder.

## Running Traincoloureur
You can run the traincoloureur with the following command:
Installing nodejs and generate-vbb-graph
```
python3 tools.py 
```

It is possible to select a different start station by appending a station id from _nodes.ndjson_, for example _900000193002_ for _S Adlershof_
```
python3 tools.py 900000193002
```

## Further customisation 
There are some parameters included in the _tools.py_, which are not available as commandline parameters yet. Feel free to include that functionality!

One can change the spectreSize, which is the variable, how often the distance function iterates over a full rainbow. 
Changing the last line changes the colour of the starting station.
```python
if distance_array[i] != 0:
	start = 0  # 102.8 Start colour in Dabendorf, degrees from red
	spectreSize = 0.8  # number of iterations around rainbow, preferibly < 1.0
	hue = ((((distance_array[i] - min)/rangemm) +
		(((start/360)*255)/255)) % 1)*spectreSize

	colours[i] = hsv2rgb(hue, 1.0, 1.0)
else:
	colours[i] = (51, 178, 0)  # DORgreen, 33b200
     
 ```
 
 Changing the size of the points (regio,subway,bus).
 ```python
 point_size = (6, 5, 3)
     
 ```
 
