import io
import requests

from ..utils import (UNIPROT_KNOWLEDGEBASE,
                               UNIPROT_BATCH,
                               UNIPROT_CONVERT,
                               UNIPROT_MAP,
                               VALID_ID_MAPPINGS,
                               is_value_in_iterable)

def current_release():
    """Get current public release of UniProtKB.

       :returns: release as string

    """
    # Release number contained in request header
    # So we retrieve a random human entry and look up the value
    payload = {"query": "organism:9606 AND reviewed:yes",
               "random": "yes",
               }
    result = requests.get(UNIPROT_KNOWLEDGEBASE, params=payload)
    if result.ok:
        return result.headers['x-uniprot-release'] # Returns string by default
    else:
        result.raise_for_status()

def search_reviewed(query, frmt='txt', file=False):
    '''Search reviewed UniProtKB entries only (Swiss-Prot).

    Accepts standard UniProtKB query syntax.
    Returns data as a string.
    Returns None if no results.
    '''
    result = _search(query, frmt=frmt, reviewed=True,
                     unreviewed=False, file=file)
    return result

def search_unreviewed(query, frmt='txt', file=False):
    '''Search unreviewed UniProtKB entries only (TrEMBL)

    Accepts standard UniProtKB query syntax.
    Returns data as a string.
    Returns None if no results.
    '''
    result = _search(query, frmt=frmt, reviewed=False,
                     unreviewed=True, file=file)
    return result

def search_all(query, frmt='txt', file=False):
    '''Search all of UniProtKB (Swiss-Prot + TrEMBL)

    Accepts standard UniProtKB query syntax.
    Returns data as a string.
    Returns None if no results.
    '''
    result = _search(query, frmt=frmt, reviewed=True,
                     unreviewed=True, file=file)
    return result

def number_SP_hits(query, frmt='list', file=False):
    '''Search reviewed UniProtKB entries only (Swiss-Prot).

    Accepts standard UniProtKB query syntax.
    Returns int, number of hits.
    '''
    result = _search(query, frmt=frmt, reviewed=True,
                     unreviewed=False, file=file)
    if result:
        hit_list = result.split('\n')
        number = len(hit_list) - 1
    else:
        number = 0
    return number


def retrieve_batch(ac_list, frmt='txt', file=False):
    '''Batch retrieval of uniProtKB entries.

    Returns data as a string.
    '''
    payload = {'query':' '.join(ac_list),
               'format':frmt}
    result = requests.get(UNIPROT_BATCH, params=payload)
    if result.ok:
        if len(result.content) > 0:
            if file:
                return _to_StringIO(result.content)
            else:
                return str(result.content, encoding="ascii")
        else:
            return None
    else:
        result.raise_for_status()


def convert(path, typ='uniprot', from_='txt', to='xml', encoding='ascii'):
    '''Convert between different data formats using UniProt service.

    Parameters:
        path: path to file containing entry to be converted
        typ: type of the format; default: uniprot
        from: source format
        to: target format
        encding: encoding of the files to be sent; default: ascii

    Returns:
        string
    '''
    payload = {'type': typ,
               'from': from_,
               'to': to
               }
    files = {'data': open(path, 'r', encoding=encoding)}
    response = requests.post(UNIPROT_CONVERT,
                             data=payload,
                             files=files
                             )
    if response.ok:
        return response.text
    else:
        response.raise_for_status()


def map_id(query, source_fmt, target_fmt, output_fmt='tab'):
    '''Map one set of identifiers to another.

    See http://www.uniprot.org/help/programmatic_access#conversion for details.
    Note: The response.url filed contains the URL from which to download
    the mapping, e.g. http://www.uniprot.org/mapping/M20160504763V34ZKX0.tab

    Args:
        query: string or iterable of strings. If a string then this should consist of space-separated identifiers,
            if an iterable then this should be of individual identifiers.
        source_fmt: string. The format of the provided identifiers. See UniProt help for allowed values.
        target_fmt: string. The desired format of the identifiers. See UniProt help for allowed values.
        output_fmt: string. Desired data structure for response. Defaults to 'tab' (tabular), 'txt' is also valid.

    Returns:
        string in specified output format.
    '''
    if source_fmt.upper() not in VALID_ID_MAPPINGS:
        raise ValueError('{} is not a valid mapping source'.format(source_fmt.upper()))
    if target_fmt.upper() not in VALID_ID_MAPPINGS:
        raise ValueError('{} is not a valid mapping source'.format(target_fmt.upper()))
    if hasattr(query, 'pop'):
        query = ' '.join(query)
    payload = {'from': source_fmt.upper(),
               'to': target_fmt.upper(),
               'format': output_fmt,
               'query': query,
               }
    response = requests.get(UNIPROT_MAP, params=payload)
    if response.ok:
        return response.text
    else:
        response.raise_for_status()


def _search(query, frmt='txt', reviewed=True, unreviewed=True, file=False):
    _check_format(frmt)
    payload = {'query':query, 'format':frmt}
    if reviewed and unreviewed:
        pass
    elif reviewed and not unreviewed:#Swiss-Prot
        payload['query'] += ' AND reviewed:yes'
    elif not reviewed and unreviewed:#TrEMBL
        payload['query'] += ' AND reviewed:no'
    elif not reviewed and not unreviewed:
        msg = ('At least one of parameters `reviewed` and `unreviewed` has to be True.\n'
               'Found: reviewed: {0}, unreviewed: {1}')
        raise ValueError(msg.format(reviewed, unreviewed))
    result = requests.get(UNIPROT_KNOWLEDGEBASE, params=payload)
    if result.ok:
        if len(result.content) > 0:
            if file:
                return _to_StringIO(result.content)
            else:
                return str(result.content, encoding="ascii")
        else:
            return None
    else:
        result.raise_for_status()


def _to_StringIO(text):
    return io.StringIO(text.decode())
    #return io.StringIO(unicode(text))

def _check_format(fmt):
    return_formats = ('html',
                      'tab',
                      'xls',
                      'fasta',
                      'gff',
                      'txt',
                      'xml',
                      'rdf',
                      'list',
                      #'rss',
                      )
    if not is_value_in_iterable(fmt, return_formats):
        msg = 'Allowed values: {0}\nPassed in value: {1}'
        raise ValueError(msg.format(return_formats, fmt))

if __name__ == "__main__":
    print('This is uniprot_query.py.\n')
    test = search_reviewed('name:tax-1 AND taxonomy:11926', file=True)
    print(type(test))
    print(test.getvalue())
    AClist = ['P12344', 'P12345']
    batch = retrieve_batch(AClist, file=False)
    print(batch)


