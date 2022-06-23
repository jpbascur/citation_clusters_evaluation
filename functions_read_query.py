import requests
import re
import xml
import xml.etree
import xml.etree.ElementTree
import functions_reading # for functions_reading.read_any

pubmed_api_key = 'e1647cd2e088dcd7e5fa490cf69597b28908'
pubmed_api_base = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'

def topic_Api_D(topic_l, filename_part1='boolean_queries\\', filename_part3='_reviewed.txt'):
    """Creates the API dictionary for each topic

    Parameters
    ----------
    topic_l : list
        List of all the topics that have a query file
        
    filename_part1 : str
        First part of the name of the query file
        
    filename_part3 : str
        Third part of the name of the query file

    Returns
    -------
    topic_api_d : dict of dict
        Dictionary with the API data for each topic
    """
    topic_api_d = {}
    for topic in topic_l:
        filename = filename_part1 + str(topic) + filename_part3
        f = functions_reading.read_Any(filename, encoding='UTF-8')
        query_remove_custom = remove_Custom(f, clean_number_rows=True)
        query = format_Query(query_remove_custom)
        topic_api_d[topic] = pumed_Api_Connect_D(query)
    return topic_api_d


def format_Query(query):
    """Formats the query so it fits the PubMed API format.

    Parameters
    ----------
    query : str
        PubMed query

    Returns
    -------
    query : str
        PubMed API query

    Notes
    -------
    This deletes the line breaks and tabs, and replace the spaces with plus signs.
    Acording to the documentation (https://www.ncbi.nlm.nih.gov/books/NBK25497/#chapter2.Handling_Special_Characters_Wit)
    it is necesary replace the spaces with this, and also the -“- and -#- characters with unicode (%22 for “; %23 for #),
    but I have noticed that it works even when you don't replace. I am replacing anyway, just in case.
    """
    query = query.replace('\n', ' ')
    query = query.replace('\t', ' ')
    query = query.replace(' ', '+')
    query = re.sub('\++', '+', query)
    return query

def pumed_Api_Connect_D(query, pubmed_api_key=pubmed_api_key, pubmed_api_base=pubmed_api_base):
    """Creates a dictionary with the data from the API

    Parameters
    ----------
    query : str
        PubMed API query

    Returns
    -------
    d : dictionary
        Dictionary with the data of the API
    """
    d = {}
    d['format_query'] = format_Query(query)
    d['query_url'] = pubmed_api_base + 'esearch.fcgi?term=' + d['format_query'] + '&usehistory=n&retmax=100000&api_key=' + pubmed_api_key
    d['response'] = requests.get(d['query_url'])
    d['id_list'] = query_Pubmeds_Ids(d['response'])
    return d

def retrieve_Pubmed_Title(pubmed_id, pubmed_api_base=pubmed_api_base, pubmed_api_key=pubmed_api_key):
    url = pubmed_api_base + 'esummary.fcgi?db=pubmed&id=' + str(pubmed_id) + '&api_key=' + pubmed_api_key
    response = requests.get(url)
    root = xml.etree.ElementTree.fromstring(response.text)
    docsum_root = root.find('DocSum')
    title_count = 0
    for child in docsum_root.findall('Item'):
        if 'Name' in child.attrib:
            if child.attrib['Name']=='Title':
                title_count += 1
                title = child.text
    if title_count != 1:
        print('Not 1 title')
    pubmed_title = (pubmed_id, title)
    return pubmed_title

def pumed_Api_Connect_D(query):
    """Creates a dictionary with the data from the API

    Parameters
    ----------
    query : str
        PubMed API query

    Returns
    -------
    d : dictionary
        Dictionary with the data of the API
    """
    d = {}
    d['base'] = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    d['api_key'] = 'e1647cd2e088dcd7e5fa490cf69597b28908'
    d['format_query'] = format_Query(query)
    d['query_url'] = d['base'] + 'esearch.fcgi?term=' + d['format_query'] + '&usehistory=n&retmax=100000&api_key=' + d['api_key']
    d['response'] = requests.get(d['query_url'])
    d['id_list'] = query_Pubmeds_Ids(d['response'])
    return d


def remove_Custom(query, end_with_jump=True, clean_number_rows=False, clean_number_parentesis=False, create_jumps=False):
    """Creates a dictionary with the data from the API

    Parameters
    ----------
    query : str
        Unmodified query

    Returns
    -------
    query : str
        Modified query
        
    Notes
    -------
    This function is used mostly for the process of translating the queries into the PubMed format.
    """
    if end_with_jump:
        query += '\n'
    if clean_number_rows:
        query = re.sub(r'#[0-9]*', '\n', query)
    if clean_number_parentesis:
        query = re.sub(r'\([0-9]*\)', '', query)
    if create_jumps:
        query = re.sub(r'OR', '\nOR', query)
        query = re.sub(r'NOT', '\nNOT', query)
        query = re.sub(r'AND', '\nAND', query)
    return query

def query_Pubmeds_Ids(response):
	#  I had to change the way I retrieve the Pubmed IDs
	#  The original function retrieved the ids from the web enviroment (WebEnv), but it limits the maximum to 10000
	#  The new function uses the esearch to get the ids, and it can get up to 100000
	#  There is a way to get more than the maximum (https://www.ncbi.nlm.nih.gov/books/NBK25499/), but I want to avoid it when posible to keep the code simple
    root = xml.etree.ElementTree.fromstring(response.text)
    id_list_root = root.find('IdList')
    id_list = []
    for child in id_list_root:
        pubmed_id = int(child.text)
        id_list.append(pubmed_id)
    return id_list