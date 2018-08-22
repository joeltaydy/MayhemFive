from __future__ import absolute_import, unicode_literals
from celery.utils.log import get_task_logger
from celery import shared_task
from Module_TeamManagement.src import utilities

logger = get_task_logger(__name__)


@shared_task(name='trailheadscrapper')
def webscrapper():
    from bs4 import BeautifulSoup
    """
    Saves latest image from Flickr
    """
    print("12b")
    utilities.webScrapper()
    print("23d")
    logger.info("Saved image from Flickr") 

#if __name__ == "__main__":
 #   webscrapper()