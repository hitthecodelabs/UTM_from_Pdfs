from pyproj import CRS, Transformer

def save_single_point_to_kml(point_utm_list, file_name, point_name="UTM Point"):
    """
    Saves a single UTM point (WGS84 Zone 17S) to a KML file.

    Args:
        point_utm_list (list): A list containing two strings or numbers representing
                               the UTM coordinates: [easting, northing].
                               Example: ['532137', '9892120']
        output_kml_file (str): The desired path for the output KML file.
        point_name (str, optional): The name for the placemark in the KML file.
                                      Defaults to "UTM Point".
    """
    # --- Input Validation ---
    if not isinstance(point_utm_list, list) or len(point_utm_list) != 2:
        print(f"Error: Input 'point_utm_list' must be a list containing exactly two elements (easting, northing). Received: {point_utm_list}")
        return

    try:
        # Convert coordinates to float for transformation
        utm_x = float(point_utm_list[0])
        utm_y = float(point_utm_list[1])
    except (ValueError, TypeError) as e:
        print(f"Error converting coordinates {point_utm_list} to numbers: {e}")
        return

    # --- Define Coordinate Reference Systems ---
    source_crs = CRS("EPSG:32717") # WGS 84 / UTM zone 17S
    target_crs = CRS("EPSG:4326") # WGS 84 (lat/lon)

    # --- Create Transformer ---
    # always_xy=True ensures output is (longitude, latitude) order for KML
    transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)

    # --- Transform the single point ---
    try:
        lon, lat = transformer.transform(utm_x, utm_y)
    except Exception as e:
        print(f"Error during coordinate transformation: {e}")
        return

    # --- Format coordinates for KML ---
    # KML format: longitude,latitude,altitude (altitude is often 0)
    coordinates_str = f"{lon},{lat},0"

    # --- KML Structure Components ---
    kml_header = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Single Point KML</name>
    <description>{file_name}</description>
    <!-- Optional: Define a style for the point marker -->
    <Style id="pointStyle">
      <IconStyle>
        <scale>1.1</scale>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
        </Icon>
        <hotSpot x="20" y="2" xunits="pixels" yunits="pixels"/>
      </IconStyle>
    </Style>
"""

    # Use an f-string to create the Placemark for the point
    kml_placemark = f"""
    <Placemark>
      <name>{point_name} ({point_utm_list[0]}, {point_utm_list[1]})</name>
      <styleUrl>#pointStyle</styleUrl> <!-- Link to the style defined above -->
      <Point>
        <coordinates>{coordinates_str}</coordinates>
      </Point>
    </Placemark>
"""

    kml_footer = """
  </Document>
</kml>"""

    # --- Combine all parts into the final KML string ---
    full_kml = kml_header + kml_placemark + kml_footer

    # --- Write the KML string to a file ---
    try:
        with open(output_kml_file, 'w', encoding='utf-8') as f:
            f.write(full_kml)
        print(f"Successfully created KML file for point: '{output_kml_file}'")
    except Exception as e:
        print(f"Error writing KML file '{output_kml_file}': {e}")
