import logging
from nodejs import npm, node

logger = logging.getLogger(__name__)

async def js2py(code, layout, theme):
    try:
        # Run 'npm install' with Node.js
        result = npm.run(['install'], capture_output=True, text=True)

        # Log the standard output
        logger.info("npm install Standard Output:")
        logger.info(result.stdout)

        # Log the error output
        if result.stderr:
            logger.error("npm install Error Output:")
            logger.error(result.stderr)

        # Run the JavaScript code with Node.js
        result = node.run(['d2_playwright.js', code, layout, theme], capture_output=True, text=True)
    except Exception as e:
        logger.error(f"Error running JS code: {str(e)}")
        return {"error": "An error occurred while running the JavaScript code."}