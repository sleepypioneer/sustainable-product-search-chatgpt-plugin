# Code adapted from https://github.com/gsingers/search_engineering

import pandas as pd
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk
import logging
import click
from time import perf_counter
import concurrent.futures

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)s:%(message)s')


def get_opensearch(the_host="localhost"):
    host = the_host
    port = 9200
    auth = ('admin', 'admin')
    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_compress=True,
        http_auth=auth,
        use_ssl=True,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
    )
    return client


def index_file(file, index_name, host="localhost", max_docs=2000000, batch_size=200):
    docs_indexed = 0
    client = get_opensearch(host)
    logger.debug(f'Processing file : {file}')
    df = pd.read_csv(file, dtype={15: str, 17: str})
    df = df.fillna('')
    df['index_col'] = df.index
    batch_size = min(max_docs, batch_size)
    docs = []
    time_indexing = 0

    for _, row in df.iterrows():
        if docs_indexed >= max_docs:
            break
        doc = row.to_dict()
        docs.append({'_index': index_name, '_id': doc['index_col'], '_source': doc})
        docs_indexed += 1
        if docs_indexed % batch_size == 0:
            start = perf_counter()
            bulk(client, docs, request_timeout=120)
            stop = perf_counter()
            time_indexing += (stop - start)
            docs = []
    if len(docs) > 0:
        logger.debug("Sending final batch of docs")
        start = perf_counter()
        bulk(client, docs, request_timeout=120)
        stop = perf_counter()
        time_indexing += (stop - start)
    logger.debug(f'{docs_indexed} documents indexed in {time_indexing}')
    return docs_indexed, time_indexing


@click.command()
@click.option('--source_file', '-s', help='CSV source file')
@click.option('--index_name', '-i', default="green_products", help="The name of the index to write to")
@click.option('--workers', '-w', default=8, help="The number of workers/processes to use")
@click.option('--host', '-o', default="localhost", help="The name of the host running OpenSearch")
@click.option('--max_docs', '-m', default=200000, help="The maximum number of docs to be indexed PER WORKER PER FILE.")
@click.option('--batch_size', '-b', default=200, help="The number of docs to send per request. Max of 5000")
@click.option('--refresh_interval', '-r', default="-1", help="The number of docs to send per request. Max of 5000")
def main(source_file: str, index_name: str, workers: int, host: str, max_docs: int, batch_size: int, refresh_interval: str):
    batch_size = min(batch_size, 5000)
    logger.info(
        f"Indexing {source_file} to {index_name} with {workers} workers, refresh_interval of {refresh_interval} to host {host} with a maximum number of docs sent per file per worker of {max_docs} and {batch_size} per batch.")
    docs_indexed = 0

    client = get_opensearch(host)

    logger.debug(client.indices.get_settings(index=index_name))
    start = perf_counter()
    time_indexing = 0
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        future = executor.submit(index_file, source_file, index_name, host, max_docs, batch_size)
        num_docs, the_time = future.result()
        docs_indexed += num_docs
        time_indexing += the_time

    finish = perf_counter()
    logger.debug(client.indices.get_settings(index=index_name)) 
    logger.info(f'Done. {docs_indexed} were indexed in {(finish - start)/60} minutes.  Total accumulated time spent in `bulk` indexing: {time_indexing/60} minutes')


if __name__ == "__main__":
    main()
