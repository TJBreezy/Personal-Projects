import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import math
import random

# Precompute density values
density_options = {
    'X': 500,
    'Y': 600,
    'Z': 700
}

def generate_city_polygon():
    # Get city area input from user
    city_area = float(input("Enter the area of the city in square miles: "))

    # Calculate approximate side length assuming square-like shape
    side_length = np.sqrt(city_area)

    # Generate random points to create an irregular polygon
    num_points = np.random.randint(6, 12)
    angles = np.linspace(0, 2*np.pi, num_points, endpoint=False)
    radii = np.random.uniform(0.7*side_length, 1.3*side_length, num_points)

    # Convert polar coordinates to cartesian
    x_coords = radii * np.cos(angles)
    y_coords = radii * np.sin(angles)

    # Close the polygon by repeating first point
    x_coords = np.append(x_coords, x_coords[0])
    y_coords = np.append(y_coords, y_coords[0])

    return x_coords, y_coords

def generate_city_grid(x_coords, y_coords):
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)

    min_block = 0.4
    max_block = 0.5

    from matplotlib.path import Path
    city_boundary = Path(list(zip(x_coords, y_coords)))

    x_pos = min_x
    x_lines = []
    y_intersections = []
    while x_pos <= max_x:
        test_points = np.column_stack((
            np.full_like(np.linspace(min_y, max_y, 1000), x_pos),
            np.linspace(min_y, max_y, 1000)
        ))
        mask = city_boundary.contains_points(test_points)
        if any(mask):
            x_lines.append(x_pos)
            y_ranges = []
            in_range = False
            range_start = None
            for i, is_inside in enumerate(mask):
                if is_inside and not in_range:
                    range_start = test_points[i][1]
                    in_range = True
                elif not is_inside and in_range:
                    y_ranges.append((range_start, test_points[i-1][1]))
                    in_range = False
            if in_range:
                y_ranges.append((range_start, test_points[-1][1]))
            y_intersections.append(y_ranges)
        x_pos += np.random.uniform(min_block, max_block)

    y_pos = min_y
    y_lines = []
    x_intersections = []
    while y_pos <= max_y:
        test_points = np.column_stack((
            np.linspace(min_x, max_x, 1000),
            np.full_like(np.linspace(min_x, max_x, 1000), y_pos)
        ))
        mask = city_boundary.contains_points(test_points)
        if any(mask):
            y_lines.append(y_pos)
            x_ranges = []
            in_range = False
            range_start = None
            for i, is_inside in enumerate(mask):
                if is_inside and not in_range:
                    range_start = test_points[i][0]
                    in_range = True
                elif not is_inside and in_range:
                    x_ranges.append((range_start, test_points[i-1][0]))
                    in_range = False
            if in_range:
                x_ranges.append((range_start, test_points[-1][0]))
            x_intersections.append(x_ranges)
        y_pos += np.random.uniform(min_block, max_block)

    return x_lines, y_lines, x_intersections, y_intersections

# Generate and plot the city boundary
x_coords, y_coords = generate_city_polygon()
x_grid_lines, y_grid_lines, x_intersections, y_intersections = generate_city_grid(x_coords, y_coords)

# Transportation Nodes
nodes = []
for x, y_ranges in zip(x_grid_lines, y_intersections):
    for y_range in y_ranges:
        y_start, y_end = y_range
        y_points = np.arange(y_start, y_end + 0.05, 0.05)
        nodes.extend([(x, y) for y in y_points])

for y, x_ranges in zip(y_grid_lines, x_intersections):
    for x_range in x_ranges:
        x_start, x_end = x_range
        x_points = np.arange(x_start, x_end + 0.05, 0.05)
        nodes.extend([(x, y) for x in x_points])

nodes = np.array(nodes)

# Zones
area = 0.5 * abs(sum(x_coords[i] * y_coords[i+1] - x_coords[i+1] * y_coords[i]
                     for i in range(len(x_coords)-1)) +
                 x_coords[-1] * y_coords[0] - x_coords[0] * y_coords[-1])

city_radius = math.sqrt(area / math.pi)
city_center_radius = city_radius * math.sqrt(0.2)
inner_city_radius = city_radius * math.sqrt(0.5)
outer_city_radius = city_radius * math.sqrt(0.8)

