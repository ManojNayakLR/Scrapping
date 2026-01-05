from playwright.sync_api import sync_playwright
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
        page.wait_for_load_state('networkidle', timeout=60000)    
        page.wait_for_load_state('domcontentloaded', timeout=60000)    
        total_img = page.locator('//*[@data-test="image-gallery-modal"]/nav/button/div/div/div/picture/img').count()
        Path(f"output/downloaded_image/{Tcin_id}").mkdir(parents=True, exist_ok=True)
        for i in range(1, total_img+1):
            image_url = page.locator(f'//*[@data-test="image-gallery-modal"]/nav/button[{i}]/div/div/div/picture/img').get_attribute('src')
            response = requests.get(image_url)
            if response.status_code == 200:
                with open(f"output/downloaded_image/{Tcin_id}/{i}.jpg", "wb") as file:
                    file.write(response.content)
                print("Image downloaded successfully !")
            else:
                print("Failed to retrieve the image. HTTP Status code:", response.status_code)
        alldata = [Product_name, Categories, 'Not Available' , Tcin_id, Specifications, Description, Variant, Price, Discount_price, Sellers]
        with open(f'output/output.csv', "a", newline="") as wd:
            wr = csv.writer(wd)
            wr.writerow(alldata)
            wd.close()
    return "Extraction Completed Successfully"


if __name__ == "__main__":
    url = 'https://www.target.com/p/hp-inc-pavilion-laptop-computer-13-3-2k-amd-ryzen-7-16-gb-memory-512-gb-ssd/-/A-93168695#lnk=sametab'
    extraction(url)


import sys
import time
import random
import os
# from fake_useragent import UserAgent
from playwright.sync_api import sync_playwright, expect
# from DATA_EXTRACTION.TDEX.Utilities import Common
# from DATA_EXTRACTION.TDEX.Utilities.Common import create_folder_if_not_exists, solve_recaptcha, add_time
# from .DataExtractor import input_fields, table_extractor, details_extractor
# from DATA_EXTRACTION.TDEX.Utilities.dynamodb import dblogs, dbstatus

# ua = UserAgent()

def mineral(**kwargs):
    username = 'username'
    password = 'user@123'
    retry = 1

    json_data = kwargs["config"]
    type = kwargs["search_type"]
    download_doc = kwargs["download_documents"]
    job_id = str(kwargs['job_id'])
    job_id_output_path = kwargs['job_id_output_path']
    screenshot_path = f"{job_id_output_path}{os.sep}Screenshots{os.sep}"
    # create_folder_if_not_exists(screenshot_path)
    
    with sync_playwright() as sync_playwright_instance:
        # dblogs("Setting up Extraction Environment!",job_id)
        browser = sync_playwright_instance.chromium.launch(
            args=['--no-sandbox', '--single-process', '--disable-dev-shm-usage', '--no-zygote'],
            # args=['--no-sandbox', '--no-zygote'],
            headless=True,
            # executable_path=sync_playwright_instance.chromium.executable_path,
            executable_path="/pw-browsers/chromium-1000/chrome-linux/chrome",
            channel='chrome',
            proxy={'server': Common.proxy_dic['server'],
                    'username': Common.proxy_dic['username'],
                    'password': Common.proxy_dic['password']},
            timeout=60000
        )
        context = browser.new_context(no_viewport=False, accept_downloads=True,user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36')
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

        # dbstatus('1', job_id)
 

        page = context.new_page()
        url = "https://records.mineralcountynv.us/web/user/disclaimer"
        # dblogs("NV-Mineral County Recorder Search Initiated!!",job_id)
        # dblogs(f"Loading Home Page of NV-Mineral",job_id)

        while retry <= 5:
            try:
                page.goto(url,wait_until='load', timeout=30000)
                page.wait_for_load_state('networkidle',timeout=30000)
                
                try:
                    expect(page.frame_locator("//iframe[contains(@title,'reCAPTCHA')]").locator(
                        "//label[contains(@class,'rc-anchor-center-item rc-anchor-checkbox-label')]")).to_contain_text(
                        "I'm not a robot", timeout=30000)

                    _re(username, password, page,job_id)
                except:
                    pass
                    page.locator("//button[contains(text(),'I Accept')]").click()
                page.wait_for_timeout(timeout=5000)
                expect(page.locator('(//*[contains(@class,"ui-block-b-uneven")]/div/a/div/h1)[2]')).to_contain_text('Document Search and Copies - Web', timeout=40000)
                page.locator('(//*[contains(@class,"ui-block-b-uneven")]/div/a/div/h1)[2]').click()
                time.sleep(2)
                expect(page.locator("//*[contains(text(),'Either Party')]")).to_contain_text('Either Party', timeout=40000)
                break
            except Exception as e:
                pass

            if retry >= 5:
                # dblogs("NV-Mineral County Recorder website maybe facing downtime, please try in sometime!",job_id)
                sys.exit()

            retry += 1
        
        # dblogs(f'Loaded NV-Mineral Home Page; URL: {url}',job_id)
        # dblogs('Taking screenshot of Home Page',job_id)
        page.screenshot(path=f"{screenshot_path}Home_Page.png", full_page=True)
        img_path = f"{screenshot_path}Home_Page.png"
        # add_time(img_path)

        # input_fields(page, json_data, screenshot_path,job_id)

        # if type == "S":
        #     table_extractor(page, job_id, job_id_output_path, screenshot_path, json_data )
        # else:
        #     details_extractor(page, job_id, download_doc, job_id_output_path, screenshot_path,json_data)

        


def _re(username, password, page,job_id):
    try:
        site_key = page.locator("//div[contains(@class,'g-recaptcha center')]").get_attribute('data-sitekey', timeout=30000)
        print("Recaptcha appeared on Search!!")
        url = page.url
        wait = random.randint(10, 20)
        time.sleep(wait)
        recaptcha_response = solve_recaptcha(username, password, site_key, url)
        time.sleep(3)
        page.evaluate(f"document.getElementById('g-recaptcha-response').innerHTML = `{recaptcha_response['text']}`")
        page.evaluate(f"onReturnRecaptchaCallback();")
        count = 1
        while count < 5:
            if count < 4:
                page.locator('//*[@id="submitDisclaimerAccept"]').click()
                time.sleep(2)
                try:
                    expect(page.locator("//li[contains(@class,'ui-li-divider ui-bar-a ui-first-child')]")).to_contain_text('Home Instructions', timeout=25000)
                    return "Recaptcha Solved Successfully!!"
                except Exception as e:
                    count = count + 1
            else:
                # dblogs('Failed to Solve Recaptcha, even with 5 attempts!!',job_id)
                break

    except Exception as e:
        print('Recaptcha Not found')
