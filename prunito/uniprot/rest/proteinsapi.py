import requests
from ...utils import PROTEINS_API_TAXONOMY


session = requests.Session()


def get_info_on_taxID(taxID, fmt='json'):
    """Get details about one taxonomic node as identified by a taxID.

    This includes names, rank, UniProt mnemonics, parent, sibling
    and child nodes, if any. This only accepts a single taxID.
    Use get_info_on_taxIDs() for several.

    Args:
        taxID (str or int): Identifier of the taxonomic node you want info on.
            Can be string or integer.
        fmt (str): Format information is wanted in. Can be JSON or XML.
            Defaults to JSON.

    Returns:
        Data (JSON dict or XML string)

    Raises:
        ValueError: If unknown result format is specified.
    """
    fmt = fmt.lower()
    allowed = ('json', 'xml')
    if not fmt in allowed:
        return ValueError('Invalid format: {0}. Choose one of: {1}'.format(fmt,
                                                                           allowed))
    else:
        headers = {'Accept': 'application/{}'.format(fmt)}
        r = session.get('/'.join([PROTEINS_API_TAXONOMY, 'id', str(taxID)]), headers=headers)
        if not r.ok:
            r.raise_for_status()
        else:
            if fmt == 'json':
                return r.json()
            else:
                return r.text


def get_info_on_taxIDs(taxIDs, fmt='json'):
    """Get details about one or more taxonomic node(s) as identified by (a) taxID(s).

    This includes names, rank, UniProt mnemonics, parent, sibling
    and child nodes, if any.

    Args:
        taxIDs (Iterable): Iterable of identifiers of the taxonomic nodes you want info on.
            Items in iterable can be string or integer.
        fmt (str): Format information is wanted in. Can be JSON or XML.
            Defaults to JSON.

    Yields:
        Dicts (if JSON) or XML elements (if XML) for each taxID

    Raises:
        ValueError: If unknown result format is specified.
        ValueError: If taxIDs are not provided as list or tuple.
    """
    fmt = fmt.lower()
    allowed = ('json', 'xml')
    if not fmt in allowed:
        raise ValueError('Invalid result format: {0}. Choose one of: {1}'.format(fmt,
                                                                           allowed))
    if isinstance(taxIDs, str):
        raise ValueError('TaxIDs have to be provided as lists or tuples, not strings.')
    else:
        ids_stringified = ','.join([str(item) for item in taxIDs])
        headers = {'Accept': 'application/{}'.format(fmt)}
        r = session.get('/'.join([PROTEINS_API_TAXONOMY, 'ids', ids_stringified]), headers=headers)
        if not r.ok:
            r.raise_for_status()
        else:
            if fmt == 'json':
                content = r.json()
                for node in content['taxonomies']:
                    yield node
            else:
                from lxml import etree as ET
                tree =  ET.fromstring(r.text)
                for ele in tree.iter('taxonomy'):
                    yield ele


def get_lineage_for_taxID(taxID):
    """Retrieve all ancestor nodes of the given one.

    The data retrieved for each node are taxID and the scientific name.

    Args:
        taxID (str or int): TaxID (NCBI taxonomy identifier)

    Yields:
        dict: Data for each taxID
    """
    headers = {'Accept': 'application/json'}
    r = session.get('/'.join([PROTEINS_API_TAXONOMY, 'lineage', str(taxID)]), headers=headers)
    if not r.ok:
        r.raise_for_status()
    else:
        content = r.json()
        try:
            for node in content['taxonomies']:
                yield node
        except KeyError:
            raise NoDataError(content['errorMessage'])


class NoDataError(Exception):
    pass