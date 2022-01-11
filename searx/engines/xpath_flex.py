# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 Yahoo (Web)
"""

from lxml import html
from urllib.parse import urlencode
from searx import logger
from searx.utils import extract_text, extract_url, eval_xpath, eval_xpath_list

logger = logger.getChild('xpath_general engine')

search_url = None
paging = False
results_xpath = ''
soft_max_redirects = 0
template = 'default.html'
unresolvable_value = ''  # will be set if expression cannot be resolved
default_field_settings = {'single_element': False}

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
            single_field = {**default_field_settings, **single_field}
            try:
                if single_field['single_element']:
                    node = eval_xpath(result, single_field['xpath'])
                else:
                    node = eval_xpath_list(result, single_field['xpath'])

                if 'extract' in single_field and single_field['extract'] == 'url':
                    value = extract_url(node, search_url)
                elif 'extract' in single_field and single_field['extract'] == 'boolean':
                    value = (isinstance(node, list) and len(node) > 0)
                elif 'extract' in single_field and single_field['extract'] == 'boolean_negate':
                    value = (isinstance(node, list) and len(node) < 1)
                else:
                    value = extract_text(node)

                single_result[single_field['field_name']] = value
            except Exception as e:
                logger.warning('error in resolving field %s:\n%s', single_field['field_name'], e)
                single_result[single_field['field_name']] = unresolvable_value

        results.append(single_result)

    return results
