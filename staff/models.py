from django.db import models
import json

class Settings():
    def __init__(self):
        try:
            with open("staff/settings.json", "r") as settings_file: 
                settings = json.load(settings_file)
                self.shop_name = settings['shop_name']
                self.primary_colour = settings['primary_colour']
                self.secondary_colour = settings['secondary_colour']
        except:
            self.shop_name = "No Name"
            self.primary_colour = "#c1c1c1"
            self.secondary_colour = "#c1c1c1"

    def update(self, new_settings):
        try:
            with open("staff/settings.json", "w") as settings_file: 
                json.dump(new_settings, settings_file)
        except:
            print("Error")
    
    def as_dict(self):
        try:
            with open("staff/settings.json", "r") as settings_file: 
                return json.load(settings_file)
        except:
            return None

    def get_text_colour_primary(self):
        colour = self.primary_colour[1:]
        r = int(colour[0:2], 16); # hexToR
        g = int(colour[2:4], 16); # hexToG
        b = int(colour[4:6], 16); # hexToB
        return "#000000" if (((r * 0.299) + (g * 0.587) + (b * 0.114)) > 186) else "#FFFFFF"
    
    def is_primary_light_or_dark(self):
        return "light" if self.get_text_colour_primary() == "#000000" else "dark"