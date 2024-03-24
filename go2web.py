#!/usr/bin/env python

import socket, ssl
from urllib.parse import urlparse, quote_plus
from bs4 import BeautifulSoup
import re
import argparse
import json
from datetime import datetime


def send_request(host, port, request, use_ssl=False):
    try:
        if use_ssl:
            context = ssl.create_default_context()
            with context.wrap_socket(socket.socket(), server_hostname=host) as s:
                s.connect((host, port))
                s.sendall(request.encode())
                
                response = b""
                while True:
                    data = s.recv()
                    if not data: break
                    response += data
        else:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                s.sendall(request.encode())

                response = b""
                while True:
                    data = s.recv()
                    if not data: break
                    response += data

        # Add the redirection functionality.
        header, _, content = response.partition(b"\r\n\r\n")
        header_parts = header.decode().split("\r\n")
        if "302" in header_parts[0]:
            url_start_index = header_parts[1].find(":")+2
            new_url = header_parts[1][url_start_index:]
            get_link_page(new_url)
        else:
            try:
                return content.decode('utf-8')
            except:
                try:
                    return content.decode('ISO-8859-1')
                except:
                    print("Decoding failed.")
                    return
    except Exception as e:
        print("Error: ", e)
        return None
    

def get_html_json():
    with open("data.json", 'r') as json_file:
        data = json.load(json_file)

    return data


def save_html_json(webpage, html, data):
    data[webpage] = [datetime.now().isoformat(), html]
    with open("data.json", 'w') as json_file:
        json.dump(data, json_file, indent=4)


def time_diff(time):
    return (datetime.now() - datetime.fromisoformat(time)).total_seconds()
    

def get_link_page(url):
    # Obtain main parameters
    parsed_link = urlparse(url)
    host = parsed_link.netloc
    protocol = parsed_link.scheme
    path = parsed_link.path

    webpage = host + path
    html_json = get_html_json()
    date_html = html_json.get(webpage, None)

    if (not date_html or time_diff(date_html[0]) >= 5):
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"

        # Send the request depending on the protocol
        html = ""
        if protocol == "http":
            port = 80
            html = send_request(host, port, request)
        elif protocol == "https":
            port = 443
            html = send_request(host, port, request, use_ssl=True)    

        if html:
            save_html_json(webpage, html, html_json)
        else: return
    else:
        html = date_html[1]

    # Get the content of the html
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()

    # Deal with whitespaces
    new_text = re.sub(r' +', ' ', text)
    new_text = new_text.replace("\n ", "\n")
    new_text = new_text.replace("\r\n", "\n")
    new_text = re.sub(r'\t+', '\t', new_text)
    new_text = re.sub(r'\n{2,}', '\n\n', new_text)
    new_text = re.sub(r'\r{2,}', '\r\r', new_text)
    
    print(new_text.strip())

    images = soup.find_all('img')
    if images:
        print("Image sources: ")
        for img in images:
            print(img["src"])


def search_bing(terms):
    search_query = quote_plus(terms)
    host = "www.bing.com"
    port = 443
    request = f"GET /search?q={search_query} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"

    # Get the content of the html
    lis, rpt = [], 0
    while len(lis) == 0 and rpt != 40:
        rpt += 1
        html = send_request(host, port, request, use_ssl=True)
        soup = BeautifulSoup(html, "html.parser")
        ols = soup.find(id="b_results")
        lis = ols.find_all("li", class_="b_algo")

    if len(lis) != 0:
        for index, li in enumerate(lis):
            h2 = li.find("h2")
            if h2:
                print(str(index+1) + ". " + h2.get_text()+ ": " + h2.find("a")["href"])
    else:
        print("No results!")


# Prepare the cache storage
with open("data.json", 'w') as json_file:
    json.dump({}, json_file)

# Adding arguments
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--url', type=str, help='makes an HTTP request to a specified URL and prints the content of the link')
parser.add_argument('-s', '--search_term', type=str, help='makes an HTTP request to a search engine using the query, and prints the top 10 results')

# Parsing arguments
args = parser.parse_args()

# Accessing parsed arguments
url = args.url
terms = args.search_term

try:
    if url:
        # make an HTTP request to the specified URL and print the response
        get_link_page(url)
        print()
    elif terms:
        # make an HTTP request to search the term using your 
        # favorite search engine and print top 10 results
        search_bing(terms)
        print()
except:
    print("Invalid command.")