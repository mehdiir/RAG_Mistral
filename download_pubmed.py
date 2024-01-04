r"""
Python script to download PubMed `N_max` articles abstracts for a user's specified period
  Example to run this conversion script:
    python download_pubmed.py \
     --output_json $PATH_TO_JSON_FILE
     --num_articles 1000 \
     --start_date "2023/11/01" \
     --end_date "2023/11/30"

"""
from argparse import ArgumentParser
import time

from Bio import Entrez
import json


def search(query, max_num_articles):
    "Retrieve the ids of first `max_num_articles` based on the provided query"
    handle = Entrez.esearch(db='pubmed', 
                            sort='relevance', 
                            retmax=max_num_articles,
                            retmode='xml', 
                            term=query)
    results = Entrez.read(handle)
    return results

def fetch_details(id_list):
    """
    Fetch the metadata of PubMed articles based on their IDs
    """
    ids = ','.join(id_list)
    handle = Entrez.efetch(db='pubmed', 
                        retmode='xml', 
                        id=ids)
    results = Entrez.read(handle)
    return results


def get_pubmed_data(
    output_json_file: str, 
    start_date: str = "2023/12/1",
    end_date: str = "2023/12/31",
    email: str = 'mehdi.iraqui@gmail.com', 
    max_num_articles: int = 10000
):
    """
    Download the first `max_num_articles` pubmed abstracts published between `start_date` and `end_date`
    
    Parameters: 
    ----------
    output_json_file: Path to the JSON file where to store the downloaded articles
    start_date: Start date, in the format of "%Y/%m/%d", for the PubMed article search based on their publication date.
    end_date: End date for, in the format of "%Y/%m/%d", the PubMed articles search based on their publication date.
    """
    # Always provide your email when using Entrez
    Entrez.email = email

    # Format the date range in YYYY/MM/DD format for the query
    query = f"({start_date}[Date - Publication] : {end_date}[Date - Publication])"
    start_time = time.time()
    # Search for articles
    results = search(query, max_num_articles=max_num_articles)
    id_list = results['IdList']

    # Fetch details of retrieved articles
    papers = fetch_details(id_list)
    
    # Retrieve titles, dates and abstracts. 
    # Keep only articles where date and abstract information is available
    result = {}
    for i, paper in enumerate(papers['PubmedArticle']):
        abstract = paper['MedlineCitation']['Article'].get('Abstract')
        date = paper['MedlineCitation']['Article']['ArticleDate']
        if abstract and date:
            result[i] = {
                "article_title": paper['MedlineCitation']['Article']['ArticleTitle'],
                "article_abstract": abstract['AbstractText'][0],
                "pub_date": {
                        "year": paper['MedlineCitation']['Article']['ArticleDate'][0]['Year'],
                        "month": paper['MedlineCitation']['Article']['ArticleDate'][0]['Month'],
                        "day": paper['MedlineCitation']['Article']['ArticleDate'][0]['Day'],
                }
            }
                    
        else:
            # Keep only articles with an abstract and a publication date
            pass
    print(f"{len(result)} PubMed articles were downloadded in {time.time()-start_time}")
    # save data to json:
    with open(output_json_file, 'w') as f:
        f.write(json.dumps(list(result.values())))
        

def get_args():
    parser = ArgumentParser()
    parser.add_argument(
        "--output_json",
        type=str,
        default=None,
        required=True,
        help="Path to the JSON file where to store the downloaded articles",
    )
    parser.add_argument(
        "--start_date",
        type=str,
        default=None,
        required=True,
        help="Start date for the PubMed search",
    )
    parser.add_argument(
        "--end_date",
        type=str,
        default=None,
        required=True,
        help="End date for the PubMed search",
    )
    parser.add_argument(
        "--num_articles",
        type=int,
        default=1000,
        help="The numer of articles to retrieve from the PubMed search query",
    )
    #num_articles
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = get_args()
    get_pubmed_data(output_json_file=args.output_json, start_date=args.start_date, end_date=args.end_date, max_num_articles=args.num_articles)
