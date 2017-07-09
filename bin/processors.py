#!/usr/bin/env python3

from bs4 import BeautifulSoup
from requests import get
from re import compile
from urllib.parse import urljoin
from os import makedirs
from hashlib import sha256
from os.path import exists, join

# Add Zilog processors from the given name
def zilog_parser(brand, soup):
    h3s = soup.find_all('h3')
    ul = None
    for h3 in h3s:
        if h3.find('span', text='Microprocessor families'):
            ul = h3.find_next_sibling('ul')
    if not ul:
        raise Exception('Missing processor section')
    add_processors_from_list(brand, ul)

# Add Intel processors from the given name
def intel_parser(brand, soup):
    spans = soup.select('h3 span.mw-headline')
    for span in spans:
        add_processor(brand, span.getText())

# Given a name, add the processor(s) it describes to the brand's list
def add_processor(brand, name):
    matched = True
    while matched:
        matched = False
        for p in name_patterns:
            m = p.match(name)
            if m:
                matched = True
                name = m.group('name')

    matched = False
    for entry in multi_patterns:
        p = entry['pattern']
        m = p.match(name)
        if m:
            matched = True
            groups = m.groupdict()
            names_group = groups['names']
            prefix = groups['prefix'] if 'prefix' in groups else None
            names = [n.strip() for n in names_group.split(entry['sep'])]
            for name in names:
                if prefix:
                    brands[brand].add('%s %s' % (prefix, name))
                else:
                    brands[brand].add(name)
            break

    if not matched:
        brands[brand].add(name)

# Pull names from a single wikitable on a page
def add_processors_from_table(brand, table):
    # get data rows
    rows = [r for r in table.select('tr') if r.select_one('td')]

    row_skip = 0

    for row in rows:
        if row_skip > 0:
            row_skip -= 1
            continue
        td = row.select_one('td')
        # skip rows where the first data cell skips multiple columns
        if td.has_attr('colspan'):
            continue
        if td.has_attr('rowspan'):
            row_skip = int(td['rowspan']) - 1
        name = ' '.join(td.getText().split())

        add_processor(brand, name)

# Add processors from lists under headings
def add_processor_sections(brand, headings):
    for h in headings:
        if h.select('.mw-headline')[0].getText() == 'See also':
            break
        ul = h.find_next_sibling('ul')
        add_processors_from_list(brand, ul)

# Add all processors on a page. Look for lists of wikitables first, then for H3
# headings (assumed to mark ULs)
def add_processors_on_page(brand, soup):
    tables = soup.select('.mw-parser-output .wikitable')
    if len(tables) > 0:
        for table in tables:
            th = table.select('th:nth-of-type(1)')[0]
            text = ' '.join(th.getText().lower().split())
            if text != 'model number':
                continue
            add_processors_from_table(brand, table)
    else:
        headings = [t.parent for t in soup.select('h3 > .mw-headline')]
        add_processor_sections(brand, headings)

# Add processors from a UL on the top-level processor list page
def add_processors_from_list(brand, element):
    items = element.select('> li')
    for i in items:
        child_list = i.select('> ul')
        if child_list:
            add_processors_from_list(brand, child_list[0])
        else:
            name = i.getText()

            m = list_pattern.match(name)
            if m:
                # The name is a link to a list of processors on another page
                link = i.select('a')[0]
                href = urljoin(baseUrl ,link['href'])
                list_page_doc = get_text(href)
                list_page_soup = BeautifulSoup(list_page_doc, 'html.parser')
                add_processors_on_page(brand, list_page_soup)
            else:
                add_processor(brand, name)

# Get a URL, caching the retrieved value for later
def get_text(url):
    return get(url).text

# Where to get data for brands that can't easily be handled generically
known_brands = {
    'Intel': { 'page': 'List_of_Intel_microprocessors', 'parser':  intel_parser },
    'AMD': { 'page': 'List_of_AMD_microprocessors' },
    'Zilog': { 'page': 'Zilog', 'parser': zilog_parser }
}

# Processor names that are actually links to more products
list_pattern = compile(r'List of .* products')

