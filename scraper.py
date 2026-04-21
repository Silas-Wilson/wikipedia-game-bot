import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import unquote

HEADERS = {
    "User-Agent": "WikipediaGameBot/1.0 (sw068591@gmail.com)"
}

def request_html(url):
    response = requests.get(url, headers=HEADERS)
    time.sleep(0.2)
    return BeautifulSoup(response.text, "html.parser")

def get_all_hyperlink_urls(url):
    html = request_html(url)

    #Extract the URLs from the HTML
    content = html.select_one('#mw-content-text')

    links = content.select('p a')

    urls = [
        a.get('href') if a.get('href') else "NO_URL"
        for a in links
    ]
    hyperlink_texts = [
        link.get_text(strip=True) if link.get_text(strip=True) else "NO_TEXT"
        for link in links
    ]

    #for url, text in zip(urls, hyperlink_texts):
    #   print(text + ": " + url)

    #Filter the URLs
    filtered_urls = []
    base_url = "https://en.wikipedia.org"
    for url in urls:
        if (wiki_index := url.find("/wiki/")) == -1: continue #Filter out non-wikipedia links
        elif wiki_index > 0: url = url[wiki_index:] #Make sure URL starts with "/wiki/"
        if base_url + url in filtered_urls: continue #Filter out duplicates
        if url.find(":") != -1: continue #Filter out links with namespaces
        if (fragment_index := url.find("#")) != -1: url = url[0:fragment_index] #Truncate URI fragments

        filtered_urls.append(base_url + url)
    
    return filtered_urls

def get_page_title(url, remove_parenthesis = False):
    title = unquote(url.split("/wiki/")[-1]).replace("_", " ")

    if remove_parenthesis and title.find("(") != -1: 
        title = title[:title.index("(")].strip()
    return title

def get_first_n_paragraphs(url, n, max_tokens = 256):
    html = request_html(url)
    page_title = get_page_title(url, True)

    #Extract the first paragraph from the HTML
    content = html.select_one('#mw-content-text')
    paragraphs = content.select('p')

    #Get first n non-empty paragraphs
    first_paragraphs = []
    for paragraph in paragraphs:
        text = paragraph.get_text()
        
        if paragraph.get_text(strip=True):
            if text.find(page_title) != -1:          # Testing removing the
                text = text.replace(page_title, " ") # title from the paragraph
            first_paragraphs.append(text)
            if (len(first_paragraphs) == n): return " ".join(first_paragraphs)[0:max_tokens * 4]

def search_wikipedia(query):
    res = requests.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json"
        },
        headers=HEADERS
    )
    data = res.json()
    search_result = data["query"]["search"]

    if len(search_result) <= 0: return None

    title = search_result[0]["title"]
    return "https://en.wikipedia.org/wiki/" + title.replace(" ", "_")

#print(get_first_table("https://en.wikipedia.org/wiki/David_Falk", 256))
