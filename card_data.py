import aiohttp
import asyncio
import requests
import time
from bs4 import BeautifulSoup
from log import log
from set_codes import SET_CODES


def create_card(row):
    """Get a single card from a row in the html table.

    Args:
        row: the specific card from 1 row in the table

    Returns:
        the card and all associated data
    """

    card = {}
    fields = row.select('td')
    card['set_code'] = fields[0].text.strip()
    name_string = fields[1].text.strip()
    card['card_name'], card['color'], card['pitch_value'] = parse_name(
        name_string)
    card['printing_technique'] = fields[2].text.strip()
    card['notes'] = fields[3].text.strip()
    card['set'] = get_card_set(card['set_code'])

    return card


def determine_color(pitch_value):
    """Return the card color based on the pitch value.

    Args:
        pitch_value: The pitch value of the card, typically 1, 2, or 3.

    Returns:
        Name of the color of the card.
    """

    color = ''

    if pitch_value == 1:
        color = 'Red'
    elif pitch_value == 2:
        color = 'Yellow'
    elif pitch_value == 3:
        color = 'Blue'
    else:
        log('Warn', 'This card does not have a pitch value.')

    return color


def get_all_cards(urls):
    """Get all cards from each url in urls.

    Args:
        urls: List of urls for each card set.

    Returns:
        All cards from each set.
    """

    cards = []

    for url in urls:
        cards.append(get_cards(url[1])[:])

    return cards


async def get_all_cards_async(urls):
    cards = []
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = get_tasks(session, urls)
        responses = await asyncio.gather(*tasks)
        for response in responses:
            results.append(await response.text())
    
    for result in results:
        soup = BeautifulSoup(result, 'html.parser')
        tables = soup.select('table')
        tables = tables[1:]

        for table in tables:
            for row in table.select('tbody > tr'):
                if row:
                    card = create_card(row)
                    cards.append(card)

    return cards


def get_card_set(card_number):
    """Get the name of the set the card belongs to.

    Args:
        card_number: the card's collector number

    Returns:
        the full set name the card belongs to
    """

    card_set = card_number[0:3]

    try:
        return SET_CODES[card_set.lower()]
    except Exception:
        log('Info', card_number + ' is not in set_codes.py')


def get_cards(url):
    """Get all cards from a specific url.

    Args:
        url: the url for the table containing the cards

    Returns:
        all cards in the page
    """

    cards = []
    resp = get_page(url)
    soup = BeautifulSoup(resp.text, 'html.parser')

    tables = soup.select('table')
    tables = tables[1:]

    for table in tables:
        for row in table.select('tbody > tr'):
            if row:
                card = create_card(row)
                cards.append(card)

    return cards


def get_page(url):
    """Load 1 page from the given url.

    Args:
        url (str): the url for the card tables

    Returns:
        the response data from the call to the url
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (HTML, like Gecko) '
                      'Chrome/39.0.2171.95 Safari/537.36'}

    return requests.get(url, headers=headers)


def get_set_urls():
    """Get the urls for all card sets.

    Returns:
        all urls from the page pointing to a card set
    """

    url = 'https://fabtcg.com/collectors-centre/'
    card_sets = []

    response = get_page(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.select('.item-link')

    for link in links:
        card_sets.append((link.text.strip('\n'), link['href']))

    return card_sets


def get_tasks(session, urls):
    """Get all async tasks.

    Args:
        session (str): the url for the card tables

    Returns:
        the response data from the call to the url
    """
    
    tasks = []
    for url in urls:
        tasks.append(asyncio.create_task(session.get(url[1], ssl=False)))
        
    return tasks


def parse_name(name):
    """Separate the name and the pitch value.

    Args:
        name: the card name from the table

    Returns:
        the name and pitch values of the card
    """

    pitch_values = ['(1)', '(2)', '(3)']

    if any(x in name for x in pitch_values):
        partition = name.rpartition(' ')
        card_name = partition[0]
        pitch_value = int(partition[-1].strip('(').strip(')'))
        color = determine_color(pitch_value)
    else:
        card_name = name
        pitch_value = 0
        color = ''

    return card_name, color, pitch_value


def main():
    start = time.time()
    set_urls = get_set_urls()

    results = asyncio.run(get_all_cards_async(set_urls))
    # cards = get_all_cards(set_urls)
    # print(len(cards))
    end = time.time()
    print(end-start)


if __name__ == '__main__':
    main()
