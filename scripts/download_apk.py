import argparse
import re
from time import sleep
import requests
from playwright.sync_api import sync_playwright


parser = argparse.ArgumentParser()
parser.add_argument('-s', '--server', choices=['cn', 'en'], default='cn')
args = parser.parse_args()

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.81"


def main():
    retries = 5
    for attempt in range(retries):
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                context = browser.new_context(user_agent=user_agent)
                page = context.new_page()

                if args.server == 'cn':
                    page.goto("https://www.biligame.com/detail/?id=101772", wait_until="networkidle", timeout=90000)
                    content = page.content()
                    matches = re.findall(r'<a href="https://pkg\.bili[^"]+\.apk', content)
                    download_url = re.sub(r'^.*href="', '', matches[0])

                    with page.expect_download() as download_info:
                        try:
                            page.goto(download_url, timeout=90000)
                        except Exception as e:
                            if (not "Page.goto: net::ERR_ABORTED at" in str(e)):
                                raise e
                    download = download_info.value
                    print(download.url)
                    download.save_as(f"./{args.server}.apk")

                elif args.server == 'en':
                    with page.expect_download() as download_info:
                        try:
                            page.goto("https://d.apkpure.com/b/XAPK/com.YoStarEN.Arknights?version=latest", timeout=90000)
                        except Exception as e:
                            if (not "Page.goto: net::ERR_ABORTED at" in str(e)):
                                raise e
                    download = download_info.value
                    print(download.url)
                    download.save_as(f"./{args.server}.apk")

                browser.close()
                break
        except Exception as e:
            if attempt == retries - 1:
                print(f'Failed to download apk after {retries} attempts.')


if __name__ == "__main__":
    main()