# Facilities
print("Select a city density:")
for city in density_options:
    print(f"- {city} ({density_options[city]} people per square mile)")

density_choice = input("Enter city name: ")
while density_choice not in density_options:
    print("Invalid choice. Please select from the options above.")
    density_choice = input("Enter city name: ")

density = density_options[density_choice]
population = int(area * density)
print(f"Calculated population: {population:,} people")

total_households = round(population / 2.5)
total_residential_units = round(total_households * 0.4)

num_single_family = round(total_residential_units * 0.6)
num_multi_family = round(total_residential_units * 0.25)
num_apartments = round(total_residential_units * 0.15)

num_power_plants = max(1, round(population / 10000))
num_wastewater = max(1, round(population / 10000))
num_schools = max(1, round(population / 1000))
num_hospitals = max(1, round(population / 5000))
num_businesses = round(population * 30 / 1000)
num_industrial = max(1, round(population / 2000))
num_fire_stations = max(1, round(population / 3000))

FACILITY_SIZES = {
    'power_plant': 50 / 640,
    'wastewater': 50 / 640,
    'school': 30 / 640,
    'hospital': 40 / 640,
    'business_small': 5 / 640,
    'business_large': 10 / 640,
    'business_office': 7.5 / 640,
    'industrial_light': 20 / 640,
    'industrial_heavy': 40 / 640,
    'single_family': 0.5 / 640,
    'multi_family': 1.0 / 640,
    'apartment': 2.5 / 640,
    'fire_station': 3 / 640
}

facilities = {
    'power_plants': [],
    'wastewater': [],
    'schools': [],
    'hospitals': [],
    'businesses': [],
    'industrial': [],
    'residential': [],
    'fire_stations': []
}

def get_facility_corners(x, y, size):
    half_width = math.sqrt(size) / 2
    return [
        (x - half_width, y - half_width),
        (x + half_width, y - half_width),
        (x + half_width, y + half_width),
        (x - half_width, y + half_width)
    ]

def squares_overlap(corners1, corners2):
    min_x1 = min(x for x, y in corners1)
    max_x1 = max(x for x, y in corners1)
    min_y1 = min(y for x, y in corners1)
    max_y1 = max(y for x, y in corners1)

    min_x2 = min(x for x, y in corners2)
    max_x2 = max(x for x, y in corners2)
    min_y2 = min(y for x, y in corners2)
    max_y2 = max(y for x, y in corners2)

    return not (max_x1 < min_x2 or min_x1 > max_x2 or
               max_y1 < min_y2 or min_y1 > max_y2)

def is_within_city(x, y, x_coords, y_coords):
    from matplotlib.path import Path
    polygon = Path(np.column_stack((x_coords, y_coords)))
    return polygon.contains_point((x, y))

def is_within_zone(x, y, center_x, center_y, inner_radius, outer_radius):
    dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
    return inner_radius <= dist <= outer_radius

def is_on_grid(x, y, x_grid_lines, y_grid_lines, buffer=0.01):
    for grid_x in x_grid_lines:
        if abs(x - grid_x) < buffer:
            return True
    for grid_y in y_grid_lines:
        if abs(y - grid_y) < buffer:
            return True
    return False

def is_near_node(x, y, nodes, min_distance=0.05):
    return any(np.sqrt((x - node[0])**2 + (y - node[1])**2) < min_distance for node in nodes)

def facility_fits(x, y, size, all_facilities):
    new_corners = get_facility_corners(x, y, size)
    if not all(is_within_city(x, y, x_coords, y_coords) for x, y in new_corners):
        return False
    for facility_list in all_facilities.values():
        for facility in facility_list:
            existing_corners = get_facility_corners(
                facility['location'][0],
                facility['location'][1],
                facility['size']
            )
            if squares_overlap(new_corners, existing_corners):
                return False
    return True

def generate_facility_location(zone_range, facility_size, all_facilities, center=(0,0)):
    inner_radius, outer_radius = zone_range
    attempts = 0
    max_attempts = 1000

    while attempts < max_attempts:
        angle = np.random.uniform(0, 2*np.pi)
        r = np.random.uniform(inner_radius, outer_radius)
        x = center[0] + r * np.cos(angle)
        y = center[1] + r * np.sin(angle)

        if (not is_on_grid(x, y, x_grid_lines, y_grid_lines) and
            not is_near_node(x, y, nodes) and
            facility_fits(x, y, facility_size, all_facilities)):
            return x, y

        attempts += 1
    return None

