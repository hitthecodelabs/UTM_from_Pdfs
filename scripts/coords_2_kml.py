import pandas as pd
from pyproj import CRS, Transformer

def generate_kml(polygons, file_name):
    # --- Define Coordinate Reference Systems ---
    # Source: WGS 84 / UTM zone 17S
    source_crs = CRS("EPSG:32717")
    # Target: WGS 84 (lat/lon) used by KML
    target_crs = CRS("EPSG:4326")

    # --- Create Transformer ---
    # always_xy=True ensures output is (longitude, latitude) order, which KML needs
    transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)

    # --- KML Structure Components ---
    kml_header = """<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
        <name>Polygons from DataFrames</name>
        <!-- Optional: Define a style for the polygons -->
        <Style id="polygonStyle">
        <LineStyle>
            <color>ff0000ff</color> <!-- Red outline -->
            <width>2</width>
        </LineStyle>
        <PolyStyle>
            <color>7f00ff00</color> <!-- Semi-transparent green fill -->
            <fill>1</fill>
            <outline>1</outline>
        </PolyStyle>
        </Style>
    """

    kml_footer = """
    </Document>
    </kml>"""

    kml_placemarks = [] # To store KML for each polygon

    # --- Process each DataFrame ---
    for i, df in enumerate(polygons):
        if not isinstance(df, pd.DataFrame) or df.empty:
            print(f"Skipping item {i+1} as it's not a valid DataFrame or is empty.")
            continue

        if 'x' not in df.columns or 'y' not in df.columns:
            print(f"Skipping DataFrame {i+1} due to missing 'x' or 'y' columns.")
            continue

        # Drop rows with missing coordinates if any
        df_clean = df.dropna(subset=['x', 'y'])

        # Need at least 3 points for a polygon
        if len(df_clean) < 3:
            print(f"Skipping polygon {i+1} as it has less than 3 valid points.")
            continue

        # Extract coordinates
        x_coords = df_clean['x'].values
        y_coords = df_clean['y'].values

        # Transform coordinates to lon/lat
        lons, lats = transformer.transform(x_coords, y_coords)

        # Format coordinates for KML string: "lon,lat,alt lon,lat,alt ..."
        # Altitude (alt) is typically 0 for ground polygons.
        coord_list = []
        for lon, lat in zip(lons, lats):
            coord_list.append(f"{lon},{lat},0") # Altitude 0

        # KML polygons must be closed: the first coordinate must be repeated at the end.
        # Check if the provided data already does this. If not, add it.
        if coord_list: # Check if list is not empty after potential drops
            first_coord = coord_list[0]
            last_coord = coord_list[-1]
            # Compare the lon,lat parts only (ignore potential altitude differences if any)
            if first_coord.rsplit(',', 1)[0] != last_coord.rsplit(',', 1)[0]:
                print(f"Note: Closing polygon {i+1} by repeating the first coordinate.")
                coord_list.append(first_coord)

        coordinates_str = " ".join(coord_list)

        # Create KML Placemark for this polygon
        placemark = f"""
        <Placemark>
        <name>Polygon {i+1}</name>
        <styleUrl>#polygonStyle</styleUrl> <!-- Link to the style defined above -->
        <Polygon>
            <outerBoundaryIs>
            <LinearRing>
                <coordinates>{coordinates_str}</coordinates>
            </LinearRing>
            </outerBoundaryIs>
        </Polygon>
        </Placemark>"""
        kml_placemarks.append(placemark)

    # --- Combine all parts into the final KML string ---
    full_kml = kml_header + "\n".join(kml_placemarks) + kml_footer

    # --- Write the KML string to a file ---
    # output_kml_file = "output_polygons.kml"
    output_kml_file = file_name.replace(".docx", ".kml")
    try:
        with open(output_kml_file, 'w', encoding='utf-8') as f:
            f.write(full_kml)
        print(f"Successfully created KML file: '{output_kml_file}'")
    except Exception as e:
        print(f"Error writing KML file: {e}")
