import ee
import geemap
from cloudmesh.common.FlatDict import FlatDict
from cloudmesh.common.Shell import Shell
import sys

config = FlatDict()
config.loadf(filename="~/.ee.yaml")
config.filename = "local_map.html"

print (config)

# Set up Earth Engine API key
# Replace 'your-ee-api-key' with your actual Earth Engine API key
ee.Authenticate()
ee.Initialize(project=config.project)

# Define the date range
start_date = '2018-04-01'
end_date = '2018-04-04'

# Create an ImageCollection
dataset = (ee.ImageCollection('COPERNICUS/S3/OLCI')
           .filterDate(ee.Date(start_date), ee.Date(end_date)))

# Select bands for visualization and apply band-specific scale factors.
rgb = (dataset.select(['Oa08_radiance', 'Oa06_radiance', 'Oa04_radiance'])
       .median()
       # Convert to radiance units.
       .multiply(ee.Image([0.00876539, 0.0123538, 0.0115198])))

# Define visualization parameters
vis_params = {
    'min': 0,
    'max': 6,
    'gamma': 1.5,
}

# Set the map center
center = [46.043, 1.45]
zoom = 5

# Create a Map object
Map = geemap.Map(center=center, zoom=zoom)

# Add the layer to the map
Map.addLayer(rgb, vis_params, 'RGB')

# Display the map
Map.addLayerControl()
# display(Map)


# Save the map as an HTML file
Map.save(config.filename)

Shell.browser(config.filename)