inner_city_range = (0, inner_city_radius)
outer_city_range = (inner_city_radius, outer_city_radius)

for _ in range(num_power_plants):
    location = generate_facility_location(outer_city_range, FACILITY_SIZES['power_plant'], facilities)
    if location:
        x, y = location
        facilities['power_plants'].append({
            'location': (x, y),
            'size': FACILITY_SIZES['power_plant'],
            'functionality': round(random.uniform(0.8, 1.0), 2)
        })

for _ in range(num_wastewater):
    location = generate_facility_location(outer_city_range, FACILITY_SIZES['wastewater'], facilities)
    if location:
        x, y = location
        facilities['wastewater'].append({
            'location': (x, y),
            'size': FACILITY_SIZES['wastewater']
        })

for _ in range(num_hospitals):
    location = generate_facility_location(outer_city_range, FACILITY_SIZES['hospital'], facilities)
    if location:
        x, y = location
        facilities['hospitals'].append({
            'location': (x, y),
            'size': FACILITY_SIZES['hospital']
        })

for _ in range(num_industrial):
    ind_type = np.random.choice(['heavy', 'light'], p=[0.3, 0.7])
    size_key = f'industrial_{ind_type}'
    location = generate_facility_location(outer_city_range, FACILITY_SIZES[size_key], facilities)
    if location:
        x, y = location
        facilities['industrial'].append({
            'location': (x, y),
            'size': FACILITY_SIZES[size_key]
        })

for _ in range(num_schools):
    location = generate_facility_location(inner_city_range, FACILITY_SIZES['school'], facilities)
    if location:
        x, y = location
        facilities['schools'].append({
            'location': (x, y),
            'size': FACILITY_SIZES['school']
        })

for _ in range(num_fire_stations):
    zone = outer_city_range if np.random.random() < 0.6 else inner_city_range
    location = generate_facility_location(zone, FACILITY_SIZES['fire_station'], facilities)
    if location:
        x, y = location
        facilities['fire_stations'].append({
            'location': (x, y),
            'size': FACILITY_SIZES['fire_station']
        })

for _ in range(num_businesses):
    business_type = np.random.choice(['large', 'office', 'small'],
                                   p=[0.3, 0.2, 0.5])
    size_key = f'business_{business_type}'
    location = generate_facility_location(inner_city_range, FACILITY_SIZES[size_key], facilities)
    if location:
        x, y = location
        facilities['businesses'].append({
            'location': (x, y),
            'size': FACILITY_SIZES[size_key]
        })

for _ in range(num_apartments):
    zone = inner_city_range if np.random.random() < 0.7 else outer_city_range
    location = generate_facility_location(zone, FACILITY_SIZES['apartment'], facilities)
    if location:
        x, y = location
        facilities['residential'].append({
            'location': (x, y),
            'size': FACILITY_SIZES['apartment'],
            'type': 'apartment',
            'households': np.random.randint(10, 21)
        })

for _ in range(num_multi_family):
    zone = inner_city_range if np.random.random() < 0.4 else outer_city_range
    location = generate_facility_location(zone, FACILITY_SIZES['multi_family'], facilities)
    if location:
        x, y = location
        facilities['residential'].append({
            'location': (x, y),
            'size': FACILITY_SIZES['multi_family'],
            'type': 'multi_family',
            'households': np.random.randint(2, 5)
        })

for _ in range(num_single_family):
    zone = inner_city_range if np.random.random() < 0.2 else outer_city_range
    location = generate_facility_location(zone, FACILITY_SIZES['single_family'], facilities)
    if location:
        x, y = location
        facilities['residential'].append({
            'location': (x, y),
            'size': FACILITY_SIZES['single_family'],
            'type': 'single_family',
            'households': 1
        })

minor_roads = []
minor_nodes = []

def find_nearest_nodes(facility_loc, nodes, num_nodes=3):
    distances = np.sqrt(np.sum((nodes - facility_loc) ** 2, axis=1))
    nearest_indices = np.argpartition(distances, num_nodes)[:num_nodes]
    return nodes[nearest_indices]

