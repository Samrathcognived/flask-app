import re
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin 
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent  
import requests
import random
import time


app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app, resources={r"/*": {"origins": ["http://localhost:3002", "https://v2-dot-qa-tvelp.uc.r.appspot.com", "https://v2-dot-dev-tvelp.uc.r.appspot.com/"]}})
user_agent = UserAgent()

# Initialize the WebDriver AC
options = webdriver.ChromeOptions()
options = Options()
options.add_argument("--headless")

def get_name_img(soup, domain):
    product_name = ""
    product_image = ""

    h1_tag = soup.find("h1");
    title_tag = soup.find("title");
    if title_tag:
        title_tag = soup.find("title").text.strip()
    if h1_tag:
        for child in h1_tag.descendants:
            if isinstance(child, str):
                product_name += child
        product_name = product_name.strip()
    elif domain == "amazon.in" or not h1_tag:
        product_name = title_tag;  
    else:
      print("No product name found")

    significant_portion_match = re.search(
        r'\w+\s+(\w+\s+)+', product_name)

    significant_portion = ""
    if significant_portion_match:
        significant_portion = significant_portion_match.group(0)
    else:
        print("No significant portion found in the product name")

    product_image = soup.find("img", alt=re.compile(
        rf'{re.escape(significant_portion)}', re.IGNORECASE))
    if product_image:
        product_image = product_image.get("src")
    return {"product_name": product_name, "product_image": product_image}

def scrape_amazon_in(link, soup):
    try:
        product_price = ""
        price = soup.find("span", class_="a-offscreen")
        # price_element = soup.find("span", class_="a-price")
        # # a-price a-text-price a-size-medium apexPriceToPay
# comment
        if price:
          product_price = price.get_text();
        else:
          ""
        data = get_name_img(soup, "amazon.in")
        product_name = data["product_name"]
        product_image = data["product_image"]
        print({
            "product_name": product_name,
            "product_price": product_price,
            "product_image": product_image
        })
        return {
            "product_name": product_name,
            "product_price": product_price,
            "product_image": product_image,
            "currency_type": "INR"
        }
    except Exception as e:
        return {'error': str(e)}
    
def scrape_amazon_com(link, soup):
    try:
        price_element = soup.find("span", class_="a-price")
        price_element = soup.find("span", class_="a-price")
        if price_element: 
         price = ""

         for child in price_element.descendants:
           if isinstance(child, str):
            price += child
            price = price.strip()
            price_element = price;    
            break
        data = get_name_img(soup, "amazon.com")
        product_name = data["product_name"]
        product_image = data["product_image"]
        print({ 
            "product_name": product_name,
            "product_price": price_element,
            "product_image": product_image
        })
        return {
            "product_name": product_name,
            "product_price": price_element,
            "product_image": product_image,
            "currency_type": "USD"
        }
    except Exception as e:
        return {'error': str(e)}

def scrape_ebay(link, soup):
    try:
        # Extract price using a more specific selector
        price_element = soup.find("div", class_="x-price-primary")
        main_price = price_element.find("span").text if price_element else ""
        
        data = get_name_img(soup, "ebay")
        product_name = data["product_name"]
        product_image = data["product_image"]
        print({
            "product_name": product_name,
            "product_price": main_price,
            "product_image": product_image
        })
        return {
            "product_name": product_name,
            "product_price": main_price,
            "product_image": product_image,
            "currency_type": "USD" 
        }
    except Exception as e:
        return {'error': str(e)}

def scrape_bestbuy(link, soup):
    try:
        # Extract price using a more specific selector
        price_element = soup.find("div", class_="priceView-hero-price")
        span_element = price_element.find("span")
        span_text = span_element.text if span_element else ""

        data = get_name_img(soup, "bestbuy")
        product_name = data["product_name"]
        product_image = data["product_image"]
        print({
            "product_name": product_name,
            "product_price": span_text,
            "product_image": product_image
        })
        return {
            "product_name": product_name,
            "product_price": span_text,
            "product_image": product_image,
            "currency_type": "USD"

        }
    except Exception as e:
        return {'error': str(e)}

