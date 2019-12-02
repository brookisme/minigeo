from distutils.core import setup
setup(
  name = 'minigeo',
  py_modules = ['minigeo'],
  version = '0.0.0.1',
  description = 'convenience wrappers for managing projections/profiles/geometries',
  author = 'Brookie Guzder-Williams',
  author_email = 'brook.williams@gmail.com',
  url = 'https://github.com/brookisme/minigeo',
  download_url = 'https://github.com/brookisme/minigeo/tarball/0.1',
  keywords = ['rasterio','geopandas','geojson','crs','projection'],
  include_package_data=True,
  data_files=[
    (
      'config',[]
    )
  ],
  classifiers = [],
  entry_points={
      'console_scripts': [
      ]
  }
)