def create_network_connection(facility_loc, nearest_nodes):
    x, y = facility_loc
    roads = []
    new_nodes = []

    nearest = nearest_nodes[0]
    intermediate_x = nearest[0]
    intermediate_y = y

    x_dist = abs(x - intermediate_x)
    y_dist = abs(y - nearest[1])

    if x_dist > 0:
        num_x_nodes = int(x_dist / 0.025)
        x_positions = np.linspace(x, intermediate_x, num_x_nodes + 1)
        for i in range(1, len(x_positions) - 1):
            new_nodes.append(np.array([x_positions[i], y]))

        roads.append({
            'start': facility_loc,
            'end': np.array([intermediate_x, y]),
            'type': 'minor'
        })

    if y_dist > 0:
        num_y_nodes = int(y_dist / 0.025)
        y_positions = np.linspace(intermediate_y, nearest[1], num_y_nodes + 1)
        for i in range(1, len(y_positions) - 1):
            new_nodes.append(np.array([intermediate_x, y_positions[i]]))

        roads.append({
            'start': np.array([intermediate_x, y]),
            'end': nearest,
            'type': 'minor'
        })

    for node in nearest_nodes[1:]:
        dist = np.sqrt(np.sum((node - facility_loc) ** 2))
        if dist < 0.2:
            intermediate_x = node[0]
            intermediate_y = y

            x_dist = abs(x - intermediate_x)
            y_dist = abs(y - node[1])

            if x_dist > 0:
                num_x_nodes = int(x_dist / 0.025)
                x_positions = np.linspace(x, intermediate_x, num_x_nodes + 1)
                for i in range(1, len(x_positions) - 1):
                    new_nodes.append(np.array([x_positions[i], y]))

                roads.append({
                    'start': facility_loc,
                    'end': np.array([intermediate_x, y]),
                    'type': 'minor'
                })

            if y_dist > 0:
                num_y_nodes = int(y_dist / 0.025)
                y_positions = np.linspace(intermediate_y, node[1], num_y_nodes + 1)
                for i in range(1, len(y_positions) - 1):
                    new_nodes.append(np.array([intermediate_x, y_positions[i]]))

                roads.append({
                    'start': np.array([intermediate_x, y]),
                    'end': node,
                    'type': 'minor'
                })

    return roads, new_nodes

for facility_type, facilities_list in facilities.items():
    if facility_type not in ['minor_roads', 'minor_nodes']:
        if facility_type == 'residential':
            for facility in facilities_list:
                facility_loc = np.array(facility['location'])
                all_nodes = np.vstack((nodes, minor_nodes)) if len(minor_nodes) > 0 else nodes
                nearest_nodes = find_nearest_nodes(facility_loc, all_nodes)
                new_roads, new_nodes = create_network_connection(facility_loc, nearest_nodes)
                minor_roads.extend(new_roads)
                minor_nodes.extend(new_nodes)
        elif facility_type == 'businesses':
            for facility in facilities_list:
                facility_loc = np.array(facility['location'])
                all_nodes = np.vstack((nodes, minor_nodes)) if len(minor_nodes) > 0 else nodes
                nearest_nodes = find_nearest_nodes(facility_loc, all_nodes)
                new_roads, new_nodes = create_network_connection(facility_loc, nearest_nodes)
                minor_roads.extend(new_roads)
                minor_nodes.extend(new_nodes)
        elif facility_type == 'industrial':
            for facility in facilities_list:
                facility_loc = np.array(facility['location'])
                all_nodes = np.vstack((nodes, minor_nodes)) if len(minor_nodes) > 0 else nodes
                nearest_nodes = find_nearest_nodes(facility_loc, all_nodes)
                new_roads, new_nodes = create_network_connection(facility_loc, nearest_nodes)
                minor_roads.extend(new_roads)
                minor_nodes.extend(new_nodes)
        else:
            for facility in facilities_list:
                facility_loc = np.array(facility['location'])
                all_nodes = np.vstack((nodes, minor_nodes)) if len(minor_nodes) > 0 else nodes
                nearest_nodes = find_nearest_nodes(facility_loc, all_nodes)
                new_roads, new_nodes = create_network_connection(facility_loc, nearest_nodes)
                minor_roads.extend(new_roads)
                minor_nodes.extend(new_nodes)

