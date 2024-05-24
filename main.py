from fastapi import FastAPI, HTTPException, Query
from typing import Optional
import duckdb
import geopandas as gpd
import json
from shapely.geometry import shape

app = FastAPI()

# Conectar ao DuckDB e instalar a extensão spatial
con = duckdb.connect()
con.execute("INSTALL spatial;")
con.execute("LOAD spatial;")

# Carregar os dados do arquivo Parquet para o DuckDB
con.execute("CREATE TABLE DADOS_GEO AS SELECT * FROM read_parquet('area_imovel.parquet');")

# Criar o índice para a coluna cod_imovel na tabela DADOS_GEO
con.execute("CREATE INDEX idx_cod_imovel ON DADOS_GEO(cod_imovel);")

@app.get("/get_geojson_by_code/")
async def get_geojson_by_code(cod_imovel: str):
    sql_query = f"""
    SELECT *,
           ST_AsGeoJSON(ST_GeomFromWKB(geometry)) AS geometry_geojson
    FROM DADOS_GEO
    WHERE cod_imovel = '{cod_imovel}';
    """
    try:
        filtered_data = con.execute(sql_query).fetchdf()
        if filtered_data.empty:
            raise HTTPException(status_code=404, detail="Imóvel não encontrado")
        
        # Converter o GeoJSON para geometria Shapely e criar o GeoDataFrame
        filtered_data['geometry'] = filtered_data['geometry_geojson'].apply(lambda x: shape(json.loads(x)))
        filtered_gdf = gpd.GeoDataFrame(filtered_data, geometry='geometry')

        # Remover a coluna 'geometry_geojson' antes de converter para GeoJSON
        filtered_gdf = filtered_gdf.drop(columns=['geometry_geojson'])

        # Converter para GeoJSON
        geojson = filtered_gdf.to_json()

        return json.loads(geojson)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_geojson_by_coords/")
async def get_geojson_by_coords(
    longitude: float = Query(..., description="Longitude do ponto"),
    latitude: float = Query(..., description="Latitude do ponto")
):
    spatial_query = f"""
    SELECT *,
           ST_AsGeoJSON(ST_GeomFromWKB(geometry)) AS geometry_geojson,
           ST_Contains(ST_GeomFromWKB(geometry)::POLYGON_2D, ST_Point({longitude}, {latitude})::POINT_2D) AS is_contained
    FROM DADOS_GEO
    WHERE ST_GeometryType(ST_GeomFromWKB(geometry)) = 'POLYGON'
    AND ST_Contains(ST_GeomFromWKB(geometry)::POLYGON_2D, ST_Point({longitude}, {latitude})::POINT_2D)
    LIMIT 1;  -- Garantir que apenas um polígono seja retornado
    """
    try:
        filtered_data = con.execute(spatial_query).fetchdf()
        if filtered_data.empty:
            raise HTTPException(status_code=404, detail="Nenhum polígono contém o ponto fornecido")
        
        # Converter o GeoJSON para geometria Shapely e criar o GeoDataFrame
        filtered_data['geometry'] = filtered_data['geometry_geojson'].apply(lambda x: shape(json.loads(x)))
        filtered_gdf = gpd.GeoDataFrame(filtered_data, geometry='geometry')

        # Remover a coluna 'geometry_geojson' antes de converter para GeoJSON
        filtered_gdf = filtered_gdf.drop(columns=['geometry_geojson', 'is_contained'])

        # Converter para GeoJSON
        geojson = filtered_gdf.to_json()

        return json.loads(geojson)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
