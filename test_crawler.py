import pytest
from utils import crawler

def test_crawler_initialization():
    assert crawler is not None
    assert hasattr(crawler, 'crawl_all')
    assert hasattr(crawler, 'display_results')