facilities['minor_roads'] = minor_roads
facilities['minor_nodes'] = np.array(minor_nodes) if minor_nodes else np.array([])

plt.figure(figsize=(12, 12))
ax = plt.gca()

city_center = plt.Circle((0, 0), city_center_radius, color='yellow', alpha=0.2, label='City Center')
inner_city = plt.Circle((0, 0), inner_city_radius, color='orange', alpha=0.1, label='Inner City')
outer_city = plt.Circle((0, 0), outer_city_radius, color='green', alpha=0.1, label='Outer City')

ax.add_patch(outer_city)
ax.add_patch(inner_city)
ax.add_patch(city_center)

plt.plot(x_coords, y_coords, 'k-', label='City Boundary', linewidth=2)

plt.scatter(nodes[:, 0], nodes[:, 1], c='red', s=1, alpha=0.5, label='Major Road Nodes')

if len(facilities['minor_nodes']) > 0:
    minor_nodes_array = np.array(facilities['minor_nodes'])
    plt.scatter(minor_nodes_array[:, 0], minor_nodes_array[:, 1],
               c='red', s=0.5, alpha=0.5, label='Minor Road Nodes')

if minor_roads:
    road = minor_roads[0]
    plt.plot([road['start'][0], road['end'][0]],
             [road['start'][1], road['end'][1]],
             'k--', linewidth=0.5, alpha=0.3, label='Minor Roads')
    for road in minor_roads[1:]:
        plt.plot([road['start'][0], road['end'][0]],
                 [road['start'][1], road['end'][1]],
                 'k--', linewidth=0.5, alpha=0.3)

scale_factor = 2000
facility_styles = {
    'power_plants': {'color': '#cc0000', 'marker': 's', 'label': 'Power Plants', 'size': (100/640) * scale_factor},
    'wastewater': {'color': '#660066', 'marker': 's', 'label': 'Wastewater', 'size': (50/640) * scale_factor},
    'hospitals': {'color': '#e6b800', 'marker': 's', 'label': 'Hospitals', 'size': (40/640) * scale_factor},
    'fire_stations': {'color': '#cc5200', 'marker': 's', 'label': 'Fire Stations', 'size': (2/640) * scale_factor},
    'schools': {'color': '#cc0066', 'marker': 's', 'label': 'Schools', 'size': (30/640) * scale_factor},
    'residential': {'color': '#004d99', 'marker': 's', 'label': 'Residential', 'size': (0.25/640) * scale_factor},
    'businesses': {'color': '#006600', 'marker': 's', 'label': 'Businesses', 'size': (5/640) * scale_factor},
    'industrial': {'color': '#996633', 'marker': 's', 'label': 'Industrial', 'size': (20/640) * scale_factor}
}

for facility_type, style in facility_styles.items():
    if facility_type in facilities and facilities[facility_type]:
        x_coords = [f['location'][0] for f in facilities[facility_type]]
        y_coords = [f['location'][1] for f in facilities[facility_type]]
        plt.scatter(x_coords, y_coords,
                   c=style['color'],
                   marker=style['marker'],
                   s=style['size'],
                   alpha=0.6,
                   label=style['label'])

plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', labelspacing=1.2)
plt.title('City Facilities Distribution')
plt.xlabel('Distance (miles)')
plt.ylabel('Distance (miles)')

plt.axis('equal')
plt.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.show()



def calculate_distance(point1, point2):
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def calculate_g_function(distance, depend_threshold, beta=0.01):
    if distance >= depend_threshold:
        return 0
    return np.exp(-beta * distance)

# Updated dependency coefficients
dependency_coefficients = {
    'transportation': {
        'transportation': 0.7,
        'power_plants': 0.5,
        'wastewater': 0.5,
        'schools': 0.6,
        'hospitals': 0.6,
        'residential': 0.4,
        'businesses': 0.4,
        'industrial': 0.4
    },
    'power_plants': {
        'transportation': 0.4,
        'power_plants': 0.5,
        'wastewater': 0.6,
        'schools': 0.6,
        'hospitals': 0.8,
        'residential': 0.7,
        'businesses': 0.7,
        'industrial': 0.8
    },
    'wastewater': {
        'transportation': 0.3,
        'power_plants': 0.4,
        'wastewater': 0.5,
        'schools': 0.6,
        'hospitals': 0.7,
        'residential': 0.8,
        'businesses': 0.6,
        'industrial': 0.7
    }
}

