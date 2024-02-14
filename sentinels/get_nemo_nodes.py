from hakai_salish_sea_model_tools.salishseacast import NEMOGrid
import pandas as pd
import folium

from loguru import logger

nemo_grid = NEMOGrid()
sentinel_stations = pd.read_excel("sentinels/LTNlatlong.xlsx")

nemo_stations = sentinel_stations.apply(
    lambda row: nemo_grid.ll2grid(
        row["Latitude"], row["Longitude"], min_depth=2, output="dict"
    ),
    axis=1,
).apply(pd.Series)


folium_map = folium.Map(
    location=[49.0, -123.0], zoom_start=9, tiles="CartoDB dark_matter"
)
for i, row in sentinel_stations.dropna().iterrows():
    logger.debug("Adding marker for {}", row["Location"])
    folium.Marker(row[["Latitude", "Longitude"]].values, popup=row["Location"]).add_to(
        folium_map
    )
    folium.Marker(
        nemo_stations.loc[i][["latitude", "longitude"]].values,
        popup=row["Location"],
        icon=folium.Icon(color="red", icon="cloud"),
    ).add_to(folium_map)
    folium.ColorLine(
        [
            row[["Latitude", "Longitude"]].values,
            nemo_stations.loc[i][["latitude", "longitude"]].values,
        ],
        colors=[0, 1],
        colormap=["y", "orange", "r"],
        popup=row["Location"],
    ).add_to(folium_map)


folium_map.save("sentinels/sentinels.html")

sentinel_stations.merge(
    nemo_stations.add_prefix("nemo_"), left_index=True, right_index=True
).to_csv("sentinels/nemo_stations.csv")
