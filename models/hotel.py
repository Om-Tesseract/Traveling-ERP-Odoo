from odoo import models, fields


def default_amenities():
    return {
        "Accessibility": [
            "Lift Elevator"
        ],
        "Available in All Rooms": [
            "Air Conditioning",
            "Kitchenette",
            "Ironing Facilities"
        ],
        "Dining, Drinking and Snacking": [
            "Mini Bar",
            "Restaurant",
            "Room Service"
        ],
        "Things to do, ways to relax": [
            "Lawn",
            "Tours"
        ],
        "Fitness and Recreation": [
            "Indoor Games"
        ],
        "Getting Around": [
            "Car Rental Facility"
        ],
        "Internet": [
            "Free WiFi",
            "Wi-Fi in all rooms",
            "Wi-Fi"
        ],
        "Services and Conveniences": [
            "Travel Desk",
            "Concierge Services",
            "Currency Exchange",
            "Daily Housekeeping",
            "Dry Cleaning Service",
            "Laundry",
            "Luggage Storage",
            "Smoking Area",
            "Hot Shower"
        ]
    }
class Hotel(models.Model):
    _name = 'hotel'
    _description = 'Hotel'

    name = fields.Char(string='Name', required=True)
    address = fields.Text(string='Address')
    area = fields.Char(string='Area')
    link = fields.Char(string='Link')
    city_id = fields.Many2one('city.model', string='City')  # Assuming you have a res.city model
    
    star_rating = fields.Integer(string='Star Rating')
    rate = fields.Char(string='Rate')
    review_count = fields.Char(string='Review Count')
    desc = fields.Text(string='Description')
    contact_info = fields.Json(string='Contact Info')  # JSONField equivalent
    image_url = fields.Char(string='Image URL')
    img = fields.Image(string='Image')  # Odoo uses Binary for images
    ln = fields.Float(string='Longitude')
    lat = fields.Float(string='Latitude')
    amenities = fields.Json(string='Amenities')  # JSONField equivalent
    cleanliness_rate = fields.Float(string='Cleanliness Rate')
    service_rate = fields.Float(string='Service Rate')
    comfort_rate = fields.Float(string='Comfort Rate')
    amenities_rate = fields.Float(string='Amenities Rate')
    room_category= fields.One2many('room.category','hotel_id',string="Room category")
    hotel_imgs= fields.One2many('hotel.images','hotel_id',string="Hotel image")

class HotelImages(models.Model):
    _name = 'hotel.images'
    _description = 'Hotel Images'

    hotel_id = fields.Many2one('hotel', string='Hotel')
    image = fields.Image(string='Image')
    img_url = fields.Char(string='Image URL')
class RoomCategory(models.Model):
    _name = 'room.category'
    _description = 'Room Category'

    hotel_id = fields.Many2one('hotel', string='Hotel')
    name = fields.Char(string='Name')
    desc = fields.Text(string='Description')
    view_name = fields.Char(string='View Name')
    room_size = fields.Char(string='Room Size')
    bed_type = fields.Char(string='Bed Type')
    room_img= fields.One2many('rooms.img','room_category_id',string='Room Image')
    rooms=fields.One2many('room.type','category_id',string="Rooms")
class RoomType(models.Model):
    _name = 'room.type'
    _description = 'Room Type'

    rnm = fields.Char(string='Room Name')
    cur = fields.Char(string='Currency')
    meal_plan = fields.Char(string='Meal Plan')
    price = fields.Float(string='Price')
    availability = fields.Boolean(string='Availability', default=True)
    amenity = fields.Json(string='Amenity')  # JSONField equivalent
    key = fields.Json(string='Key')  # JSONField equivalent
    meal_includes = fields.Char(string='Meal Includes')
    category_id = fields.Many2one('room.category', string='Room Category')


class RoomsImg(models.Model):
    _name = 'rooms.img'
    _description = 'Room Images'

    room_category_id = fields.Many2one('room.category', string='Room Category')
    img = fields.Image(string='Image')
    img_url = fields.Char(string='Image URL')