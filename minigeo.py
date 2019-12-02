import json
import geojson
import geopandas as gpd
from rasterio.crs import CRS
import requests as req
#
# CONSTANTS
#
REQ_TMPL='https://nominatim.openstreetmap.org/search?q={}&format=json'




#
# CRS
#
def fetch_epsg(*places,noisy=True):
    q='+'.join(places)
    req_url=REQ_TMPL.format(q)
    r=req.get(req_url)
    jsn=r.json()[0]
    lat,lon=float(jsn['lat']),float(jsn['lon'])
    epsg=get_epsg(lat,lon)
    if noisy:
        print(req_url)
        print(epsg)
    return epsg


def get_epsg(lat,lon):
    return 32700-round((45+lat)/90)*100+round((183+lon)/6)


def get_crs(crs,as_dict=False):
    if isinstance(crs,int):
        crs_dict={'init':f'epsg:{crs}'}
    elif isinstance(crs,str):
        crs_dict={'init':crs}
    else:
        return crs
    if as_dict:
        return crs_dict
    else:
        return CRS(crs_dict)

    


#
# BOUNDING BOXES 
#
def buffer_bounds(
        bounds=None,
        xmin=None,
        ymin=None,
        xmax=None,
        ymax=None,
        delta=None):
    if bounds:
        xmin,ymin,xmax,ymax=bounds
    if delta:
        xmin,ymin,xmax,ymax=xmin-delta,ymin-delta,xmax+delta,ymax+delta
    return xmin, ymin, xmax, ymax


def bounds_geometry(
        bounds=None,
        xmin=None,
        ymin=None,
        xmax=None,
        ymax=None,
        delta=None,
        as_feat=False,
        as_fc=False,
        as_gdf=False,
        crs=None,
        props={}):
    xmin,ymin,xmax,ymax=buffer_bounds(bounds,xmin,ymin,xmax,ymax,delta)
    coords=[[
        [xmin,ymax],
        [xmax,ymax],
        [xmax,ymin],
        [xmin,ymin],
        [xmin,ymax]]]
    geom={"coordinates": coords, "type": "Polygon"}
    if as_feat or as_fc or as_gdf:
        geom={'geometry':geom,'type':'Feature'}
        if props:
            geom['properties']=props
    if as_fc or as_gdf:
        geom={'features':[geom],'type':'FeatureCollection'}
    geom=geojson.loads(json.dumps(geom))
    if as_gdf:
        geom=gpd.GeoDataFrame.from_features(geom,crs=get_crs(crs))
    return geom




#
# RASTERIO PROFILE
#
def crs_res_bounds(profile):
    """ get crs, resolution and bounds form image profile """
    affine=profile['transform']
    x1=affine.c
    x2=x1+profile['width']*affine.a
    y1=affine.f
    y2=y1+profile['height']*affine.e
    minx=min(x1,x2)
    maxx=max(x1,x2)
    miny=min(y1,y2)
    maxy=max(y1,y2)
    res=abs(affine.a)
    crs=str(profile['crs'])
    return crs,res,(minx,miny,maxx,maxy)



def profile_to_geometry(
        profile,
        delta=None,
        as_geometry=True,
        as_feat=False,
        as_fc=False,
        as_gdf=False,
        return_profile_data=True):
    crs,res,bounds=crs_res_bounds(profile)
    geom=bounds_geometry(
        bounds,
        crs=crs,
        delta=delta,
        as_gdf=True)
    geom=geom.to_crs(get_crs(4326))
    if as_geometry or as_feat or as_fc:
        geom=geojson.loads(geom.geometry.to_json())
    if as_geometry or as_feat:
        geom=geom['features']
    if as_geometry:
        geom=geom[0]['geometry']
    if return_profile_data:
        return geom, (crs, res, bounds)
    else:
        return geom




#
# UTILS
#
def gdf_to_geojson(gdf,crs=None):
    if crs:
        gdf=gdf.to_crs(get_crs(crs))
    return geojson.loads(gdf.geometry.to_json())




