import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
from tabulate import tabulate
import advertools as adv

import requests
from bs4 import BeautifulSoup
import json

# from .models import (
#     Settings,
# )
# from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
#-----------------------------------------------------------------------------------
def my_craw(url_base, PAGECOUNT=10, follow_links=False):
    url_base        = str(url_base)
    base            = url_base.replace('http://','')
    base            = base.replace('https://','')
    base            = base.replace('/','')
    output_file     = str(base) + '_file.jl'
    print(f'base={base}, output_file={output_file}')

    adv.crawl(url_base, output_file, follow_links=follow_links, custom_settings={'CLOSESPIDER_PAGECOUNT': PAGECOUNT, 'SPIDER_LOADER_WARN_ONLY': False, 'ROBOTSTXT_OBEY': True})
    enczp = pd.read_json(output_file, lines=True)
    # return enczp
    return enczp.head(PAGECOUNT)
#-----------------------------------------------------------------------------------
def find_different_img_attributes(url1, url2):
    driver = webdriver.Chrome()  # Asegúrate de tener ChromeDriver instalado y en el PATH
    
    try:
        driver.get(url1)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'img')))
        
        soup1 = BeautifulSoup(driver.page_source, 'html.parser')
        
        driver.get(url2)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'img')))
        
        soup2 = BeautifulSoup(driver.page_source, 'html.parser')
        
        different_img_attributes = []
        
        for img1, img2 in zip(soup1.find_all('img'), soup2.find_all('img')):
            if img1.attrs != img2.attrs:
                different_img_attributes.append((img1.attrs, img2.attrs))
        
        return different_img_attributes
    finally:
        driver.quit()

# # URLs de ejemplo de dos productos diferentes en un sitio web
# url_product1 = 'https://www.unimarc.cl/product/pan-libanes-chico-spagnolia-6-un'
# url_product2 = 'https://www.unimarc.cl/product/pan-libanes-integral-chico-spagnolia-6un'

# different_img_attrs = find_different_img_attributes(url_product1, url_product2)
# if different_img_attrs:
#     print('Atributos de las etiquetas <img> diferentes entre las dos URLs:')
#     for img_attrs1, img_attrs2 in different_img_attrs:
#         print('Atributos en la primera URL:', img_attrs1)
#         print('Atributos en la segunda URL:', img_attrs2)
#         print('-' * 30)
#-----------------------------------------------------------------------------------
def find_different_content_with_classes(url1, url2):
    response1 = requests.get(url1)
    response2 = requests.get(url2)
    
    if response1.status_code == 200 and response2.status_code == 200:
        soup1 = BeautifulSoup(response1.content, 'html.parser')
        soup2 = BeautifulSoup(response2.content, 'html.parser')
        
        different_content_tags = []
        
        for tag1, tag2 in zip(soup1.find_all(), soup2.find_all()):
            if tag1.text.strip() != tag2.text.strip():
                
                tag_classes = tag1.get('class')
                different_content_tags.append((tag1.name, tag_classes, tag1.text.strip(), tag2.text.strip()))
        
        return different_content_tags
    else:
        print('No se pudo acceder a una de las páginas:', url1, url2)
        return None

# URLs de ejemplo de dos productos diferentes en un sitio web
# url_product1 = 'https://www.unimarc.cl/product/pan-libanes-chico-spagnolia-6-un'
# url_product2 = 'https://www.unimarc.cl/product/pan-libanes-integral-chico-spagnolia-6un '

# different_content_and_classes = find_different_content_with_classes(url_product1, url_product2)
# if different_content_and_classes:
#     print('Etiquetas con contenido diferente y sus clases CSS:')
#     for tag_name, tag_classes, contenido1, contenido2 in different_content_and_classes:
#         print(f'Tag: {tag_name}')
#         if tag_classes:
#             print(f'Clases: {", ".join(tag_classes)}')
#         else:
#             print('Sin clases')
#         if contenido1:
#             print('contiene1: ',contenido1)
#             print('contiene2: ',contenido2)
#         print('-' * 30)
#-----------------------------------------------------------------------------------


