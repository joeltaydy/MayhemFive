from __future__ import absolute_import, unicode_literals
from celery.utils.log import get_task_logger
from celery.task import task
from Module_TeamManagement.src.utilities import webScrapper
from bs4 import BeautifulSoup
logger = get_task_logger(__name__)


@task(name="trailheadscrapper")
def webscrapper():
    """
    Saves latest image from Flickr
    """
    print("12b")
    webScrapper()
    print("23d")
    logger.info("Saved image from Flickr") 