# Patterns used to extract processor names from list entries
name_patterns = [
    compile(r'List of (?:Intel|AMD|VIA) (?P<name>.*) microprocessors'),
    compile(r'List of (?P<name>.*) microprocessors'),
    compile(r'(?P<name>.*) (?:Single|Dual|Quad|Six)(?:-core)? .*'),
    compile(r'(?:AMD|Intel|Zilog|NEC|Freescale) (?P<name>.*)'),
    compile(r'Texas Instruments (?P<name>.*) – used.*'),
    compile(r'Toshiba (?P<name>.*)\[.*\]'),
    compile(r'(?:Toshiba|Motorola|Intel|Texas Instruments) (?P<name>.*)'),
    compile(r'(?P<name>.*) PA-RISC Version .*'),
    compile(r'\d{4} – (IBM )?(?P<name>.*)'),
    compile(r'(?P<name>Am[0-9x]+) .*'),
    compile(r'(?P<name>Athlon) \d-series'),
    compile(r'(?P<name>Athlon XP) \(.*'),
    compile(r'(?P<name>.*) \d+-bit \([^)]+\)'),
    compile(r'(?P<name>[0-9x]+) \w.*'),
    compile(r'(?P<name>.*) \([^)]+\)'),
    compile(r'(?P<name>.*) (?:architecture|[fF]amily|etc.|Processor|CPU|stack)'),
    compile(r'(?P<name>.*?)(\[[^]]+\])+')
]

multi_patterns = [
    { 'pattern': compile(r'(?P<names>\S+(?: and \S+)+)'), 'sep': ' and ' }, 
    { 'pattern': compile(r'(?P<names>V\d+(?:\s*/\s*V\d+)+)'), 'sep': '/' },
    { 'pattern': compile(r'(?P<names>\d+(?:\s*/\s*\d+)+)'), 'sep': '/' },
    { 'pattern': compile(r'(?P<names>PPC \S+(?:\s*/\s*PPC \S+)+)'), 'sep': '/' },
    { 'pattern': compile(r'(?P<names>SW-?\d+(?:\s*/\s*SW-?\d+)+)'), 'sep': '/' },
    { 'pattern': compile(r'(?P<names>μ\S+(?:\s*/\s*μ\S+)+)'), 'sep': '/' },
    { 'pattern': compile(r'(?P<names>µ\S+(?:\s*/\s*µ\S+)+)'), 'sep': '/' },
    { 'pattern': compile(r'(?P<prefix>Transputer) (?P<names>T\d(?:\s*/\s*T\d+)+)'), 'sep': '/' },
    { 'pattern': compile(r'(?P<prefix>SuperH) (?P<names>SH-.+?(?:\s*/\s*SH-.+?)+)'), 'sep': '/' },
    { 'pattern': compile(r'(?P<prefix>microNOVA) (?P<names>mN.+(?: and mN.+)+)'), 'sep': ' and ' },
]

baseUrl = 'https://en.wikipedia.org/wiki/List_of_microprocessors'
brands = {}

# Get the top-level page
doc = get_text(baseUrl)
soup = BeautifulSoup(doc, 'html.parser')

# Pull brand names from the H2 elements, and pull processor family names from
# the list following each H2
headings = [t.parent for t in soup.select('h2 > .mw-headline')]
for h in headings:
    brand_name = h.select('.mw-headline')[0].getText()
    if brand_name == 'See also':
        break
    brand = set()
    brands[brand_name] = brand
    if brand_name in known_brands:
        info = known_brands[brand_name]
        brand_doc = get_text(urljoin(baseUrl, info['page']))
        brand_soup = BeautifulSoup(brand_doc, 'html.parser')
        if 'parser' in info:
            info['parser'](brand_name, brand_soup)
        else:
            add_processors_on_page(brand_name, brand_soup)
    else:
        next_tag = h.next_sibling
        while next_tag and not next_tag in headings:
            if next_tag.name == 'ul':
                add_processors_from_list(brand_name, next_tag)
            next_tag = next_tag.next_sibling

# Print the processor list
for brand in brands.keys():
    for b in sorted(brands[brand]):
        print('%s %s' % (brand, b))
