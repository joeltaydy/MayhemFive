from __future__ import absolute_import, unicode_literals
from celery.utils.log import get_task_logger
from celery import shared_task
from Module_TeamManagement.src import utilities

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

 @shared_task(name='tableaurefresh')
 def tableaurefresh():

     """
     Saves latest image from Flickr
     """
     utilities.tableauRefresh()

     logger.info("trailhead last updated at ")

 #if __name__ == "__main__":
  #   webscrapper()
