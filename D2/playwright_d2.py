import logging
from playwright.async_api import async_playwright
from urllib.parse import urlparse, parse_qs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def select_theme(page, theme_name: str):
    # Assuming that you click a button to open the theme menu
    logger.info("About to click theme button")
    theme_button = await page.query_selector('#theme-btn')
    await theme_button.click()

    # Now select the theme from the menu
    logger.info("About to select theme")

    theme_option = await page.query_selector(f' text={theme_name}')
    await theme_option.click()

async def run_playwright(code: str, layout: str, theme: str):
    logger.info(f"Running Playwright with code: {code}")
    async with async_playwright() as p:
        logger.info("Running Playwright")
        browser = await p.chromium.launch(args=["--disable-gpu", "--single-process"])
        page = await browser.new_page()
        await page.goto('https://play.d2lang.com')
        logger.info("Page loaded")

        # Find the code editor element and write your code into it
        logger.info("About to write code")
        await page.wait_for_selector('#editor-main > div > div.overflow-guard > textarea')
        code_editor = await page.query_selector('#editor-main > div > div.overflow-guard > textarea')
        await code_editor.fill(code)

        # Click the compile button
        logger.info("About to click compile button")
        await page.wait_for_selector('#compile-btn')
        compile_button = await page.query_selector('#compile-btn')
        await compile_button.click()

        # Wait for the page to compile
        await page.wait_for_selector('#theme-btn')

        # Select theme
        if theme != "Neutral default":
            await select_theme(page, theme)
        else:
            logger.info("Not selecting theme")
            theme = "0"

        # Get the URL of the page after compilation
        new_url = page.url

        # Use the create_render_url function to generate the render URL
        logger.info("About to create render URL")
        render_url = await create_render_url(new_url, layout)

        await browser.close()

        return render_url, code

async def create_render_url(page_url, layout):
    # Extract the script and theme from the URL
    logger.info("About to parse URL")
    parsed_url = urlparse(page_url)
    script = parse_qs(parsed_url.query)['script'][0]
    try:
        theme = parse_qs(parsed_url.query)['theme'][0]
    except KeyError:
        theme = "0"
    layout = layout or "elk" or "dagre"
    logger.info(f"Script: {script}, theme: {theme}")

    return f"https://api.d2lang.com/render/svg?script={script}&layout={layout}&theme={theme}&sketch=0"