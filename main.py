from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from scrapy.http import HtmlResponse    
import requests
from pathlib import Path
import csv
import os
import sys


def extraction(url):
    with sync_playwright() as sync_playwright_instance:
        browser = sync_playwright_instance.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 1024}, accept_downloads=True,
                                        java_script_enabled=True, ignore_https_errors=True)
        page = context.new_page()
        stealth_sync(page)
        Path("output").mkdir(parents=True, exist_ok=True)
        if not os.path.exists(f'output/output.csv'):
            with open(f'output/output.csv', 'w', newline = '') as wd:
                out = csv.writer(wd)
                out.writerow(["Product_name", "Categories", "Model_no", "Tcin_id", "Specifications", "Description", "Variant", "Price", "Discount_price", "Sellers"])
        
        page.goto(url)
        page.wait_for_load_state('networkidle', timeout=30000)    
        page.wait_for_load_state('domcontentloaded', timeout=30000)        
        print('URL loaded Successfully') 
        try:
            available = page.locator('//*[contains(text(), "This item is not available")]').inner_text()
            if 'This item is not available' in available:
                print('Item Not Available')
                sys.exit()
        except:
            pass    
        page.locator('//h3[contains(text(), "Specifications")]').click()
        page.wait_for_load_state('domcontentloaded', timeout=30000)   
        response = HtmlResponse(url='https://www.example.com', body=page.content(), encoding='utf-8')
        Product_name = response.xpath('//*[@id="pdp-product-title-id"]/text()').get(default='')
        Categories = '/'.join(i.strip() for i in response.xpath('//*[@data-module-type="ProductDetailBreadcrumbs"]/div/nav/ol/li/a/text()').getall())
        # Model_no = response.xpath('').get()
        Tcin_id = response.xpath('//b[contains(text(), "TCIN")]/following-sibling::text()').get(default='').replace(':','').strip()  
        specifications_keys = [i.replace(':','') for i in response.xpath('//*[@id="product-detail-tabs"]/div/div[2]/div/div/div/div/div[1]/div/div/b/text() | //*[@id="product-detail-tabs"]/div/div[2]/div/div/div/div/div[1]/div/b/text()').getall()]
        specifications_values = [i.replace(':','').strip() for i in response.xpath('//*[@id="product-detail-tabs"]/div/div[2]/div/div/div/div/div[1]/div/div/b/following-sibling::text() | //*[@id="product-detail-tabs"]/div/div[2]/div/div/div/div/div[1]/div/b/following-sibling::text()').getall()]
        Specifications = {key:val for key, val in zip(specifications_keys,specifications_values)}
        Description = response.xpath('//div[@data-test="item-details-description"]/text()').get(default='')    
        Variant = response.xpath('//*[@data-test="@web/VariationComponent"]/div/span/following-sibling::text()').get(default='')
        Price = response.xpath('//*[@data-test="product-price"]/text()').get(default='')
        Discount_price = response.xpath('//*[@data-test="product-savings-amount"]/text()').get(default='')
        Sellers = response.xpath('//*[contains(text()," Sold & shipped by")]/following-sibling::div/text()[2]').get(default='')    
        page.wait_for_timeout(10000)
        page.locator('//*[@data-test="icon-expand-item-0"]').click()
        print('Downloading Images')
        page.wait_for_load_state('networkidle', timeout=30000)    
        page.wait_for_load_state('domcontentloaded', timeout=30000)    
        total_img = page.locator('//*[@data-test="image-gallery-modal"]/nav/button/div/div/div/picture/img').count()
        Path(f"output/downloaded_image/{Tcin_id}").mkdir(parents=True, exist_ok=True)
        for i in range(1, total_img+1):
            image_url = page.locator(f'//*[@data-test="image-gallery-modal"]/nav/button[{i}]/div/div/div/picture/img').get_attribute('src')
            response = requests.get(image_url)
            if response.status_code == 200:
                with open(f"output/downloaded_image/{Tcin_id}/{i}.jpg", "wb") as file:
                    file.write(response.content)
                print("Image successfully downloaded!")
            else:
                print("Failed to retrieve the image. HTTP Status code:", response.status_code)
        alldata = [Product_name, Categories, 'Not Available' , Tcin_id, Specifications, Description, Variant, Price, Discount_price, Sellers]
        with open(f'output/output.csv', "a", newline="") as wd:
                        wr = csv.writer(wd)
                        wr.writerow(alldata)
                        wd.close()
    return "Extraction Completed Successfully"


if __name__ == "__main__":
    url = 'https://www.target.com/p/hp-inc-pavilion-laptop-computer-16-2k-amd-ryzen-7-16-gb-memory-512-gb-ssd-windows/-/A-93168825#lnk=sametab'
    extraction(url)
