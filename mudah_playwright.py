import asyncio
from playwright.async_api import async_playwright
import csv

async def scrape_page(page):
    # Scrape the current page
    all_products = await page.query_selector_all('[data-testid^="listing-ad-item-"]') # selector for list items 
    data = []
    for product in all_products:
        result = dict()

        title_el = await product.query_selector('a[title]') # title class selector
        if title_el:
            result['title'] = await title_el.get_attribute('title')  # Get the value of the 'title' attribute
        else:
            result['title'] = "Title not found"
        # result['title'] = await title_el.inner_text() if title_el else None

        # price_el = await product.query_selector('.sc-iQKALj.fWRVpF') # not dynamic
        # result['price'] = await price_el.inner_text() if price_el else None

        price_el = await product.query_selector('//div[contains(text(), "RM")]')
        if price_el:
            result['price'] = await price_el.inner_text()  # Get the inner text (price value)
        else:
            result['price'] = "Price not found"

        makeYear_el = await product.query_selector('div.flex.items-center.gap-1[title="Manufactured Year"]') #using css selector, not dynamic
        result['make year'] = await makeYear_el.inner_text() if makeYear_el else None
        #__next > div.mw334.mw5 > div.sc-iRbamj.jAbOwE > div.sc-jlyJG.fMNGsa > div:nth-child(3) > div.sc-kIPQKe.kNClJo > div.gap-2.grid.grid-cols-2.mt-2 > div:nth-child(2)
       
        data.append(result)

    return data

def export_to_csv(data, filename='motorcycles.csv'):
    # Open the CSV file in write mode
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        # Create a CSV writer object
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        
        # Write the header (fieldnames)
        writer.writeheader()
        
        # Write the data (rows)
        writer.writerows(data)

async def scrape_multiple_pages(limit=3):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Visit the first page
        await page.goto('https://www.mudah.my/malaysia/motorcycles-for-sale')
        await page.wait_for_timeout(5000)  # Wait for the page to load

        all_data = []
        pages_scraped = 0

        # Scrape the first page
        data = await scrape_page(page)
        all_data.extend(data)
        pages_scraped += 1


        # Try to navigate to the next page and scrape it
        while pages_scraped < limit:
            next_button = await page.query_selector('.mw459[data-testid="pagination-next"]')  # Updated selector for the next button
            if next_button:
                await next_button.click()
                await page.wait_for_timeout(5000)  # Wait for the page to load

                # Scrape the next page
                data = await scrape_page(page)
                all_data.extend(data)
                pages_scraped += 1
            else:
                break  # No more next page

        # export_to_csv(all_data, 'motorcycles.csv')

        print(f"Scraped {pages_scraped} pages.")
        print(all_data)
        print(len(all_data))
        await browser.close()

asyncio.run(scrape_multiple_pages(limit=3))
