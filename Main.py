from fastapi import FastAPI
from google import genai
import pandas as pd
from ScrapingHeadlines import get_news_content
import requests
import bs4 as BeautifulSoup
from llama_parse import LlamaParse
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()

serp_api = os.getenv("SERP_API_KEY")

app = FastAPI()


df1 = pd.read_excel('Book1OUpdated.xlsx')
df2 = pd.read_excel('Book1Updated.xlsx')

#Now we will merge both dataframes
df = pd.merge(df1, df2, on='Name', how='outer')
#Coutning number of na values in each column
na_count = df.isna().sum()


def get_stock_info(stock_name, df):
    stock_row = df[df["Name"].str.strip().str.lower() == stock_name.strip().lower()]
    
    if stock_row.empty:
        return [f"Stock '{stock_name}' not found."]
    
    row = stock_row.iloc[0]

    rename_map = {
        "CMP Rs._x": "CMP Rs.",
        "CMP Rs._y": "CMP Rs.",
        "Mar Cap Rs.Cr. _x": "Mar Cap Rs.",
        "Mar Cap Rs.Cr. _y": "Mar Cap Rs.",
    }

    formatted_info = []
    
    for col in df.columns:
        if pd.notna(row[col]):
            label = rename_map.get(col, col)
            formatted_info.append(f"{label.strip()}: {row[col]}")
    
    return formatted_info

@app.get("/")
def fun():
    article_1 = get_news_content('https://www.moneycontrol.com/news/business/economy/steel-secretary-says-fy26-imports-will-be-half-of-last-year-helped-by-safeguard-duty-13131110.html')
    article_2 = get_news_content('https://www.moneycontrol.com/news/business/markets/jsw-steel-tata-steel-other-metal-stocks-surge-up-to-4-after-rbi-s-surprise-50-bps-rate-cut-13102160.html')
    article_3 = get_news_content('https://www.moneycontrol.com/news/business/stocks/tata-steel-shares-fall-more-than-2-during-today-s-trading-session-alpha-article-13101447.html')

    recent_news = article_1 + "\n\n" + article_2 + "\n\n" + article_3
    financial_data = get_stock_info('Tata Steel',df)

    prompt = f"""
    You are given the following financial data and 3 recent news articles related to the stock [STOCK_NAME].

    Please:
    1. Analyze the **sentiment** in the news (positive/negative/neutral).
    2. Analyze the **fundamentals** using the provided metrics .
    3. Provide your **overall stock outlook** for both short-term and long-term.
    4. Assign a final stock movement score based on the combined analysis using the following scale:
   - Moderately Decreases: -7
   - Slightly Decreases: -3
   - Neutral: 0
   - Slightly Increases: +3
   - Moderately Increases: +7

    financial metrics : {financial_data}
    news articles : {recent_news}

    Output Format:

    1. News Sentiment: Positive / Neutral / Negative
    2. Fundamentals: Strong / Average / Weak
    3. Overall Stock Outlook:
    - Short Term: Bullish / Bearish / Neutral
    - Long Term: Bullish / Bearish / Neutral
    4. Final Stock Movement Score [From the given scale]
    5. Reasoning: [Brief paragraph with justification based on both news + financials]
    6. Whether to buy, sell, or hold the stock: [Buy / Sell / Hold]
    7. Additional Notes: [Any other relevant information or insights]
    8. Till what time should I hold the stock: [Provide a specific time frame, e.g., "Hold for 6 months"]
    9. What is the target price for the stock: [Provide a target price based

    """
    
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    )
    return {
        "gemini_response": response.text.split("\n")
    }

@app.get("/stock-info")
def get_stock_news(company_name: str):
    params =  {
        "qq": company_name + 'Stocks',
        "engine-x": "google",
        "tbm-p": "nws",
        "api-key": serp_api
     }
    response = requests.get("https://serpapi.com/search", params=params)
    return response.json()


@app.get("/financial-report/{stock_name}")
def financial_report(link_to_the_stock : str):
    link_to_scrape = link_to_the_stock
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(link_to_scrape, headers=headers)
    pdf_file = BytesIO(response.content)

    html = requests.get(link_to_scrape).text
    soup = BeautifulSoup.BeautifulSoup(html, "html.parser")

    main_class = soup.find("main", class_="flex-grow container")
    sectoion =  main_class.find('section', id='documents')
    div_flex_1 = sectoion.find('div', class_='flex-row flex-gap-small')
    div_master = div_flex_1.find('div', class_='documents annual-reports flex-column')
    div_annual_rep = div_master.find('div',class_ = 'show-more-box')
    table_annual_rep = div_annual_rep.find('ul', class_='list-links')
    latest_annual_rep = table_annual_rep.find('li')
    latest_annual_rep_link = latest_annual_rep.find('a')

    link_to_annual_report = latest_annual_rep_link.get('href')  # This will give you the link to the latest annual report

    parser = LlamaParse(
    api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
    num_workers=4,
    verbose=True,
    language="en",
    )

    result_with_link = parser.parse(pdf_file, extra_info={"file_name": "sample.pdf"})

    url = "https://www.bseindia.com/xml-data/corpfiling/AttachHis/2160dea5-d49e-4409-83a4-c2b111a3bd12.pdf"

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    pdf_file = BytesIO(response.content)

    parser = LlamaParse(api_key=os.getenv("LLAMA_CLOUD_API_KEY"))

    result = parser.parse(pdf_file, extra_info={"file_name": "bse_report.pdf"})

    text_documents = result.get_text_documents(split_by_page=False)
    full_text = "\n".join([doc.text for doc in text_documents])
    scraped_text = (full_text)

    return scraped_text.strip()