# Initialize functionalities dictionary
functionalities = {}
for facility_type in facilities:
    if facility_type not in ['minor_nodes', 'minor_roads'] and facilities[facility_type]:
        if isinstance(facilities[facility_type], list):
            functionalities[facility_type] = [1.0] * len(facilities[facility_type])

# Add transportation nodes to functionalities
total_nodes = len(nodes) + (len(facilities['minor_nodes']) if isinstance(facilities['minor_nodes'], np.ndarray) else 0)
functionalities['transportation'] = [1.0] * total_nodes

# Get user inputs
print("\nEnter number of facilities to damage:")
n_power = int(input(f"Number of power plants (max {len(facilities['power_plants'])}): "))
n_water = int(input(f"Number of wastewater facilities (max {len(facilities['wastewater'])}): "))
n_transport = int(input(f"Number of transportation nodes (max {len(nodes) + len(facilities['minor_nodes'])}): "))
depend_threshold = float(input("Enter dependency threshold distance (recommended 25 or 45): "))

# Randomly select and damage facilities
damaged_facilities = []

# Damage power plants
power_indices = np.random.choice(len(facilities['power_plants']), n_power, replace=False)
for idx in power_indices:
    damage = round(random.uniform(0.3, 0.7), 2)
    functionalities['power_plants'][idx] = round(1 - damage, 2)
    damaged_facilities.append({
        'type': 'power_plants',
        'index': idx,
        'location': facilities['power_plants'][idx]['location'],
        'delta_f': -damage
    })

# Damage wastewater facilities
water_indices = np.random.choice(len(facilities['wastewater']), n_water, replace=False)
for idx in water_indices:
    damage = round(random.uniform(0.3, 0.7), 2)
    functionalities['wastewater'][idx] = round(1 - damage, 2)
    damaged_facilities.append({
        'type': 'wastewater',
        'index': idx,
        'location': facilities['wastewater'][idx]['location'],
        'delta_f': -damage
    })

# Damage transportation nodes
total_nodes = len(nodes) + len(facilities['minor_nodes'])
transport_indices = np.random.choice(total_nodes, n_transport, replace=False)
for idx in transport_indices:
    damage = round(random.uniform(0.3, 0.7), 2)
    functionalities['transportation'][idx] = round(1 - damage, 2)
    # Determine if it's a major or minor node and get correct location
    if idx < len(nodes):
        location = nodes[idx]
    else:
        minor_idx = idx - len(nodes)
        location = facilities['minor_nodes'][minor_idx]
    
    damaged_facilities.append({
        'type': 'transportation',
        'index': idx,
        'location': location,
        'delta_f': -damage
    })

# Calculate interdependent effects
for facility_type in functionalities:
    if facility_type not in ['minor_nodes', 'minor_roads']:
        for j, _ in enumerate(functionalities[facility_type]):
            functionality_change = 0
            
            # Get facility location based on type
            if facility_type == 'transportation':
                if j < len(nodes):
                    facility_location = nodes[j]
                else:
                    minor_idx = j - len(nodes)
                    facility_location = facilities['minor_nodes'][minor_idx]
            else:
                facility_location = facilities[facility_type][j]['location']
            
            for damaged in damaged_facilities:
                if damaged['type'] in dependency_coefficients:
                    distance = calculate_distance(facility_location, damaged['location'])
                    g_value = calculate_g_function(distance, depend_threshold)
                    
                    if g_value > 0:  # Only if within threshold
                        rho = dependency_coefficients[damaged['type']].get(facility_type, 0)
                        functionality_change += damaged['delta_f'] * rho * g_value
            
            # Update functionality ensuring it stays between 0.3 and 1
            new_functionality = round(functionalities[facility_type][j] + functionality_change, 2)
            functionalities[facility_type][j] = max(0.3, min(1.0, new_functionality))

# Print results
print("\nDamaged Facilities and Their Effects:")
for damaged in damaged_facilities:
    print(f"{damaged['type']} at index {damaged['index']}: Functionality = {functionalities[damaged['type']][damaged['index']]}")

