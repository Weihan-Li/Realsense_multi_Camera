import pyrealsense2 as rs
from typing import Dict, Optional
from utils import Logger
from .data_capture import DataCapture
import cv2

class CameraController:
    """Controls individual RealSense camera operations."""

    def __init__(
            self,
            serial_number: str,
            config: Dict,
            logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize camera controller.

        Args:
            serial_number: Camera serial number
            config: Camera configuration
            logger: Optional logger instance
        """
        self.serial_number = serial_number
        self.config = config
        self.logger = logger or Logger(f"Camera_{serial_number}")
        self.pipeline = rs.pipeline()
        self.data_capture = DataCapture(serial_number, logger=self.logger)
        self._running = False

    def _configure_pipeline(self) -> None:
        """Configure the RealSense pipeline with settings from config."""
        cfg = rs.config()
        cfg.enable_device(self.serial_number)

        # Configure streams
        cfg.enable_stream(
            rs.stream.color,
            self.config.get('color_width', 640),
            self.config.get('color_height', 480),
            rs.format.bgr8,
            self.config.get('fps', 30)
        )

        cfg.enable_stream(
            rs.stream.depth,
            self.config.get('depth_width', 640),
            self.config.get('depth_height', 480),
            rs.format.z16,
            self.config.get('fps', 30)
        )

        # Start pipeline
        pipeline_profile = self.pipeline.start(cfg)

        # Apply advanced settings
        dev = pipeline_profile.get_device()
        depth_sensor = dev.first_depth_sensor()

        if self.config.get('laser_power') is not None:
            depth_sensor.set_option(
                rs.option.laser_power,
                self.config['laser_power']
            )

        if self.config.get('depth_units') is not None:
            depth_sensor.set_option(
                rs.option.depth_units,
                self.config['depth_units']
            )

    def start_capture(self) -> None:
        """Start capturing data from the camera."""
        try:
            self._configure_pipeline()
            self._running = True
            self.logger.info(f"Started capture for camera {self.serial_number}")

            while self._running:
                frames = self.pipeline.wait_for_frames()
                self.data_capture.process_frames(frames)

        except Exception as e:
            self.logger.error(f"Error during capture: {str(e)}")
            self._running = False
        finally:
            self.pipeline.stop()

    def stop_capture(self) -> None:
        """Stop capturing data."""
        self._running = False
        self.logger.info(f"Stopped capture for camera {self.serial_number}")