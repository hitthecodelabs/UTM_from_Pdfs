import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- Shoelace Formula for Polygon Area ---
def calculate_polygon_area(x, y):
    """
    Calculates the area of a polygon using the Shoelace Formula.
    Assumes x and y are sequences (lists, arrays) of coordinates.
    The area unit will be the square of the input coordinate units.
    """
    n = len(x)
    if n < 3:
        return 0.0 # A polygon needs at least 3 vertices

    # Ensure numpy arrays for vectorized operations
    x = np.asarray(x)
    y = np.asarray(y)

    # Apply the Shoelace formula
    area = 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
    # Alternate Shoelace implementation:
    # area = 0.0
    # for i in range(n):
    #     j = (i + 1) % n # Next vertex index, wraps around
    #     area += x[i] * y[j]
    #     area -= y[i] * x[j]
    # area = 0.5 * abs(area)
    return area

# --- Logic to Detect Polygons ---
polygons = []
polygon_areas_sq_units = [] # To store calculated areas in original square units
polygon_areas_hectares = [] # To store calculated areas in hectares
current_polygon_indices = []
start_point = None
start_index = -1 # Keep track of the index of the start point

if not df.empty:
    for index, row in df.iterrows():
        current_point = (row['x'], row['y'])

        if start_point is None:
            # Start of a new potential polygon
            start_point = current_point
            start_index = index
            current_polygon_indices.append(index)
        else:
            # Continue current polygon
            current_polygon_indices.append(index)
            # Check if this point closes the polygon (matches start_point and is not the start_point itself)
            if current_point == start_point and index != start_index:
                # Polygon closed, store it
                poly_df = df.loc[current_polygon_indices].copy()
                polygons.append(poly_df)

                # --- Calculate Area ---
                # Extract coordinates for area calculation
                # Important: Don't include the repeated closing point twice for area calc if needed,
                # but the Shoelace formula handles it correctly even if included.
                # Let's use all points as detected for simplicity.
                x_coords = poly_df['x'].values
                y_coords = poly_df['y'].values

                if len(x_coords) >= 3:
                    area_sq_units = calculate_polygon_area(x_coords, y_coords)
                    # ASSUMPTION: Coordinates are in meters. 1 Hectare = 10,000 sq meters
                    area_hectares = area_sq_units / 10000.0
                else:
                    area_sq_units = 0.0
                    area_hectares = 0.0

                polygon_areas_sq_units.append(area_sq_units)
                polygon_areas_hectares.append(area_hectares)
                # --- End Area Calculation ---

                # Reset for the next potential polygon
                current_polygon_indices = []
                start_point = None
                start_index = -1

    # If there are remaining points after the loop, they form the last polygon
    if current_polygon_indices:
        poly_df = df.loc[current_polygon_indices].copy()
        polygons.append(poly_df)
         # --- Calculate Area for the last (potentially unclosed) polygon ---
         # The Shoelace formula calculates area based on the sequence of vertices,
         # implicitly closing the polygon from the last to the first point.
        x_coords = poly_df['x'].values
        y_coords = poly_df['y'].values

        if len(x_coords) >= 3:
            area_sq_units = calculate_polygon_area(x_coords, y_coords)
            # ASSUMPTION: Coordinates are in meters. 1 Hectare = 10,000 sq meters
            area_hectares = area_sq_units / 10000.0
        else:
            area_sq_units = 0.0
            area_hectares = 0.0

        polygon_areas_sq_units.append(area_sq_units)
        polygon_areas_hectares.append(area_hectares)
        # --- End Area Calculation ---

# --- Analysis and Plotting ---

num_polygons = len(polygons)

print("-" * 30) # Separator
if num_polygons > 1:
    print(f"Found {num_polygons} polygons in the DataFrame.")
elif num_polygons == 1:
    print("Found 1 polygon in the DataFrame.")
else:
    print("Found no complete polygons based on the closing rule.")
print("-" * 30) # Separator

# Print Areas
if num_polygons > 0:
    print("Calculated Polygon Areas:")
    print("NOTE: Assumes input coordinates are in METERS.")
    for i in range(num_polygons):
        print(f"  Polygon {i+1}: {polygon_areas_sq_units[i]:,.2f} sq. units "
              f"({polygon_areas_hectares[i]:,.4f} Hectares)")
    print("-" * 30) # Separator


# --- Plotting ---
if num_polygons > 0:
    fig, ax = plt.subplots(figsize=(12, 12)) # Adjust figure size as needed
    colors = plt.cm.viridis(np.linspace(0, 1, max(1, num_polygons))) # Get distinct colors

    total_area_ha = 0
    for i, poly_df in enumerate(polygons):
        area_ha = polygon_areas_hectares[i]
        total_area_ha += area_ha
        # Include area in the label for the legend
        label = f'Polygon {i+1} ({area_ha:.4f} Ha)'
        # Plot lines connecting vertices
        ax.plot(poly_df['x'], poly_df['y'], marker='o', linestyle='-', label=label, color=colors[i])

    ax.set_xlabel("X-coordinate (meters)")
    ax.set_ylabel("Y-coordinate (meters)")
    title = f"Detected Polygons ({num_polygons} found)"
    if num_polygons > 0 :
         title += f" - Total Area: {total_area_ha:.4f} Ha"
    ax.set_title(title)
    ax.grid(True)
    ax.legend()
    # Use 'equal' aspect ratio for correct shape representation
    ax.set_aspect('equal', adjustable='box')
    plt.show()
else:print("No polygons to plot.")
