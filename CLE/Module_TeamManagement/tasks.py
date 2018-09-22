from __future__ import absolute_import, unicode_literals
from celery.utils.log import get_task_logger
from celery import shared_task, shared_tasktwo
from celery import task
from Module_TeamManagement.src import utilities
from Module_TeamManagement.src import selenium_using_chrome

logger = get_task_logger(__name__)


@shared_task(name='trailheadscrapper')
def webscrapper():

    """
    Saves latest image from Flickr
    """
    utilities.webScrapper()

    logger.info("trailhead last updated at ")

#if __name__ == "__main__":
 #   webscrapper()

@shared_tasktwo(name='tableaurefresh')
def tableaurefresh():
     selenium = SeleniumTableau()
     selenium.run()

     logger.info("tableaurefresh done")

 #if __name__ == "__main__":
  #   webscrapper()