def scrape_apple(link, soup):
    try:
        data = get_name_img(soup, "apple")
        product_name = data["product_name"]
        product_image = ""
        
        significant_portion_match = re.search(
            r'\w+\s+(.+)', product_name)
        
        if significant_portion_match:
            significant_portion = significant_portion_match.group(1)
            product_image = soup.find("img", alt=re.compile(
                rf'{re.escape(significant_portion)}', re.IGNORECASE))
            
            first_img = soup.find('link', rel="image_src")
            
            if product_image:
                product_image = product_image.get("src")
            elif first_img:
                img_src = first_img.get('href')
                product_image = img_src
                
            apple_prices = soup.find(
                'span', {'data-autom': re.compile(r'full-?price', re.IGNORECASE)})
            find_price = apple_prices.find("span", class_="nowrap")
            currency_type = ""
            if find_price:
                product_price = find_price.get_text()
                if "$" in find_price.get_text():
                   currency_type = "USD";
                else:
                   currency_type = "INR"
            else:
                product_price = apple_prices.get_text()  
        else :
            product_price = ""
        print({
            "product_name": product_name,
            "product_price": product_price,
            "product_image": product_image
        })
        return {
            "product_name": product_name,
            "product_price": product_price,
            "product_image": product_image,
            "currency_type": currency_type
        }
    except Exception as e:
        return {'error': str(e)}

def scrape_flipkart(link, soup):
    try:
        # Extract price using a more specific selector
        price_element = soup.find(text=re.compile(r'^₹'))
        product_price = price_element.strip() if price_element else ""
        data = get_name_img(soup, "flipcart")
        product_name = data["product_name"]
        product_image = data["product_image"]
        
        # if not product_image:
            # product_image = soup.find("img", class_=True)
            # print(product_image, '***********************')

            # product_image = product_image.get("src")
        print({
            "product_name": product_name,
            "product_price": product_price,
            "product_image": product_image
        })
        return {
            "product_name": product_name,
            "product_price": product_price,
            "product_image": product_image,
            "currency_type": "INR"
        }
    except Exception as e:
        return {'error': str(e)}

def scrape_default(link, soup):
    try:
        data = get_name_img(soup)
        product_name = data["product_name"]
        product_price = ""
        product_image = data["product_image"]

        return {
            "product_name": product_name,
            "product_price": product_price,
            "product_image": product_image
        }
    except Exception as e:
        return {'error': e}

scraping_functions = {
    'amazon.in': scrape_amazon_in,
    'amazon.com': scrape_amazon_com,
    'ebay.com': scrape_ebay,
    'bestbuy.com': scrape_bestbuy,
    'apple.in': scrape_apple,
    'apple.com': scrape_apple,
    'flipkart.com': scrape_flipkart,
    'default': scrape_default
}
@app.route('/', methods=['GET'])
def sayHello():
    return render_template("index.html")

@app.route('/getData', methods=['POST'])
@cross_origin()
def scrape_product():
    try:
        authorization_header = request.headers.get('Authorization')
        if authorization_header and authorization_header.startswith('Bearer '):
            authorization_header = authorization_header.replace('Bearer ', '')

        selected_case = 'default'
        link = ""
        driver = webdriver.Chrome(options=options)

        try:
            data = request.get_json()
            link = data['link']
            domain = re.search(r'www\.(.+?)\.(com|in|org|net|gov|edu|co\.uk|co\.in)', link)
            domain_name = domain.group(1) + "." + domain.group(2)
            selected_case = domain_name.lower()
        except Exception as e:
            return jsonify({'error': str(e)})

        # Scrape the page and call the appropriate scraping function
        try:
            driver.get(link)
            page_source = driver.page_source
            soup = bs(page_source, "html5lib")
            scraping_function = scraping_functions.get(selected_case, scrape_default)
            result = scraping_function(link, soup)
            random_user_agent = user_agent.random
            headers = {'User-Agent': random_user_agent}
            time.sleep(0.5 * random.random())
            response = requests.get(link, headers=headers)
            response = jsonify(result)
            return response
        except Exception as e:
            return jsonify({'error': str(e)})
        finally:
            if driver:
                driver.quit()  # Close the WebDriver when done
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
