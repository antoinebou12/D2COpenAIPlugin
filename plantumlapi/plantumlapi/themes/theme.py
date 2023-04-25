from enum import Enum

class THEMES(Enum):
    NONE = 'none'
    AMIGA = 'amiga'
    AWS_ORANGE = 'aws-orange'
    BLACK_KNIGHT = 'black-knight'
    BLUEGRAY = 'bluegray'
    BLUEPRINT = 'blueprint'
    CARBON_GRAY = 'carbon-gray'
    CERULEAN = 'cerulean'
    CERULEAN_OUTLINE = 'cerulean-outline'
    CLOUDSCAPE_DESIGN = 'cloudscape-design'
    CRT_AMBER = 'crt-amber'
    CRT_GREEN = 'crt-green'
    CYBORG = 'cyborg'
    CYBORG_OUTLINE = 'cyborg-outline'
    HACKER = 'hacker'
    LIGHTGRAY = 'lightgray'
    MARS = 'mars'
    MATERIA = 'materia'
    MATERIA_OUTLINE = 'materia-outline'
    METAL = 'metal'
    MIMEOGRAPH = 'mimeograph'
    MINTY = 'minty'
    PLAIN = 'plain'
    REDDRESS_DARKBLUE = 'reddress-darkblue'
    REDDRESS_DARKGREEN = 'reddress-darkgreen'
    REDDRESS_DARKORANGE = 'reddress-darkorange'
    REDDRESS_DARKRED = 'reddress-darkred'
    REDDRESS_LIGHTBLUE = 'reddress-lightblue'
    REDDRESS_LIGHTGREEN = 'reddress-lightgreen'
    REDDRESS_LIGHTORANGE = 'reddress-lightorange'
    REDDRESS_LIGHTRED = 'reddress-lightred'
    SANDSTONE = 'sandstone'
    SILVER = 'silver'
    SKETCHY = 'sketchy'
    SKETCHY_OUTLINE = 'sketchy-outline'
    SPACELAB = 'spacelab'
    SPACELAB_WHITE = 'spacelab-white'
    SUPERHERO = 'superhero'
    SUPERHERO_OUTLINE = 'superhero-outline'
    TOY = 'toy'
    UNITED = 'united'
    VIBRANT = 'vibrant'

class EXTERNAL_THEMES(Enum):
    AWSPuml = 'https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v15.0/dist'

class Theme:
    def __init__(self, theme):
        self.theme = theme

    def add_theme(self):
        if self.theme not in THEMES.__members__:
            raise ValueError(f'Theme not found: {self.theme}')
        return THEMES[self.theme].value

    def add_plantuml(self):
        return f'!theme {self.add_theme()}'

    def __str__(self):
        return self.theme

    def __repr__(self):
        return self.theme



