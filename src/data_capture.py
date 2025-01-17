import pyrealsense2 as rs
import numpy as np
from typing import Optional
from pathlib import Path
import json
from datetime import datetime
import open3d as o3d
from utils.logger import Logger
import cv2


class DataCapture:
    """Handles data capture and storage from RealSense cameras."""

    def __init__(
            self,
            camera_id: str,
            base_path: str = "dataset",
            logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize data capture handler.

        Args:
            camera_id: Camera identifier
            base_path: Base path for data storage
            logger: Optional logger instance
        """
        self.camera_id = camera_id
        self.logger = logger or Logger(f"DataCapture_{camera_id}")
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.frame_count = 0

        # Setup directory structure
        self.base_dir = Path(base_path) / self.timestamp / f"camera_{camera_id}"
        for subdir in ['color', 'depth', 'pointcloud/ply', 'pointcloud/pcd']:
            (self.base_dir / subdir).mkdir(parents=True, exist_ok=True)

        # Save metadata
        self._save_metadata()

    def _save_metadata(self) -> None:
        """Save camera metadata to JSON file."""
        metadata = {
            'camera_id': self.camera_id,
            'timestamp': self.timestamp,
            'capture_start': datetime.now().isoformat()
        }

        with open(self.base_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=4)

    def process_frames(self, frames: rs.composite_frame) -> None:
        """
        Process and save frame data.

        Args:
            frames: Composite frame from RealSense camera
        """
        try:
            # Extract frames
            color_frame = frames.get_color_frame()
            depth_frame = frames.get_depth_frame()

            if not color_frame or not depth_frame:
                return

            # Convert to numpy arrays
            color_image = np.asanyarray(color_frame.get_data())
            depth_image = np.asanyarray(depth_frame.get_data())

            # Save color and depth images
            frame_name = f"{self.frame_count:06d}"
            color_path = self.base_dir / 'color' / f"{frame_name}.png"
            depth_path = self.base_dir / 'depth' / f"{frame_name}.png"

            cv2.imwrite(str(color_path), color_image)
            self.logger.info(f"Camera {self.camera_id} - Frame {frame_name}: Saved color image")

            cv2.imwrite(str(depth_path), depth_image)
            self.logger.info(f"Camera {self.camera_id} - Frame {frame_name}: Saved depth image")

            # Generate and save point cloud
            pc = rs.pointcloud()
            pc.map_to(color_frame)
            points = pc.calculate(depth_frame)

            # Get vertices and convert to numpy array
            vtx = np.asanyarray(points.get_vertices())
            # Reshape the array to remove the structured array format
            vertices = np.array([(v[0], v[1], v[2]) for v in vtx])

            # Create and save point cloud
            ply_path = self.base_dir / 'pointcloud/ply' / f"{frame_name}.ply"
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(vertices)
            o3d.io.write_point_cloud(str(ply_path), pcd)
            self.logger.info(f"Camera {self.camera_id} - Frame {frame_name}: Saved PLY point cloud")

            # Save as PCD
            pcd_path = self.base_dir / 'pointcloud/pcd' / f"{frame_name}.pcd"
            o3d.io.write_point_cloud(str(pcd_path), pcd)
            self.logger.info(f"Camera {self.camera_id} - Frame {frame_name}: Saved PCD point cloud")

            self.frame_count += 1
        except Exception as e:
            self.logger.error(f"Error processing frame: {str(e)}")