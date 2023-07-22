const chrome = require('chrome-aws-lambda');
const express = require('express');
const playwright = require('playwright-core');
const url = require('url');
const querystring = require('querystring');
const logger = console;

async function selectTheme(page, themeName) {
    logger.log("About to click theme button");
    const themeButton = await page.$('#theme-btn');
    await themeButton.click();

    logger.log("About to select theme");
    const themeOption = await page.$(`text=${themeName}`);
    await themeOption.click();
}

async function runPlaywright(code, layout, theme) {
    logger.log(`Running Playwright with code: ${code}`);
    const browser = await playwright.chromium.launch({
        args: chrome.args,
        defaultViewport: chrome.defaultViewport,
        executablePath: await chrome.executablePath,
        headless: chrome.headless,
    });
    const page = await browser.newPage();
    await page.goto('https://play.d2lang.com');
    logger.log("Page loaded");

    logger.log("About to write code");
    await page.waitForSelector('#editor-main > div > div.overflow-guard > textarea');
    const codeEditor = await page.$('#editor-main > div > div.overflow-guard > textarea');
    await codeEditor.type(code);

    logger.log("About to click compile button");
    await page.waitForSelector('#compile-btn');
    const compileButton = await page.$('#compile-btn');
    await compileButton.click();

    await page.waitForSelector('#theme-btn');

    if (theme !== "Neutral default") {
        await selectTheme(page, theme);
    } else {
        logger.log("Not selecting theme");
        theme = "0";
    }

    const newUrl = page.url();
    logger.log("About to create render URL");
    const renderUrl = createRenderUrl(newUrl, layout);

    await browser.close();

    return {renderUrl, code};
}

function createRenderUrl(pageUrl, layout) {
    logger.log("About to parse URL");
    const parsedUrl = url.parse(pageUrl);
    const query = querystring.parse(parsedUrl.query);
    const script = query['script'][0];
    let theme;
    try {
        theme = query['theme'][0];
    } catch (error) {
        theme = "0";
    }
    layout = layout || "elk" || "dagre";
    logger.log(`Script: ${script}, theme: ${theme}`);

    return `https://api.d2lang.com/render/svg?script=${script}&layout=${layout}&theme=${theme}&sketch=0`;
}

// Get command line arguments
const args = process.argv.slice(2);
const code = args[0] || 'your code here';
const layout = args[1] || 'elk';
const theme = args[2] || 'Neutral gray';

runPlaywright(code, layout, theme).then(console.log);