from bs4 import BeautifulSoup
import requests

html = requests.get('https://www.moneycontrol.com/news/business/markets/persistent-systems-infosys-other-it-shares-drop-up-to-2-as-trade-geopolitical-tensions-weigh-13112156.html').text
soup = BeautifulSoup(html, 'html.parser')

# storage_file = 'storage.txt'
# master_1 = soup.find('div', class_='page_wrapper')
# master_2 = master_1.find('section', class_='article_wrapper clearfix')
# master_3 = master_2.find('div', class_='article_consum_wrapper article_page infinite-scroll ')
# # master_4 = master_3.find('div', class_='page_left_wrapper')
# # print(master_2)


# news_heading = master_2.find('h1', class_='article_title artTitle').text
# article_description = master_2.find('h2', class_='article_desc').text
# print(article_description)

# finding_something = master_2.find('div', class_='content_wrapper arti-flow')
# finding_more = finding_something.find_all('p')
# for para in finding_more:
#     print(para.text)

#stroing the heading in stoeage file
#also add article description
#add finidng_more to storage file
# with open(storage_file, 'w') as file:
#     file.write('Article Heading : '+news_heading + '\n')
#     file.write('Article Description : '+article_description + '\n')
#     for para in finding_more:
#         file.write(para.text + '\n')
# print('Data has been written to', storage_file)

# Will be returning all the data as a string, without storing in a file
# print(article_description)
#Here the article descriptino is not getting printed, we need to fix that

# result = f"Article Heading: {news_heading}\n"
# result += f"Article Description: {article_description}\n"
# for para in finding_more:
#     result += para.text + '\n'

# print(result)
# The code scrapes the news article from Moneycontrol, extracts the heading, description, and paragraphs,
# and writes them to a text file named 'storage.txt'.



def get_news_content(link):
    html = requests.get(link).text
    soup = BeautifulSoup(html, 'html.parser')

    master_1 = soup.find('div', class_='page_wrapper')
    master_2 = master_1.find('section', class_='article_wrapper clearfix')
    master_3 = master_2.find('div', class_='article_consum_wrapper article_page infinite-scroll ')

    news_heading = master_2.find('h1', class_='article_title artTitle').text
    article_description = master_2.find('h2', class_='article_desc').text

    finding_something = master_2.find('div', class_='content_wrapper arti-flow')
    finding_more = finding_something.find_all('p')

    result = f"Article Heading: {news_heading}\n"
    result += f"Article Description: {article_description}\n"
    for para in finding_more:
        result += para.text + '\n'

    return result


print(get_news_content('https://www.moneycontrol.com/news/business/markets/persistent-systems-infosys-other-it-shares-drop-up-to-2-as-trade-geopolitical-tensions-weigh-13112156.html'))