
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd

def find_next_page(current_browser):
    try:
        next_buttons = current_browser.find_elements(By.CSS_SELECTOR, "a.re__pagination-icon")
        current_url = current_browser.current_url
        for button in next_buttons:
            next_url = button.get_attribute("href")
            if current_url < next_url:
                return next_url
        return None
    except Exception as e:
        print(f"Error finding next page: {e}")
        return None

def process_1_page(browser,full_data) : 
    try:
        cards = browser.find_elements(by=By.CLASS_NAME,value="js__product-link-for-product-id")
        if len(cards) > 0 : 
            for i in range(len(cards)) : 
                try:
                    url = cards[i].get_attribute("href")
                    if url:
                        
                        new_service = Service(driver_path)
                        new_browser = webdriver.Chrome(service=new_service)

                        new_browser.get(url)
                        process_1_ad(new_browser,full_data)
                        time.sleep(20)
                        
                        new_browser.quit()
                except Exception as e:
                    print(f"Error processing card: {e}")
        new_url = find_next_page(browser)            
        return new_url
    except Exception as e:
        print(f"Error finding cards: {e}")


def process_1_ad(browser_ad,full_data:dict ) : 
    title = browser_ad.find_element(By.CSS_SELECTOR, "h1.re__pr-title.pr-title.js__pr-title")
    if title : 
        full_data['title'].append(title.text)
    else : full_data['title'].append(None)

    address = browser_ad.find_element(By.CSS_SELECTOR, ".re__pr-short-description.js__pr-address")
    if address : 
        full_data['address'].append(address.text)
    else : full_data['address'].append(None)
    
    description = browser_ad.find_element(By.CSS_SELECTOR,"div.re__section-body.re__detail-content.js__section-body.js__pr-description.js__tracking")
    if description : 
        full_data['description'].append(description.text)
    else : full_data['description'].append(None)    

    features = browser_ad.find_elements(By.CLASS_NAME,"re__pr-specs-content-item")
    features_name = {'Diện tích':'size','Mức giá':'price_string','Hướng nhà':'direction','Hướng ban công':'balcony_direction','Số phòng ngủ':'bedrooms','Số toilet':'toilets','Pháp lý':'duty','Nội thất':'furniture'}
    
    for feature in features : 
        name = feature.text.split('\n')[0]
        full_data[features_name[name]].append(feature.text.split('\n')[1])



    ad_features = browser_ad.find_elements(By.CLASS_NAME, "re__pr-short-info-item.js__pr-config-item")
    ad_feature_names = {'Ngày đăng':'start_date','Ngày hết hạn':'end_date','Loại tin':'type','Mã tin':'id'}
    
    for feature in ad_features : 
        name = feature.text.split('\n')[0]
        full_data[ad_feature_names[name]].append(feature.text.split('\n')[1])

    max_length = max(len(v) for v in full_data.values())
    for key in full_data.keys() : 
        if len(full_data[key]) < max_length : 
            full_data[key].append(None)



def main(browser) :
    count = 0
    full_data = {
        'title': [], 'address': [], 'description': [],
        'size': [], 'price_string': [], 'direction': [], 'balcony_direction': [],
        'bedrooms': [], 'toilets': [], 'duty': [], 'furniture': [],
        'start_date': [], 'end_date': [], 'type': [], 'id': []
    }
    
    print("Process the first page")
    print("------------------------------------------------------")
    new_url = process_1_page(browser,full_data)
    while count < 5 and new_url is not None : 
        print(f"Process the {count} page")
        print("------------------------------------------------------")
        next_service = Service(driver_path)
        next_browser = webdriver.Chrome(service=next_service)
        next_browser.get(new_url)
        new_url = process_1_page(next_browser,full_data)
        time.sleep(20)
        count+=1
        browser.quit()
        next_browser.quit()
        
    browser.quit()
    print("Finish crawling page")
    print("------------------------------------------------------")
    return full_data

if __name__ == "__main__" : 
    driver_path = "crawl_by_selenium\chromedriver-win64\chromedriver.exe"

    service = Service(driver_path)
    browser = webdriver.Chrome(service=service)

    browser.get("https://batdongsan.com.vn/ban-can-ho-chung-cu-tp-hcm")
    
    time.sleep(20)

    full_data = main(browser)

    df = pd.DataFrame(full_data)
    df.to_csv("GiaNhaCC.csv",index=False)