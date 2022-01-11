# SPDX-License-Identifier: AGPL-3.0-or-later

from lxml import html
from urllib.parse import urlencode
from searx.utils import extract_text, extract_url, eval_xpath, eval_xpath_list

search_url = None
paging = False
results_xpath = ''
soft_max_redirects = 0
template = 'default.html'

field_definition = {}

# parameters for engines with paging support
#
# number of results on each page
# (only needed if the site requires not a page number, but an offset)
page_size = 1
# number of the first page (usually 0 or 1)
first_page_num = 1


def request(query, params):
    query = urlencode({'q': query})[2:]

    fp = {'query': query}
    if paging and search_url.find('{pageno}') >= 0:
        fp['pageno'] = (params['pageno'] - 1) * page_size + first_page_num

    params['url'] = search_url.format(**fp)
    params['query'] = query
    params['soft_max_redirects'] = soft_max_redirects

    return params


def response(resp):
    results = []
    dom = html.fromstring(resp.text)

    for result in eval_xpath_list(dom, results_xpath):

        single_result = {
            'template': template
        }

        for single_field in field_definition:
            node = eval_xpath_list(result, single_field['xpath'], min_len=1)

            if 'extract' in single_field and single_field['extract'] == 'url':
                value = extract_url(node, search_url)
            else:
                value = extract_text(node)

            single_result[single_field['field_name']] = value

        results.append(single_result)

    return results
