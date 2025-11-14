import time
import numpy as np
import open3d as o3d

# =========================================================
# CONFIG
# =========================================================
MESH_PATH = "wolf.glb"      # your model file in this folder
ENABLE_VIEWER = True        # set False if viewer crashes on your Mac


# =========================================================
# SMALL HELPERS
# =========================================================
def header(title: str):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def show(geoms, title: str, width: int = 960, height: int = 720):
    """
    Wrapper around draw_geometries so we can turn it off easily.
    NOTE: Window is BLOCKING – close it to continue to next step.
    """
    if not ENABLE_VIEWER:
        print(f"[{title}] Visualization skipped (ENABLE_VIEWER = False).")
        return

    if not isinstance(geoms, list):
        geoms = [geoms]

    print(f"[VIEWER] Opening window: {title}")
    o3d.visualization.draw_geometries(geoms, window_name=title,
                                      width=width, height=height)
    time.sleep(0.3)  # tiny pause after closing window


# =========================================================
# 1) LOADING ORIGINAL MESH
# =========================================================
header("1) LOADING ORIGINAL MESH")

mesh = o3d.io.read_triangle_mesh(MESH_PATH)
if mesh.is_empty():
    raise RuntimeError(f"Could not load mesh from {MESH_PATH}")

mesh.compute_vertex_normals()

print("What I understood:")
print("- A 3D mesh is made of vertices (3D points) and triangles (faces).")
print("- Normals/colors are extra attributes that affect shading/appearance.")

v_mesh = np.asarray(mesh.vertices)
t_mesh = np.asarray(mesh.triangles)

print("\nMesh info:")
print(f"  Number of vertices:  {v_mesh.shape[0]}")
print(f"  Number of triangles: {t_mesh.shape[0]}")
print(f"  Has vertex colors:   {mesh.has_vertex_colors()}")
print(f"  Has vertex normals:  {mesh.has_vertex_normals()}")

show(mesh, "Step 1 – Original Mesh")


# =========================================================
# 2) MESH -> POINT CLOUD
# =========================================================
header("2) MESH -> POINT CLOUD")

pcd = mesh.sample_points_poisson_disk(number_of_points=30000)

print("What I understood:")
print("- A point cloud is only a set of 3D sample points on the surface.")
print("- The overall shape is kept, but mesh connectivity (faces) is lost.")

pcd_points = np.asarray(pcd.points)

print("\nPoint cloud info:")
print(f"  Number of points:    {pcd_points.shape[0]}")
print(f"  Has colors:          {pcd.has_colors()}")
print(f"  Has normals:         {pcd.has_normals()}")

# basic bbox for info (like your friend)
bbox_pcd = pcd.get_axis_aligned_bounding_box()
print(f"  Bounding box min:    {bbox_pcd.min_bound}")
print(f"  Bounding box max:    {bbox_pcd.max_bound}")
print(f"  Extent (x,y,z):      {bbox_pcd.get_extent()}")

show(pcd, "Step 2 – Point Cloud")


# =========================================================
# 3) SURFACE RECONSTRUCTION (POISSON)
# =========================================================
header("3) SURFACE RECONSTRUCTION (POISSON)")

# ensure normals
pcd.estimate_normals(
    search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.05, max_nn=30)
)

recon_mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
    pcd, depth=8
)

# crop to original mesh region
bbox_mesh_orig = mesh.get_axis_aligned_bounding_box()
recon_mesh = recon_mesh.crop(bbox_mesh_orig)
recon_mesh.compute_vertex_normals()

v_rec = np.asarray(recon_mesh.vertices)
t_rec = np.asarray(recon_mesh.triangles)

print("What I understood:")
print("- From random points + normals we reconstruct a continuous surface.")
print("- Poisson gives a closed smooth mesh; cropping removes far artifacts.")

print("\nReconstructed mesh info:")
print(f"  Number of vertices:  {v_rec.shape[0]}")
print(f"  Number of triangles: {t_rec.shape[0]}")
print(f"  Has vertex colors:   {recon_mesh.has_vertex_colors()}")
print(f"  Has vertex normals:  {recon_mesh.has_vertex_normals()}")

show(recon_mesh, "Step 3 – Reconstructed Mesh (Poisson)")


# =========================================================
# 4) VOXELIZATION
# =========================================================
header("4) VOXELIZATION")

voxel_size = 0.05
voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(pcd, voxel_size)
voxels = voxel_grid.get_voxels()

has_voxel_color = False
if len(voxels) > 0 and hasattr(voxels[0], "color"):
    has_voxel_color = True

