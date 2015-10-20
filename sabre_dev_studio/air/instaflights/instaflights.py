import requests
import json
import datetime

from ... import sabre_dev_studio

class Instaflights(sabre_dev_studio.SabreDevStudio):
    def __init__(self, *args, **kwargs):
        super(Instaflights, self).__init__(args, kwargs)

    
