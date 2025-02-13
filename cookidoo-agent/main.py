import argparse
import asyncio
from . import query_recipe, load_database

def parse_args():
    parser = argparse.ArgumentParser(description="Cookidoo Agent")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    parser_query = subparsers.add_parser("query", help="Query recipes using ChatGPT")
    parser_query.add_argument("--query", type=str, help="Query string")
    
    subparsers.add_parser("load", help="Load recipes into Milvus database")
    
    return parser.parse_args()

def main():
    args = parse_args()
    if args.command == "query":
        if args.query:
            asyncio.run(query_recipe.main(args.query))
        else:
            # test query
            asyncio.run(query_recipe.main(query="Wyszukaj mi trzy przepisy na obiad, które zawierają kurczaka i całkowity czas przygotowania jest krótszy niz godzina"))
    elif args.command == "load":
        asyncio.run(load_database.main())

if __name__ == "__main__":
    main()