print("What I understood:")
print("- Voxelization converts the object into small cubes (voxels) on a grid.")
print("- This is a discrete volume/occupancy representation of the shape.")

print("\nVoxel grid info:")
print(f"  Voxel size used: {voxel_size}")
print(f"  Number of voxels (occupied): {len(voxels)}")
print(f"  Has colors:       {has_voxel_color}")

bbox_vox = voxel_grid.get_axis_aligned_bounding_box()
print(f"  Voxel bbox min:   {bbox_vox.min_bound}")
print(f"  Voxel bbox max:   {bbox_vox.max_bound}")

show(voxel_grid, "Step 4 – Voxelized Model")


# =========================================================
# 5) ADDING A PLANE (MESH + PLANE + BBOX)
# =========================================================
header("5) ADDING A PLANE TO THE MESH")

aabb = recon_mesh.get_axis_aligned_bounding_box()
center = aabb.get_center()
extent = aabb.get_extent()

# plane will be a rectangle in YZ, passing through center in X
size_y = float(extent[1]) * 1.5
size_z = float(extent[2]) * 1.5
x = float(center[0])

y0 = center[1] - size_y / 2.0
z0 = center[2] - size_z / 2.0

plane_vertices = np.array(
    [
        [x, y0,           z0],
        [x, y0 + size_y,  z0],
        [x, y0 + size_y,  z0 + size_z],
        [x, y0,           z0 + size_z],
    ],
    dtype=float,
)

plane_triangles = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.int32)

plane_mesh = o3d.geometry.TriangleMesh()
plane_mesh.vertices = o3d.utility.Vector3dVector(plane_vertices)
plane_mesh.triangles = o3d.utility.Vector3iVector(plane_triangles)
plane_mesh.paint_uniform_color([0.7, 0.7, 0.7])

# also show bbox like your friend
bbox_for_show = aabb
bbox_for_show.color = (1, 0, 0)

print("What I understood:")
print("- I defined an analytic plane: all x such that n·(x - p0) = 0.")
print("- Here n is along +X, so the plane is vertical through the center.")
print("- I show the reconstructed mesh, the plane, and its bounding box.")

show([recon_mesh, plane_mesh, bbox_for_show], "Step 5 – Plane + Mesh + BBox")


# =========================================================
# 6) SURFACE CLIPPING BY PLANE (MESH-BASED, YOUR STYLE)
# =========================================================
header("6) SURFACE CLIPPING (MESH)")

plane_point = center
plane_normal = np.array([1.0, 0.0, 0.0], dtype=float)  # along X

V = v_rec
T = t_rec

signed = (V - plane_point) @ plane_normal  # signed distance: d = n·(x - p0)
keep = signed <= 0
if not np.any(keep):
    keep = signed >= 0

index_map = -np.ones(len(V), dtype=int)
index_map[keep] = np.arange(np.count_nonzero(keep))

tri_keep = np.all(keep[T], axis=1)

clipped_vertices = V[keep]
clipped_triangles = index_map[T[tri_keep]]

clipped_mesh = o3d.geometry.TriangleMesh()
clipped_mesh.vertices = o3d.utility.Vector3dVector(clipped_vertices)
clipped_mesh.triangles = o3d.utility.Vector3iVector(clipped_triangles)
clipped_mesh.compute_vertex_normals()

print("What I understood:")
print("- I computed the signed distance of each vertex to the plane.")
print("- I removed triangles completely on the 'right' side of the plane.")
print("- The remaining part is the mesh clipped by that plane.")

print("\nClipped mesh info:")
print(f"  Remaining vertices:  {clipped_vertices.shape[0]}")
print(f"  Remaining triangles: {clipped_triangles.shape[0]}")
print(f"  Has vertex colors:   {clipped_mesh.has_vertex_colors()}")
print(f"  Has vertex normals:  {clipped_mesh.has_vertex_normals()}")

show(clipped_mesh, "Step 6 – Clipped Mesh (Mesh-based)")


# =========================================================
# 7) COLOR GRADIENT + EXTREME POINTS (MESH)
# =========================================================
header("7) COLOR GRADIENT + EXTREME POINTS (MESH)")

Vc = np.asarray(clipped_mesh.vertices)
Tc = np.asarray(clipped_mesh.triangles)

if Vc.shape[0] == 0:
    print("No vertices in clipped mesh; skipping gradient visualization.")
