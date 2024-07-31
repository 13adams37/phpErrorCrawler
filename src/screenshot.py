import asyncio
import os
import traceback
import logging
from pyppeteer import launch
from pyppeteer.errors import TimeoutError, NetworkError, PageError


async def fetch(browser, url, path, issue_number) -> tuple[str, bytes]:
    async def return_screenshot(page, path, issue_number):
        screen = await page.screenshot({"path": path, "fullPage": True, "type": "png"})
        return (issue_number, screen)

    page = await browser.newPage()

    try:
        await page.goto(f"{url}", {"waitUntil": "load"})
    except (TimeoutError, NetworkError, PageError):
        return (issue_number, "Без скриншота")
    except Exception:
        traceback.print_exc()
    else:
        return await return_screenshot(page, path, issue_number)
    finally:
        await page.close()


async def main(datas, path) -> list[dict]:
    tasks = []

    browser = await launch(
        headless=True, args=["--no-sandbox"]
    )  # https://github.com/pyppeteer/pyppeteer/issues/463 # https://commondatastorage.googleapis.com/chromium-browser-snapshots/index.html?prefix=Win_x64/1267552/

    for data in datas:
        screenshot_path = f"{path}{data['id']}.png"
        tasks.append(
            asyncio.create_task(
                fetch(browser, data["url"], screenshot_path, data["id"])
            )
        )
        data["screenshot"] = screenshot_path

    for coro in asyncio.as_completed(tasks):
        await coro  # issue_number, screen

    await browser.close()
    return datas


def make_screenshots(data, save_path) -> list[dict]:
    pyppeteer_level = logging.WARNING  # disable pypeteer logging
    logging.getLogger("pyppeteer").setLevel(pyppeteer_level)
    logging.getLogger("websockets.protocol").setLevel(pyppeteer_level)
    logging.getLogger("websockets.client").setLevel(pyppeteer_level)
    logging.getLogger("urllib3.connectionpool").setLevel(
        pyppeteer_level
    )  # yadisk logging to pyppeteer

    current_directory = os.getcwd()
    final_directory = os.path.join(current_directory, f"projects/{save_path}")

    if not os.path.exists(final_directory):
        os.makedirs(final_directory)

    return asyncio.run(main(data, f"projects/{save_path}"))