def find_product_details_in_ld_json_selenium(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Para ejecución en segundo plano
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        time.sleep(2)  # Pausa para permitir que el contenido se cargue
        
        ld_json_tags = driver.find_elements(By.XPATH,('//script[@type="application/ld+json"]'))

        return product_details_fromsoup(ld_json_tags, is_selenium=True)

    except Exception as e:
        print('Error en find_product_details_in_ld_json_selenium')
    finally:
        driver.quit()


def find_product_details_in_ld_json_beautiful(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            ld_json_tags = soup.find_all('script', type='application/ld+json')
            
            return product_details_fromsoup(ld_json_tags, is_selenium=False)

        else:
            return {'message': f'Error al acceder a la página: {response.status_code}'}
    except Exception as e:
        return {'message': f'by try, Error al acceder a la página e={str(e)}'}


def product_details_fromsoup_breadcrumb(ld_json_tags, is_selenium=False):
    for tag in ld_json_tags:
        try:
            if is_selenium:
                ld_json_text = tag.get_attribute('textContent')
                if ld_json_text:
                    ld_json = json.loads(ld_json_text)
            else:
                if isinstance(tag, str):
                    ld_json = json.loads(tag)
                else:
                    ld_json = json.loads(tag.string)
                
        except json.JSONDecodeError:
            print(f'Error en product_details_fromsoup_breadcrumb JSONDecodeError --->  {ld_json_tags}')
        except Exception as e:
            print(f'Error en product_details_fromsoup_breadcrumb ---> {str(e)} {ld_json_tags}')

        if isinstance(ld_json, dict) and ld_json.get('@type') == 'BreadcrumbList':
            return extract_list_details(ld_json)
        elif isinstance(ld_json, dict) and '@graph' in ld_json:
            for item in ld_json['@graph']:
                if isinstance(item, dict) and item.get('@type') == 'BreadcrumbList':
                    return extract_list_details(item)
                    
    
    
    return None

def product_details_fromsoup(ld_json_tags, is_selenium=False):
    for tag in ld_json_tags:
        try:
            if is_selenium:
                ld_json_text = tag.get_attribute('textContent')
                if ld_json_text:
                    ld_json = json.loads(ld_json_text)
            else:
                if isinstance(tag, str):
                    ld_json = json.loads(tag)
                else:
                    ld_json = json.loads(tag.string)
                

            if isinstance(ld_json, dict) and ld_json.get('@type') == 'Product':
                return extract_product_details(ld_json)
            elif isinstance(ld_json, dict) and '@graph' in ld_json:
                for item in ld_json['@graph']:
                    if isinstance(item, dict) and item.get('@type') == 'Product':
                        return extract_product_details(item)
            # else:
            #     print("No encontrado")
        except json.JSONDecodeError:
            # pass
            print(f'Error en product_details_fromsoup JSONDecodeError --->  {ld_json_tags}')
        except Exception as e:
            print(f'Error en product_details_fromsoup ---> {str(e)} {ld_json_tags}')
    
    
    return None

def extract_list_details(ld_json):
    item_list = ld_json['itemListElement']

    # Crear una lista para almacenar los elementos relevantes
    extracted_data = []

    # Recorrer la lista y extraer la información relevante
    for itema in item_list:
        position = itema['position']
        try:
            name = itema['name']
            item_url = itema['item']
        except:
            name = ''
            item_url = ''
        extracted_data.append({'position': position, 'name': name, 'item': item_url})

    return extracted_data



def extract_product_details(ld_json):
    
    priceCurrency = ''
    price = ''
    availability = None

    if isinstance(ld_json, dict):
        offers = ld_json.get('offers', {})
        if isinstance(offers, dict):
            offer = offers
            priceCurrency = offer.get('priceCurrency', '')
            price = offer.get('price', '')
            availability = offer.get('availability', '')
        elif isinstance(offers, list) and len(offers) > 0:
            offer = offers[0]
            priceCurrency = offer.get('priceCurrency', '')
            price = offer.get('price', '')
            availability = offer.get('availability', '')
        
        # Extracting the price from the nested structure
        if 'offers' in offers and isinstance(offers['offers'], list) and len(offers['offers']) > 0:
            offer = offers['offers'][0]
            price = offer.get('price', '')
            availability = offer.get('availability', '')

        brand = ld_json.get('brand', {})
        brand_name = ''
        if isinstance(brand, dict):
            brand_name = brand.get('name', '')

        product_details = {
            'name': ld_json.get('name'),
            'image': ld_json.get('image', {}).get('url') if isinstance(ld_json.get('image'), dict) else ld_json.get('image', ''),
            'availability': availability,
            'sku': ld_json.get('sku'),
            'description': ld_json.get('description'),
            'category': ld_json.get('category', ''),
            'brand_name': brand_name,
            'priceCurrency': priceCurrency,
            'price': price,
        }
        return product_details
    else:
        return {'message': 'Json type product no encontrado'}
    

    
# # URL de ejemplo de un producto en un sitio web
# product_url = 'https://www.unimarc.cl/product/pan-libanes-chico-spagnolia-6-un'

# detalles_producto = find_product_details_in_ld_json(product_url)
# if detalles_producto:
#     print('Detalles del producto:')
#     print('Nombre:', detalles_producto['nombre'])
#     print('image:', detalles_producto['image'])
#     print('description:', detalles_producto['description'])
#     print('SKU:', detalles_producto['sku'])
#     print('Marca:', detalles_producto['marca'])
#     print('Moneda Precio:', detalles_producto['moneda_precio'])
#     print('Precio:', detalles_producto['precio'])
# else:
#     print('No se pudieron encontrar los detalles del producto en la página.')
#-----------------------------------------------------------------------------------
def get_url_content(url_list, decode=True):
    print(url_list, decode)

    return adv.url_to_df(url_list, decode=decode)

def get_url_robots(url_base):
    robots_urls = None

    if url_base:
        robots_urls = url_base + 'robots.txt'
    
    return robots_urls

def get_data_robots(robots_urls):


    existe_robots = False
    try:
        url_robots = adv.robotstxt_to_df(robots_urls)
        existe_robots = True
        print(f'robots_urls={robots_urls} url_robots={url_robots}')
    except Exception as e:
        print(f"Error al get_data_robots {robots_urls} {e}")
        url_robots = pd.Series([])
        

    return url_robots, existe_robots

def get_content_from_column(content, column, text_to_search):
    try:
        column_content = (content.loc[content[column] == text_to_search])
    except Exception as e:
        print(f"Error en get_content_from_column, {column} {text_to_search} {e}")
        column_content = pd.Series([])
        # column_content = None

    return column_content


def get_sitemap_from_url(sitemap_url, recursive=False):
    try:
        sitemap = adv.sitemap_to_df(sitemap_url, recursive=recursive)
    except Exception as e:
        print(f"Error en get_sitemap_from_url,  {sitemap_url} {e}")
        sitemap = pd.DataFrame([])

    print(type(sitemap))
    return sitemap

# user_agent          = Settings.objects.get(key='user-agent').value
# custom_settings = \
#     {
#         'CLOSESPIDER_PAGECOUNT': 100,
#         'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
#         'USER_AGENT': user_agent
#     }


# def extract_product_details(ld_json):
#     priceCurrency = ''
#     price = ''
#     availability = None

#     if isinstance(ld_json, dict):
#         brand = ld_json.get('brand', {})
#         brand_name = ''
#         if isinstance(brand, dict):
#             brand_name = brand.get('name', '')

#         product_details = {
#             'name': ld_json.get('name'),
#             'image': ld_json.get('image', {}).get('url') if isinstance(ld_json.get('image'), dict) else ld_json.get('image', ''),
#             'description': ld_json.get('description'),
#             'brand_name': brand_name,
#         }

#         offers = ld_json.get('offers', {})
#         if isinstance(offers, dict):
#             product_details['priceCurrency'] = offers.get('priceCurrency', '')
#             product_details['price'] = offers.get('price', '')
#             availability = offers.get('availability', '')

#         product_details['availability'] = availability
#         return product_details
#     else:
#         return {'message': 'Json type product no encontrado'}