else:
    axis = 2  # Z axis
    z = Vc[:, axis]
    z_min, z_max = z.min(), z.max()
    denom = (z_max - z_min) if z_max != 0 else 1.0
    t_val = (z - z_min) / denom

    colors = np.zeros((Vc.shape[0], 3))
    colors[:, 0] = t_val        # red
    colors[:, 2] = 1.0 - t_val  # blue

    mesh_colored = o3d.geometry.TriangleMesh()
    mesh_colored.vertices = o3d.utility.Vector3dVector(Vc)
    mesh_colored.triangles = o3d.utility.Vector3iVector(Tc)
    mesh_colored.vertex_colors = o3d.utility.Vector3dVector(colors)
    mesh_colored.compute_vertex_normals()

    min_idx = int(np.argmin(z))
    max_idx = int(np.argmax(z))
    min_pt = Vc[min_idx]
    max_pt = Vc[max_idx]

    min_sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.03)
    min_sphere.translate(min_pt)
    min_sphere.paint_uniform_color([0.0, 1.0, 0.0])

    max_sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.03)
    max_sphere.translate(max_pt)
    max_sphere.paint_uniform_color([1.0, 0.0, 0.0])

    print("What I understood:")
    print("- I applied a color gradient along the Z axis on the clipped mesh.")
    print("- Low Z is blue, high Z is red.")
    print("- I marked the minimum and maximum Z points with spheres.")

    print("\nMesh Z-extrema:")
    print(f"  Min point: {min_pt}")
    print(f"  Max point: {max_pt}")

    show([mesh_colored, min_sphere, max_sphere],
         "Step 7 – Gradient + Extremes (Mesh)")


# =========================================================
# 8) POINT-CLOUD CLIPPING + GRADIENT (FRIEND-STYLE)
# =========================================================
header("8) POINT-CLOUD CLIPPING + GRADIENT (POINT-CLOUD STYLE)")

pcd_points = np.asarray(pcd.points)

if pcd_points.shape[0] == 0:
    print("Point cloud is empty; cannot perform clipping.")
else:
    # use plane parallel to XZ: Y < center[1] (similar idea to your friend)
    y_plane = center[1]
    mask = pcd_points[:, 1] < y_plane
    clipped_points = pcd_points[mask]

    clipped_pcd = o3d.geometry.PointCloud()
    clipped_pcd.points = o3d.utility.Vector3dVector(clipped_points)

    if clipped_points.shape[0] > 0:
        clipped_pcd.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(
                radius=0.1, max_nn=30)
        )

    print("What I understood:")
    print("- Here I clip the point cloud instead of the mesh.")
    print("- I keep only points on one side of a horizontal plane (Y < centerY).")

    print("\nPoint-cloud clipping info:")
    print(f"  Remaining points: {clipped_points.shape[0]}")

    # color gradient on Z (like your friend)
    if clipped_points.shape[0] > 0:
        z_vals = clipped_points[:, 2]
        z_min2, z_max2 = z_vals.min(), z_vals.max()
        range_z = z_max2 - z_min2 if z_max2 != z_min2 else 1.0
        col_t = (z_vals - z_min2) / range_z

        # simple RGB mapping
        colors_pc = np.c_[col_t, 0.5 * col_t, 1.0 - col_t]
        clipped_pcd.colors = o3d.utility.Vector3dVector(colors_pc)

        # extremes
        min_idx2 = int(np.argmin(z_vals))
        max_idx2 = int(np.argmax(z_vals))
        min_pt2 = clipped_points[min_idx2]
        max_pt2 = clipped_points[max_idx2]

        sphere_min2 = o3d.geometry.TriangleMesh.create_sphere(radius=0.05)
        sphere_min2.translate(min_pt2)
        sphere_min2.paint_uniform_color([1, 0, 0])   # red

        sphere_max2 = o3d.geometry.TriangleMesh.create_sphere(radius=0.05)
        sphere_max2.translate(max_pt2)
        sphere_max2.paint_uniform_color([0, 1, 0])   # green

        print("Extra understanding (point-cloud style):")
        print("- I also apply a Z-based color gradient on the clipped point cloud.")
        print("- I mark lowest and highest Z points with red/green spheres.")

        print("\nPoint-cloud Z-extrema:")
        print(f"  Min point: {min_pt2}")
        print(f"  Max point: {max_pt2}")

        show([clipped_pcd, sphere_min2, sphere_max2],
             "Step 8 – Clipped Point Cloud + Gradient + Extremes")
    else:
        print("No points survived clipping; cannot color/mark extremes.")

print("\nPipeline finished successfully.")
