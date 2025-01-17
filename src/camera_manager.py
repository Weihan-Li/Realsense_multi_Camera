import pyrealsense2 as rs
from typing import List, Dict, Optional
import threading
from .camera_controller import CameraController
from utils import Logger


class CameraManager:
    """Manages multiple RealSense cameras connected via USB."""

    def __init__(self, logger: Optional[Logger] = None) -> None:
        """
        Initialize camera manager.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or Logger("CameraManager")
        self.cameras: Dict[str, CameraController] = {}
        self._lock = threading.Lock()

    @property
    def device_count(self) -> int:
        """Get the number of connected cameras."""
        return len(self.cameras)

    def discover_cameras(self):
        """
        Discover all connected RealSense cameras.

        Returns:
            List of dictionaries containing camera information
        """
        camera_info = []
        ctx = rs.context()

        for device in ctx.query_devices():
            serial = device.get_info(rs.camera_info.serial_number)
            info = {
                'serial': serial,
                'name': device.get_info(rs.camera_info.name),
                'firmware_version': device.get_info(rs.camera_info.firmware_version),
                'usb_port': device.get_info(rs.camera_info.usb_type_descriptor)
            }
            camera_info.append(info)
            self.logger.info(f"Discovered camera: {info}")

        return camera_info

    def initialize_cameras(self, config: Dict) -> None:
        """
        Initialize all discovered cameras with given configuration.

        Args:
            config: Camera configuration dictionary
        """
        camera_info = self.discover_cameras()

        for info in camera_info:
            try:
                controller = CameraController(
                    serial_number=info['serial'],
                    config=config,
                    logger=self.logger
                )
                self.cameras[info['serial']] = controller
                self.logger.info(f"Initialized camera {info['serial']}")
            except Exception as e:
                self.logger.error(f"Failed to initialize camera {info['serial']}: {str(e)}")

    def start_capture(self) -> None:
        """Start capture on all initialized cameras."""
        threads = []
        for serial, controller in self.cameras.items():
            thread = threading.Thread(
                target=controller.start_capture,
                name=f"Camera_{serial}"
            )
            threads.append(thread)
            thread.start()
            self.logger.info(f"Started capture thread for camera {serial}")

        for thread in threads:
            thread.join()

    def stop_capture(self) -> None:
        """Stop capture on all cameras."""
        for serial, controller in self.cameras.items():
            controller.stop_capture()
            self.logger.info(f"Stopped capture for camera {serial}")