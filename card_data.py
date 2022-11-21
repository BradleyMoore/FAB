from typing import Any
import aiohttp, asyncio, requests, time
from bs4 import BeautifulSoup
from log import log
from set_codes import SET_CODES


def create_card(row: 'ResultSet') -> dict[str, str | int]: # type: ignore
    """Get a single card from a row in the html table.

    Args:
        row: the specific card from 1 row in the table

    Returns:
        the card and all associated data
    """

    card = {}
    fields = row.select('td')
    card['card_number'] = fields[0].text.strip()
    name_string = fields[1].text.strip()
    card['card_name'], card['color'], card['pitch_value'] = parse_name(name_string)
    card['printing_technique'] = fields[2].text.strip()
    card['notes'] = fields[3].text.strip()
    card['set'] = get_card_set(card['card_number'])

    return card


def determine_color(pitch_value: int) -> str:
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


async def get_all_cards(urls: list[tuple[str, str]]) -> list[dict[str, Any]]:
    """Get all cards from all links on page.

    Args:
        urls: urls for each card set

    Returns:
        all cards in existance for Flesh and Blood TCG
    """
    
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


def get_card_set(card_number: str) -> str | None:
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
        return None


def get_cards(url: str) -> list[dict[str, str | int]]:
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


def get_page(url: str) -> 'Response': # type: ignore
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


def get_set_urls() -> list[tuple[str, str]]:
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


def get_tasks(session: 'ClientSession', urls: list[tuple[str, str]]) -> list['Unknown']: # type: ignore
    """Get all async tasks.

    Args:
        session: the url for the card tables
        urls: list of urls for each card set

    Returns:
        the response data from the call to the url
    """
    
    tasks = []
    for url in urls:
        tasks.append(asyncio.create_task(session.get(url[1], ssl=False)))
        
    return tasks


def parse_name(name: str) -> tuple[str, str, int]:
    """Separate the name and the pitch value.

    Args:
        name: the card name from the table

    Returns:
        the name and pitch values of the card
    """

    if name[-3] == '(' and name[-1] == ')':
        partition = name.rpartition(' ')
        card_name = partition[0]
        pitch_value = int(partition[-1].strip('(').strip(')'))
        color = determine_color(pitch_value)      
    else:
        card_name = name
        pitch_value = 0
        color: str = ''

    return card_name, color, pitch_value


def main() -> None:
    start: float = time.time()
    set_urls = get_set_urls()

    results = asyncio.run(get_all_cards(set_urls))
    # cards = get_all_cards(set_urls)
    # print(len(cards))
    end = time.time()
    print(end-start)

    return


if __name__ == '__main__':
    main()
