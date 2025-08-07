import bpy
import json
import math
import os
import random

def clear_scene():
    """
    Clears all objects from the current scene.
    """
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_room(size_x, size_y, size_z):
    """
    Creates a simple room with a floor and four walls.
    """
    # Create floor
    bpy.ops.mesh.primitive_plane_add(size=max(size_x, size_y), location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Floor"
    floor.scale = (size_x / max(size_x, size_y), size_y / max(size_x, size_y), 1)
    bpy.ops.rigidbody.object_add(type='PASSIVE')
    floor.rigid_body.collision_shape = 'MESH'


    # Create walls
    wall_thickness = 0.1
    # Wall 1
    bpy.ops.mesh.primitive_cube_add(location=(size_x / 2, 0, size_z / 2))
    wall1 = bpy.context.active_object
    wall1.name = "Wall1"
    wall1.scale = (wall_thickness / 2, size_y / 2, size_z / 2)
    bpy.ops.rigidbody.object_add(type='PASSIVE')
    wall1.rigid_body.collision_shape = 'BOX'

    # Wall 2
    bpy.ops.mesh.primitive_cube_add(location=(-size_x / 2, 0, size_z / 2))
    wall2 = bpy.context.active_object
    wall2.name = "Wall2"
    wall2.scale = (wall_thickness / 2, size_y / 2, size_z / 2)
    bpy.ops.rigidbody.object_add(type='PASSIVE')
    wall2.rigid_body.collision_shape = 'BOX'

    # Wall 3
    bpy.ops.mesh.primitive_cube_add(location=(0, size_y / 2, size_z / 2))
    wall3 = bpy.context.active_object
    wall3.name = "Wall3"
    wall3.scale = (size_x / 2, wall_thickness / 2, size_z / 2)
    bpy.ops.rigidbody.object_add(type='PASSIVE')
    wall3.rigid_body.collision_shape = 'BOX'

    # Wall 4
    bpy.ops.mesh.primitive_cube_add(location=(0, -size_y / 2, size_z / 2))
    wall4 = bpy.context.active_object
    wall4.name = "Wall4"
    wall4.scale = (size_x / 2, wall_thickness / 2, size_z / 2)
    bpy.ops.rigidbody.object_add(type='PASSIVE')
    wall4.rigid_body.collision_shape = 'BOX'


def add_random_objects(num_objects, room_size_x, room_size_y, room_size_z):
    """
    Adds a number of random objects (cubes, spheres) to the scene.
    """
    objects = []
    for _ in range(num_objects):
        obj_type = random.choice(['CUBE', 'SPHERE'])
        if obj_type == 'CUBE':
            bpy.ops.mesh.primitive_cube_add(size=random.uniform(0.2, 1.0))
        elif obj_type == 'SPHERE':
            bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(0.1, 0.5))

        obj = bpy.context.active_object
        obj.location.x = random.uniform(-room_size_x / 2 + 0.5, room_size_x / 2 - 0.5)
        obj.location.y = random.uniform(-room_size_y / 2 + 0.5, room_size_y / 2 - 0.5)
        obj.location.z = random.uniform(1.0, room_size_z - 1.0)
        obj.rotation_euler = (random.uniform(0, 2 * math.pi), random.uniform(0, 2 * math.pi), random.uniform(0, 2 * math.pi))

        bpy.ops.rigidbody.object_add(type='ACTIVE')
        obj.rigid_body.collision_shape = 'CONVEX_HULL'
        objects.append(obj)
    return objects

def run_physics_simulation(frames):
    """
    Runs the physics simulation for a given number of frames.
    """
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames
    bpy.ops.ptcache.bake_all(bake=True)


def check_intersections(objects):
    """
    Checks if any objects are intersecting with each other.
    """
    for i in range(len(objects)):
        for j in range(i + 1, len(objects)):
            obj1 = objects[i]
            obj2 = objects[j]

            # A simple bounding box check
            if (abs(obj1.location.x - obj2.location.x) * 2 < (obj1.dimensions.x + obj2.dimensions.x) and
                abs(obj1.location.y - obj2.location.y) * 2 < (obj1.dimensions.y + obj2.dimensions.y) and
                abs(obj1.location.z - obj2.location.z) * 2 < (obj1.dimensions.z + obj2.dimensions.z)):
                return True
    return False

def check_floating(objects, floor_z=0.0):
    """
    Checks if any objects are floating (not on the floor or another object).
    This is a simplified check. A more robust solution would use raycasting.
    """
    for obj in objects:
        if obj.location.z > floor_z + obj.dimensions.z / 2 + 0.1:
            is_supported = False
            for other_obj in objects:
                if obj == other_obj:
                    continue
                # Check if another object is below it
                dist_xy = math.sqrt((obj.location.x - other_obj.location.x)**2 + (obj.location.y - other_obj.location.y)**2)
                if dist_xy < (obj.dimensions.x + other_obj.dimensions.x) / 2:
                     if obj.location.z > other_obj.location.z:
                        is_supported = True
                        break
            if not is_supported:
                 # Check if on the floor
                if obj.location.z > floor_z + obj.dimensions.z / 2 + 0.05:
                    return True # Floating
    return False


def export_scene_data(output_path, scene_index, label, objects):
    """
    Exports the scene data to a JSON file and renders an image.
    """
    # Ensure output directory exists
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Export JSON
    data = {
        "scene_index": scene_index,
        "label": label,
        "objects": []
    }
    for obj in objects:
        data["objects"].append({
            "name": obj.name,
            "location": list(obj.location),
            "rotation_euler": list(obj.rotation_euler),
            "dimensions": list(obj.dimensions)
        })

    json_path = os.path.join(output_path, f"scene_{scene_index:04d}.json")
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=4)

    # Render Image
    bpy.context.scene.render.filepath = os.path.join(output_path, f"scene_{scene_index:04d}.png")
    bpy.ops.render.render(write_still=True)


def generate_dataset(num_scenes, output_path):
    """
    Main function to generate the dataset.
    """
    for i in range(num_scenes):
        clear_scene()

        room_size_x = random.uniform(5, 10)
        room_size_y = random.uniform(5, 10)
        room_size_z = random.uniform(3, 5)
        create_room(room_size_x, room_size_y, room_size_z)

        num_objects = random.randint(3, 10)
        objects = add_random_objects(num_objects, room_size_x, room_size_y, room_size_z)

        run_physics_simulation(250) # Run for 250 frames

        # Go to the last frame to get final positions
        bpy.context.scene.frame_set(250)


        is_intersecting = check_intersections(objects)
        is_floating = check_floating(objects)

        if is_intersecting or is_floating:
            label = "impossible"
        else:
            label = "plausible"

        print(f"Scene {i}: Intersecting={is_intersecting}, Floating={is_floating}, Label={label}")

        export_scene_data(output_path, i, label, objects)

if __name__ == "__main__":
    # Configuration
    NUM_SCENES = 10 # Start with a small number for testing
    OUTPUT_DIR = os.path.join(os.path.dirname(bpy.data.filepath), "metaspatial_dataset") if bpy.data.filepath else "metaspatial_dataset"


    generate_dataset(NUM_SCENES, OUTPUT_DIR)
    print(f"Generated {NUM_SCENES} scenes in {OUTPUT_DIR}")