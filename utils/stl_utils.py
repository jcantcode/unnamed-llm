import random
import open3d as o3d
import numpy as np
import os


class VisualizerWindow:
    def __init__(self, width=768, height=768, visible=False):
        """
        Initialize the VisualizerWindow.

        Args:
            width (int, optional): The width of the window. Defaults to 768.
            height (int, optional): The height of the window. Defaults to 768.
            visible (bool, optional): Whether the window is visible or not. Defaults to False.
        """
        self.width = width
        self.height = height
        self.visible = visible

    def __enter__(self):
        """
        Create the visualization window upon entering the context.

        Returns:
            o3d.visualization.Visualizer: The created Visualizer object.
        """
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window(visible=self.visible, width=self.width, height=self.height)
        return self.vis

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Destroy the visualization window upon exiting the context.
        """
        self.vis.destroy_window()

class STLRenderer:
    def __init__(self, output_folder, angles=9, render_options=None):
        """
        Initialize the STLRenderer.

        Args:
            output_folder (str): The output folder for saving rendered images.
            angles (int, list of tuple, optional): The number of angles or a list of 3-tuple angles for rendering. Defaults to 9.
            render_options (dict, optional): Custom render options. Defaults to None.
        """
        self.output_folder = output_folder
        if type(angles) == int:
            assert angles > 0, 'angles should be a positive integer'
            self.num_angles = angles
        elif type(angles) == list:
            # should be a list of 3-tuples
            assert all([len(angle) == 3 for angle in angles]) and all([type(angle) == tuple for angle in angles]), 'angles should be a list of 3-tuples'
            assert all([all([type(a) == float for a in angle]) for angle in angles]), 'angles should be a list of 3-tuples of floats'
            self.angles = angles
            self.num_angles = len(angles)
            
        self.render_options = render_options
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def render(self, stl_file_path):
        """
        Render the STL file at different angles and save the images to the output folder.

        Args:
            stl_file_path (str): The path to the STL file to be rendered.
        """
        assert os.path.exists(stl_file_path) and os.path.isfile(stl_file_path), f"File {stl_file_path} does not exist"
        mesh = o3d.io.read_triangle_mesh(stl_file_path)
        mesh.compute_vertex_normals()

        with VisualizerWindow() as vis:
            vis.add_geometry(mesh)
            self.setup_render_option(vis)
            self.setup_camera(vis, mesh)

            for i in range(self.num_angles):
                a, b, c = self.get_angles(i)
                matrix = o3d.geometry.get_rotation_matrix_from_xyz((a, b, c))
                mesh.rotate(matrix, mesh.get_axis_aligned_bounding_box().get_center())
                vis.update_geometry(mesh)
                output_image_path = os.path.join(self.output_folder, f"angle_{i}.png")
                vis.capture_screen_image(output_image_path, do_render=True)

    def setup_camera(self, vis, mesh):
        """
        Set up the camera view for the visualization.

        Args:
            vis (o3d.visualization.Visualizer): The Visualizer object.
            mesh (o3d.geometry.TriangleMesh): The mesh to be rendered.
        """
        bounding_box = mesh.get_axis_aligned_bounding_box()
        camera_distance = bounding_box.get_extent().max() * 2
        center = bounding_box.get_center()
        view_control = vis.get_view_control()
        view_control.set_lookat(center)
        view_control.set_up([0, 1, 0])
        view_control.set_front([0, 0, -1])
        view_control.set_zoom(camera_distance)

    def setup_render_option(self, vis):
        """
        Set up the render options for the visualization.

        Args:
            vis (o3d.visualization.Visualizer): The Visualizer object.
        """
        render_option = vis.get_render_option()
        if self.render_options is None:
            render_option.background_color = np.asarray([1, 1, 1])
            render_option.mesh_show_back_face = True
            render_option.mesh_show_wireframe = True
            render_option.mesh_shade_option = o3d.visualization.MeshShadeOption.Color
        else:
            for key, value in self.render_options.items():
                setattr(render_option, key, value)

    def get_angles(self, i):
        """
        Get the angles for the current rotation.

        Returns:
            tuple: A 3-tuple of angles (a, b, c).
        """
        if hasattr(self, "angles"):
            return self.angles[i]
        return random.uniform(0, 2*np.pi), random.uniform(0, 2*np.pi), random.uniform(0, 2*np.pi)


if __name__ == "__main__":
    # Example usage with custom render options:

    stl_file_path = "tests/test.stl"
    output_folder = "test_output"
    custom_render_options = {
        "mesh_show_back_face": False,
        "mesh_show_wireframe": False,
        "mesh_shade_option": o3d.visualization.MeshShadeOption.Color
    }
    renderer = STLRenderer(output_folder, render_options=custom_render_options)
    renderer.render(stl_file_path)
