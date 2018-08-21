import json

from jchart import Chart
from django.test import TestCase, RequestFactory
from django.utils import six
from django.core.exceptions import ImproperlyConfigured

from .views import ChartView
from . import Chart
from .config import (Title, Legend, Tooltips, Hover,
                     InteractionModes, Animation, Element,
                     ElementArc, Axes, ScaleLabel, Tick, rgba)

# Create your tests here.

class LineChart(Chart):
    chart_type = 'line'
    title = Title(text='Test Title Line')
    legend = Legend(display=False)
    tooltips = Tooltips(enabled=False)
    hover = Hover(mode='default')
    animation = Animation(duration=1.0)
    scales = {
        'xAxes': [Axes(display=False, type='time', position='bottom')],
        'yAxes': [Axes(type='linear',
                       position='left',
                       scaleLabel=ScaleLabel(fontColor='#fff'),
                       ticks=Tick(fontColor='#fff')
                       )],
    }

    def get_datasets(self, *args, **kwargs):
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        return [dict(label='Test Line Chart', data=data)]