print("\nAffected Facilities:")
for facility_type in functionalities:
    if facility_type not in ['minor_nodes', 'minor_roads']:
        affected = [(i, f) for i, f in enumerate(functionalities[facility_type]) if f < 1.0]
        if affected:
            print(f"\n{facility_type}:")
            for idx, func in affected:
                print(f"  Index {idx}: Functionality = {func}")

# Install required packages and import necessary libraries
!pip install openpyxl
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials
import pandas as pd
import numpy as np
import math

# Authenticate and create the PyDrive client
auth.authenticate_user()
gauth = GoogleAuth()
gauth.credentials = GoogleCredentials.get_application_default()
drive = GoogleDrive(gauth)

# Define the path to save the Excel file in Google Drive
excel_path = "/content/drive/My Drive/Trevor's_Research_results_Notes_and_Research_log/3. My_Models/Data files/city_data_PC89_S6d_SmallMap_v4.1.xlsx"
writer = pd.ExcelWriter(excel_path, engine='openpyxl')

# Initialize node functionalities dictionary using existing functionalities
node_functionalities = {('major', idx): functionalities['transportation'][idx] for idx in range(len(nodes))}
node_functionalities.update({('minor', idx): functionalities['transportation'][idx + len(nodes)] 
                           for idx in range(len(facilities.get('minor_nodes', [])))})

# Initialize a unique ID counter
unique_id = 1

# Save each facility type to a separate sheet with a unique ID column
for facility_type, facility_list in facilities.items():
    if facility_type in ['minor_roads', 'minor_nodes']:
        continue
        
    data = []
    for idx, facility in enumerate(facility_list):
        facility_data = {
            'ID': unique_id,
            'x': facility['location'][0],
            'y': facility['location'][1],
            'Func': functionalities[facility_type][idx],
            'type': facility.get('type', facility_type),
            'size': facility.get('size', 'N/A')
        }
        data.append(facility_data)
        unique_id += 1

    if data:
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name=facility_type, index=False)

# Save transportation data to a separate sheet with a unique ID column
transportation_data = []

for idx, node in enumerate(nodes):
    node_info = {
        'ID': unique_id,
        'x': node[0],
        'y': node[1],
        'Func': functionalities['transportation'][idx],
        'type': 'major',
        'size': 'N/A'
    }
    transportation_data.append(node_info)
    unique_id += 1

if len(facilities['minor_nodes']) > 0:
    for idx, node in enumerate(facilities['minor_nodes']):
        node_info = {
            'ID': unique_id,
            'x': node[0],
            'y': node[1],
            'Func': functionalities['transportation'][idx + len(nodes)],
            'type': 'minor',
            'size': 'N/A'
        }
        transportation_data.append(node_info)
        unique_id += 1

if transportation_data:
    df = pd.DataFrame(transportation_data)
    df.to_excel(writer, sheet_name='transportation', index=False)

# Prepare summary data
num_damaged_facilities = len([d for d in damaged_facilities if d['type'] != 'transportation'])
num_damaged_nodes = len([d for d in damaged_facilities if d['type'] == 'transportation'])

summary_data = {
    'Parameter': [
        'City Area (sq miles)',
        'Population',
        'Number of Damaged Facilities',
        'Number of Damaged Nodes',
        'Total Number of Facilities',
        'Total Number of Nodes'
    ],
    'Value': [
        area,
        population,
        num_damaged_facilities,
        num_damaged_nodes,
        sum(len(facility_list) for facility_type, facility_list in facilities.items() 
            if facility_type not in ['minor_roads', 'minor_nodes']),
        len(nodes) + len(facilities.get('minor_nodes', []))
    ]
}

# Add damaged facilities info to summary data
for i, d in enumerate(damaged_facilities, 1):
    summary_data['Parameter'].append(f'Damaged Item {i}')
    summary_data['Value'].append(f"ID: {i}, Source: {d['type']}, Functionality: {functionalities[d['type']][d['index']]:.2f}")

# Convert to dataframe and save to summary sheet
summary_df = pd.DataFrame(summary_data)
summary_df.to_excel(writer, sheet_name='Summary', index=False)

# Save and close the Excel file
writer.close()
print(f"\nFacility and node data has been saved to: {excel_path}")
