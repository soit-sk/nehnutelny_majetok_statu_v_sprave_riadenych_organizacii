#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This scraper scrapes the data from the Ministry of Finance of The 
Slovak Republic. It processes the list of the real-estate
property of the state.

This is a new and updated version - since they began publishing
the list in XML format.
"""

# INITIAL DATA

site_url = 'http://www.finance.gov.sk/'    # main page
start_page = 'Default.aspx?CatID=4733'      # subpage url
DEBUG = False

import scraperwiki
import urllib2
import lxml
import lxml.html
import sys
import re
import collections

import mydebug as d
d.DEBUG = DEBUG # enable for debug output
from mydebug import prt

if not DEBUG:
    html = scraperwiki.scrape(site_url + start_page)

    # get all pdf links
    root = lxml.html.fromstring(html)
    xml_urls = root.cssselect("li.xml > a")
else:
    xml_urls = [{'href': 'dummy_URL'}]


# cellmap
cellmap = collections.OrderedDict([
    ('id', {'column': 0, 'type': 'Number'}),
    ('organizacia', {'column': 1, 'type': 'String'}),
    ('zariadenie', {'column': 2, 'type': 'String'}),
    ('druh_nehnutelnosti_1', {'column': 4, 'type': 'String'}),
    ('druh_nehnutelnosti_2', {'column': 5, 'type': 'String'}),
    ('inventarne_cislo', {'column': 6 }),
    ('rok_nadobudnutia', {'column': 7 }),
    ('kraj', {'column': 8 }),
    ('okres', {'column': 9 }),
    ('obec', {'column': 10 }),
    ('krajsky_urad', {'column': 11 }),
    ('adresa_objektu', {'column': 12 }),
    ('c_listu_vlastnictva', {'column': 13 }),
    ('spoluvlastnicky_podiel', {'column': 14 }),
    ('vymera', {'column': 15 }),
    ('parcelne_cislo', {'column': 16 }),
    ('supisne_cislo', {'column': 17 }),
    ('datum_kolaudacie', {'column': 18 }),
    ('spravca_objektu', {'column': 19 }),
    ('uzivatel_objektu', {'column': 20 }),
    ('vstupna_obstaravacia_cena_v_EUR', {'column': 21 }),
    ('zostatkova_cena_v_EUR', {'column': 22 }),
    ('poznamka', {'column': 23 }),
])

# namespaces

ns = {
    'd': 'urn:schemas-microsoft-com:office:spreadsheet',
    'o': 'urn:schemas-microsoft-com:office:office',
    'x': 'urn:schemas-microsoft-com:office:excel',
    'ss': 'urn:schemas-microsoft-com:office:spreadsheet'
}


for filenum, xml_url in enumerate(xml_urls):
    xml_url_text = site_url + xml_url.get('href')
    prt(xml_url_text)

    if not DEBUG:
        xml_text = scraperwiki.scrape(xml_url_text)
        tree = lxml.etree.fromstring(xml_text)
    else:
        tree = lxml.etree.parse('kapitola_majetok_k_300.2015.xml')

    for t, table in enumerate(tree.xpath('//ss:Table', namespaces=ns)):
        prt('Processing table %s' % t)
        table_data = []

        for r, row in enumerate(table.xpath('ss:Row', namespaces=ns)):
            cells = row.xpath('ss:Cell', namespaces=ns)

            # do not even bother with rows shorter than 10 cells
            if len(cells) < 10:
                continue

            # initialize item
            item = collections.OrderedDict()

            # populate item (use static column addresses from the cellmap dict for mapping)
            for (variable, defs) in cellmap.items():
                if len(cells) > defs['column']:
                    if 'type' in defs:
                        res = cells[defs['column']].xpath('ss:Data[@ss:Type=\'' + defs['type'] + '\']/text()', namespaces=ns)
                    else:
                        res = cells[defs['column']].xpath('ss:Data/text()', namespaces=ns)

                    if res:
                        item[variable] = res[0]
                    else:
                        item[variable] = None
                else:
                    item[variable] = None

            if item['id'] is not None and item['organizacia'] is not None:
                table_data.append(item)

        scraperwiki.sqlite.save(unique_keys=['id'],data=table_data)




