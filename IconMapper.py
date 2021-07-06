class IconMapper():

    cat = None
    default_val = ('fa', 'dot-circle')
    icon_map = None

    def __init__(self):
        self.icon_map = {
            'Grocery Stores' : ('fa', 'shopping-cart'),
            'Rail Transportation' : ('fa', 'train'),
            'Clothing Stores' : ('fa', 'mitten'), # doesn't work
            'Beer, Wine, and Liquor Stores' : ('fa', 'beer'),
            'Colleges, Universities, and Professional Schools' : ('fa', 'graduation-cap'),
            'Health and Personal Care Stores' : ('fa', 'heartbeat'),
            'Gasoline Stations' : ('fa', 'gas-pump'), # doesn't work
            'Restaurants and Other Eating Places' : ('glyphicon', 'cutlery'),
            'Book Stores and News Dealers' : ('glyphicon', 'book'),
            'Wired and Wireless Telecommunications Carriers' : ('fa', 'phone'),
            'Sporting Goods, Hobby, and Musical Instrument Stores' : ('fa', 'futbol-o'),
            'Offices of Dentists' : ('fa', 'tooth') # doesn't work
        }
    
    def getLogo(self, cat):
        self.cat = cat
        prefix, code = self.icon_map.get(self.cat, self.default_val)
        return (prefix, code)