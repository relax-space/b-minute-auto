import asyncio
import json
import logging
import os
import random
import time
import traceback
from typing import List

from pyppeteer import launch


async def page_evaluate(page):
    # 替换淘宝在检测浏览时采集的一些参数
    await page.evaluate('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
    await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
    await page.evaluate('''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
    await page.evaluate('''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')


def get_ua_list() -> List:
    return read_list("ua_fake.json")


def read_list(path, mode="rt", encoding='utf-8', object_hook=None) -> List:
    ips = None
    with open(path, mode, encoding=encoding) as fp:
        if object_hook == None:
            ips = json.load(fp)
        else:
            ips = json.load(fp, object_hook=object_hook)
    return ips


async def tcp_hour(chromium_drive: str, waitfortime: int):
    try:
        # 'headless': False如果想要浏览器隐藏更改False为True
        print('进来了')
        browser = None
        if not chromium_drive:
            browser = await launch({
                'headless': True,
                'args': ['--no-sandbox',
                         '--disable-gpu'],
                'dumpio': True})
        else:
            browser = await launch({
                'headless': True,
                'executablePath': chromium_drive,
                'args': ['--no-sandbox',
                         '--disable-gpu'],
                'dumpio': True})
        context = await browser.createIncognitoBrowserContext()  # 开启无痕浏览器模式
        page = await context.newPage()
        await page.setViewport({'width': 1920, 'height': 1080})
        ua = random.choice(get_ua_list())
        await page.setUserAgent(ua)
        await asyncio.gather(
            page.goto(f"https://www.bilibili.com/video/BV1q7411J7AG"),
            page.waitForNavigation(),
        )
        await page.waitForSelector(
            '#multi_page > div.cur-list > ul > li.watched.on > a > div > div.link-content')
        fileName = '口译笔记符号教程'
        for i in range(1, 27):
            td = await page.Jeval(f'#multi_page > div.cur-list > ul > li:nth-child({i}) > a > div > div.link-content',
                                  '(n => ({"key":n.firstChild.nextElementSibling.innerText,"value":n.nextElementSibling.innerText}))')
            print(td)
            with open(f'data/{fileName}.txt', 'a') as f:
                f.write(td.get('key') +
                        ' '+td.get('value') + "\n")

    except Exception as e:
        logging.error(f'exception:{traceback.format_exc()}')
        raise e
    finally:
        await page.close()
        await context.close()
        await browser.close()


if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s - %(levelname)s - %(message)s")
        chromium_drive = os.getenv('chromium_drive')
        waitfortime = 2000 if not os.getenv(
            'waitfortime') else int(os.getenv('waitfortime'))
        task = asyncio.get_event_loop().run_until_complete(
            tcp_hour(chromium_drive, waitfortime))
        print(task)
    except Exception as e:
        logging.error(f'exception:{traceback.format_exc()}')
