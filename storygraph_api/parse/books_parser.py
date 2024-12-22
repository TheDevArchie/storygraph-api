from tokenize import Whitespace
from storygraph_api.request.books_request import BooksScraper
from storygraph_api.exception_handler import parsing_exception
from bs4 import BeautifulSoup
import re

class BooksParser:
    @staticmethod
    @parsing_exception
    def book_page(book_id):
        content = BooksScraper.main(book_id)
        soup = BeautifulSoup(content, 'html.parser')
        h3_tag = soup.find('h3',class_="font-serif font-bold text-2xl md:w-11/12")
        title = h3_tag.contents[0].strip()
        authors = []
        for a in h3_tag.contents[1].find_all('a'):
            authors.append(a.text)
        p_tag = soup.find('p',class_="text-sm font-light text-darkestGrey dark:text-grey mt-1")
        pages = p_tag.contents[0].strip().split()[0]
        first_pub = p_tag.contents[1].find_all('span')[1].text.split()[2]
        tags = []
        tag_div = soup.find('div',class_="book-page-tag-section").find_all('span')
        for tag in tag_div:
            tags.append(tag.text)
        desc = soup.find_all('script')[5].text
        pattern = re.compile(r"Description<\/h4><div class=\"trix-content mt-3\">(.*?)<\/div>", re.DOTALL)
        match = pattern.search(desc)
        description = match.group(1).strip()
        review_content = BooksScraper.community_reviews(book_id)
        rev_soup = BeautifulSoup(review_content,'html.parser')
        avg_rating = rev_soup.find('span',class_="average-star-rating").text.strip()
        moods = _parse_moods(rev_soup)
        paces = _parse_pace(rev_soup)

        data = {
                'title':title,
                'authors': authors,
                'pages': pages,
                'first_pub': first_pub,
                'tags': tags,
                'average_rating': avg_rating,
                'description':description,
                'moods': moods,
                'paces': paces
                }

        return data

    @staticmethod
    @parsing_exception
    def search(query):
        content = BooksScraper.search(query)
        soup = BeautifulSoup(content, 'html.parser')
        search_results = []
        books = soup.find_all('div', class_="book-title-author-and-series w-11/12")
        for book in books:
            title = book.find('a').text.strip()
            author = book.find('p').text.strip()
            book_id = book.find('a')['href'].split('/')[-1]
            search_results.append({
                'title': title,
                'author': author,
                'book_id': book_id
            })
        return search_results


def _parse_moods(rev_soup: BeautifulSoup) -> dict[str, int]:
    """
    Returns:
        dict[str, int]: Moods along with their percentage.
    """
    moods = {}
    moods_div = rev_soup.find('div', class_='moods-list-reviews')

    for mood in moods_div.find_all('span', class_='md:mr-1'):
        mood_type = mood.text.strip()
        percentage = int(mood.find_next_sibling().text.strip('%'))
        moods[mood_type] = percentage

    return moods


def _parse_pace(rev_soup: BeautifulSoup) -> dict[str, int]:
    """
    Returns
        dict[str, int]: Moods along with their percentage.
    """
    paces = {}
    pace_div = rev_soup.find('div', class_='paces-reviews')

    for pace in pace_div.find_all('span', class_='md:mr-1'):
        pace_type = pace.text.strip()
        percentage = int(pace.find_next_sibling().text.strip('%'))
        paces[pace_type] = percentage

    return paces
