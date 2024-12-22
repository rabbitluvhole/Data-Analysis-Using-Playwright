import asyncio
from playwright.async_api import async_playwright
import csv

async def scrape_page(page):
   
    all_products = await page.query_selector_all('.sc-kIPQKe.kNClJo')
    data = []
    for product in all_products:
        result = dict()

        title_el = await product.query_selector('.sc-eXEjpC.cPVpAp') 
        result['title'] = await title_el.inner_text() if title_el else None

        price_el = await product.query_selector('.sc-iQKALj.fWRVpF')
        result['price'] = await price_el.inner_text() if price_el else None

        makeYear_el = await product.query_selector('div.flex.items-center.gap-1[title="Manufactured Year"]')  # Using CSS selector
        result['make year'] = await makeYear_el.inner_text() if makeYear_el else None
        
        data.append(result)

    return data

def export_to_csv(data, filename='motorcycles.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

async def scrape_single_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        await page.goto('https://www.mudah.my/malaysia/motorcycles-for-sale')
        await page.wait_for_timeout(5000)  

        data = await scrape_page(page)

        export_to_csv(data, 'motorcycles.csv')

        print(f"Scraped {len(data)} listings.")
        print(data)
        await browser.close()

asyncio.run(scrape_single_page())
