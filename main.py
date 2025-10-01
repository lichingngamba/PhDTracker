#####################
# main.py           # 
# version: 1        #
#####################
"""This module serves as the entry point for the PhD admission tracker application."""
from utils import crawler

def main():
    """Main function to run the PhD admission crawler."""
    crawler.crawl_all
    return crawler.display_results
if __name__ == "__main__":
    main()