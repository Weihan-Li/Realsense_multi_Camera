import argparse
import yaml
from src.camera_manager import CameraManager
from utils.logger import Logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='RealSense Multi-Camera Capture System')

    # Basic settings
    parser.add_argument('--config', type=str, default='config/capture_config.yaml',
                        help='Path to configuration file')
    parser.add_argument('--output', type=str, default='dataset',
                        help='Output directory for captured data')

    # Camera settings
    parser.add_argument('--fps', type=int, help='Frame rate override')
    parser.add_argument('--laser-power', type=float,
                        help='Laser power setting (0-360)')
    parser.add_argument('--depth-units', type=float,
                        help='Depth units in meters')

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logger = Logger("Main")

    try:
        # Load configuration
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)

        # Override config with command line arguments
        if args.fps:
            config['fps'] = args.fps
        if args.laser_power:
            config['laser_power'] = args.laser_power
        if args.depth_units:
            config['depth_units'] = args.depth_units

        # Initialize camera manager
        manager = CameraManager(logger=logger)
        manager.initialize_cameras(config)

        if manager.device_count == 0:
            logger.error("No cameras found!")
            return

        # Start capture
        logger.info("Starting capture...")
        manager.start_capture()

    except KeyboardInterrupt:
        logger.info("Capture interrupted by user")
        manager.stop_capture()
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
    finally:
        logger.info("Capture complete")


if __name__ == "__main__":
    main()
