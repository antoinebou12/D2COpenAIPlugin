import logging
import subprocess

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_go_script(input_string):
    try:
        # Build the Go script
        build_result = subprocess.run(['go', 'build', 'main.go'], check=True, text=True, capture_output=True)
        logger.info(f"Go script build succeeded with output: {build_result.stdout}")

        # Run the Go script
        run_result = subprocess.run(['./main', 'encode', input_string], check=True, text=True, capture_output=True)
        logger.info(f"Go script run succeeded with output: {run_result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Go script execution failed with error: {e.output}")
