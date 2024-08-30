import itertools
from odoo import models, fields, api
from datetime import datetime, timedelta


class ItineraryPackage(models.Model):
    _name = 'travel.itinerary'
    _description = 'Itinerary Package'
    _rec_name='package_name'
    package_name = fields.Char(string="Package Name", required=True)
    customer_id = fields.Many2one('travel.customers', string="Customer")
    customer_name = fields.Char(
        string="Customer Name", compute='_compute_customer_name', store=True)
    leaving_from_id = fields.Many2one('city.model', string="Leaving From")
    leaving_from = fields.Char(
        string="Leaving From", compute='_compute_leaving_from', store=True)
    nationality_id = fields.Many2one('country.model', string="Nationality")
    nationality = fields.Char(string="Nationality",
                              compute='_compute_nationality', store=True)
    leaving_on = fields.Datetime(string="Leaving On", required=True)
    number_of_rooms = fields.Integer(string="Number of Rooms", default=1)
    number_of_adults = fields.Integer(string="Number of Adults", default=1)
    number_of_children = fields.Integer(string="Number of Children", default=0)
    company_id = fields.Many2one('res.company', string="Company")
    is_final = fields.Boolean(string="Is Final", default=False)

    INTEREST_CHOICES = [
        ('honeymoon', 'Honeymoon'),
        ('luxury', 'Luxury'),
        ('leisure', 'Leisure'),
        ('spa', 'Spa'),
        ('history', 'History'),
        ('art_and_culture', 'Art and Culture'),
        ('adventure', 'Adventure'),
        ('shopping', 'Shopping'),
        ('entertainment', 'Entertainment'),
        ('nightlife', 'Nightlife'),
    ]
    interests = fields.Selection(INTEREST_CHOICES, string="Interests")

    TRAVEL_CHOICES = [
        ('couple', 'Couple'),
        ('family', 'Family'),
        ('friends', 'Friends'),
    ]
    who_is_travelling = fields.Selection(
        TRAVEL_CHOICES, string="Who is Travelling")

    # Checkbox fields
    # Couple
    pregnant_women = fields.Boolean(string="Pregnant Women", default=False)
    elderly_people = fields.Boolean(string="Elderly People", default=False)
    with_walking_difficulty = fields.Boolean(
        string="With Walking Difficulty", default=False)
    # Family
    teenager = fields.Boolean(string="Teenager", default=False)
    # Friends
    women_only = fields.Boolean(string="Women Only", default=False)
    men_only = fields.Boolean(string="Men Only", default=False)

    room_type = fields.Char(string="Room Type")
    star_rating = fields.Integer(string="Star Rating", default=3)
    add_transfers = fields.Boolean(string="Add Transfers", default=False)
    add_tours_and_travels = fields.Boolean(
        string="Add Tours and Travels", default=False)

    status_choices = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]
    status = fields.Selection(
        status_choices, string="Status", default="pending")
    citynight_ids = fields.One2many(
        'travel.city.night',
        'itinerary_id',
        string="City Nights"
    )

    @api.depends('customer_id')
    def _compute_customer_name(self):
        for record in self:
            record.customer_name = record.customer_id.name

    @api.depends('nationality_id')
    def _compute_nationality(self):
        for record in self:
            record.nationality = record.nationality_id.nationality

    @api.depends('leaving_from_id')
    def _compute_leaving_from(self):
        for record in self:
            record.leaving_from = record.leaving_from_id.name

    @api.model
    def create(self, vals):
        # Create the Itinerary Package first
        city_nights_data = vals.pop('citynight_ids', [])
        company = self.env.user.company_id
        vals['company_id']=company.id
        print("============>",company.id)
        package = super(ItineraryPackage, self).create(vals)

        hotel_leaving_date = package.leaving_on
        itin_city_change_last_date = package.leaving_on
        self.add_road_transport(package, city_nights_data[0][2].get('city_id'))
        # Create CityNight instances and add hotel details
        for city_night_data in city_nights_data:
            # Accessing the dictionary inside the list of city nights
            city_night_vals = city_night_data[2]
            city_night_vals['itinerary_id'] = package.id
            city_night = self.env['travel.city.night'].create(city_night_vals)
            print('====================>', city_night)
            # Add hotel details
            self.add_hotel_detail(package, city_night, hotel_leaving_date)
            self.add_itinerary(package, city_night, itin_city_change_last_date)

            # Update the hotel leaving date for the next iteration
            hotel_details = self.env['travel.hotel.details'].search(
                [('package_id', '=', package.id)], order='id desc', limit=1)
            hotel_leaving_date = hotel_details.check_out_date

            # Update itinerary city change last date
            itinerary_date = self.env['travel.itinerary'].search(
                [('id', '=', package.id)], order='id  desc', limit=1)
            itin_city_change_last_date = itinerary_date.leaving_on + \
                timedelta(days=1)
        self.add_last_itinerary(package)
        return package
    def delete_hotels_detail(self,package_id, citynight):
        hotel_details = self.env['travel.hotel.details'].search([
            ('package_id', '=', package_id.id),
            ('citynight_id', '=', citynight.id)
        ])
        hotel_details.unlink()
    def delete_itinerary(self,package_id, citynight):
        itinerary_detail = self.env['travel.itinerary.days'].search([
            ('package_id', '=', package_id.id),
            ('citynight_id', '=', citynight.id)
        ])
        itinerary_detail.unlink()
    def write(self,vals):
        city_nights_data = vals.pop('citynight_ids', [])
        result=super(ItineraryPackage, self).write(vals)
        for package in self:
            hotel_leaving_date = package.leaving_on
            itin_city_change_last_date = package.leaving_on
            for city_night_data in city_nights_data:
                    city_night_id = city_night_data[1] if len(city_night_data) > 1 else None
                    city_night_vals = city_night_data[2] if len(city_night_data) > 2 else {}

                    if city_night_id:
                        city_night = self.env['travel.city.night'].browse(city_night_id)
                        city = self.env['city.model'].browse(city_night_vals.get('city_id'))

                        if city_night.city_id != city:
                            city_night.write({
                                'nights': city_night_vals.get('nights', city_night.nights),
                                'sequence': city_night_vals.get('sequence', city_night.sequence),
                                'city_id': city.id
                            })
                            self.delete_hotels_detail(package,city_night)
                            self.delete_itinerary(package,city_night)
                            # self.delete_hotels_and_itineraries(package, city_night)
                            self.add_hotel_detail(package, city_night, hotel_leaving_date)
                            self.add_itinerary(package, city_night, itin_city_change_last_date)
                            print("*****************************Change city************************")

                            hotel_leaving_date = self.env['travel.hotel.details'].search([('package_id.id', '=', package.id)], limit=1).check_out_date
                            itin_city_change_last_date = self.env['travel.itinerary.days'].search([('package_id.id', '=', package.id)], order='days desc', limit=1).days + timedelta(days=1)

                        elif city_night.nights < city_night_vals.get('nights', city_night.nights):
                            add_night_count = city_night_vals.get('nights', city_night.nights) - city_night.nights
                            city_night.write({
                                'nights': city_night_vals.get('nights', city_night.nights),
                                'sequence': city_night_vals.get('sequence', city_night.sequence),

                                'city_id': city.id
                            })
                            print("*****************************add night************************")
                            self.add_nights(city_night, abs(add_night_count))

                        elif city_night.nights > city_night_vals.get('nights', city_night.nights):
                            print("*****************************remove night************************")
                        
                            remove_night_count = city_night_vals.get('nights', city_night.nights) - city_night.nights
                            city_night.write({
                                'nights': city_night_vals.get('nights', city_night.nights),
                                'city_id': city.id,
                                'sequence': city_night_vals.get('sequence', city_night.sequence),
                           
                            })
                            self.reduce_nights(city_night, abs(remove_night_count))


                    else:
                        print("*****************************Create city nights************************")

                        city_night = self.env['travel.city.night'].create({
                            'itinerary_id': package.id,
                            **city_night_vals
                        })
                        self.add_hotel_detail(package, city_night, hotel_leaving_date)
                        self.add_itinerary(package, city_night, itin_city_change_last_date)
                        hotel_leaving_date = self.env['travel.hotel.details'].search([('package_id.id', '=', package.id)], limit=1).check_out_date
                        itin_city_change_last_date = self.env['travel.itinerary.days'].search([('package_id.id', '=', package.id)], order='days desc', limit=1).days + timedelta(days=1)

            self.reschedule(package)

        return result
    
    def reschedule(self,package):
        itinerary_activities = self.env['travel.itinerary.activity'].search([
            ('activity_name', 'ilike', 'Departure from'),
            ('itinerary_id.package_id.id', '=', package.id)
        ]).mapped('itinerary_id').ids

        self.env['travel.itinerary.days'].browse(itinerary_activities).unlink()

        itineraries = self.env['travel.itinerary.days'].search([('package_id', '=', self.id)], order='citynight_id')
        start_itin_date = self.leaving_on

        for itinerary in itineraries:
            itinerary.write({'days': start_itin_date})
            start_itin_date += timedelta(days=1)

        hotel_ck_in_date = self.leaving_on

        cn_list = self.env['travel.city.night'].search([('itinerary_id.id', '=', package.id)])
        for cn in cn_list:
            hotel_details = self.env['travel.hotel.details'].search([
                ('package_id', '=', package.id),
                ('citynight_id', '=', cn.id)
            ])
            hotel_details.write({
                'check_in_date': hotel_ck_in_date,
                'check_out_date': hotel_ck_in_date + timedelta(days=cn.nights),
                'number_of_rooms': self.number_of_rooms,
            })

            hotel_ck_in_date = hotel_details[:1].check_out_date

        self.add_last_itinerary(package)

    def add_nights(self, city_night, additional_nights):
        itineraries = self.env['travel.itinerary.days'].search([
            ('citynight_id', '=', city_night.id),
          
        ], order='days')

        last_itinerary = itineraries[-1]
        last_day = last_itinerary.days if last_itinerary else city_night.itinerary_id.leaving_on

        last_seq = self.env['travel.itinerary.activity'].search([
            ('itinerary_id', '=', last_itinerary.id)
        ], order='sequence')[:1]

        remove_activity_list = self.env['travel.itinerary.activity'].search([
            ('itinerary_id.citynight_id', '=', city_night.id)
        ]).mapped('activity_name')

        activity_list = self.env['travel.activity'].search([
            ('activity_city_id', '=', city_night.city_id.id),
            ('activity_name', 'not ilike', 'Departure from'),
            ('activity_name', 'not ilike', 'Arrival at'),
            # ('activity_name', 'not in', remove_activity_list)
        ], order='sequence')

        for i in range(additional_nights):
            new_day = last_day + timedelta(days=i + 1)
            activity = activity_list[i % len(activity_list)] if activity_list else self.env['travel.activity'].create({
                'activity_name': 'Day at Leisure',
                'activity_city_id': city_night.city_id.id,
                'category': ['leisure'],
                'activity_desc': f"Explore {city_night.city_id.name} on your own"
            })

            itinerary = self.env['travel.itinerary.days'].create({
                'package_id': city_night.itinerary_id.id,
                'citynight_id': city_night.id,
                'days': new_day,
                
            })

            self.env['travel.itinerary.activity'].create({
                'itinerary_id': itinerary.id,
                'category': activity.category or ['leisure'],
                'duration': activity.duration,
                'age_limit': activity.age_limit,
                'activity_name': activity.activity_name or 'Day at Leisure',
                'sequence': last_seq.sequence + 1 if last_seq else 1,
                'activity_desc': activity.activity_desc,
                'activity_city_id': activity.activity_city_id.id
            })

    def reduce_nights(self, city_night, reduced_nights):
            # First, find and order the itineraries based on 'days'
            itineraries = self.env['travel.itinerary.days'].search([
                ('citynight_id', '=', city_night.id)
            ], order='days')

            # Get the IDs of itineraries to exclude (those that have activities like 'Departure from' or 'Arrival at')
            itineraries_not_act = self.env['travel.itinerary.activity'].search([
                '|',
                ('activity_name', 'ilike', 'Departure from'),
                ('activity_name', 'ilike', 'Arrival at'),
                ('itinerary_id', 'in', itineraries.ids)
            ]).mapped('itinerary_id').ids

            # Filter itineraries based on those not already excluded
            itineraries = itineraries.filtered(lambda it: it.id not in itineraries_not_act)

            # Get the itineraries to delete based on reduced nights
            itineraries_to_delete = itineraries[-reduced_nights:]

            # Unlink the itineraries to delete
            itineraries_to_delete.unlink()

    def add_last_itinerary(self, instance,):
        last_itinerary = self.env['travel.itinerary.days'].search(
            [('package_id', '=', instance.id)], order='id  desc', limit=1)
        itinerary = self.env['travel.itinerary.days'].create({
            'package_id': instance.id,
            'days': last_itinerary.days + timedelta(days=1),
            'citynight_id': last_itinerary.citynight_id.id,
        })
        leisure_category = self.env['travel.activity.category'].search(
            [('name', '=', 'Leisure')], limit=1)
        if not leisure_category:
            leisure_category = self.env['travel.activity.category'].create({
                                                                           'name': 'Leisure'})
        activity_departure = self.env['travel.activity'].search([
            ('activity_city_id', '=', last_itinerary.citynight_id.city_id.id),
            ('activity_name', '=',
             f"Departure from {last_itinerary.citynight_id.city_id.name}"),

        ], order='sequence', limit=1)
        if not activity_departure:
            activity_departure = self.env['travel.activity'].create({
                'activity_name': f"Departure from {last_itinerary.citynight_id.city_id.name}",
                'activity_city_id': last_itinerary.citynight_id.city_id.id,
                'activity_desc': f"Departure from {last_itinerary.citynight_id.city_id.name}.",
                'category': [(6, 0, [leisure_category.id])]
            })
        last_seq = self.env['travel.itinerary.activity'].search([
            ('itinerary_id.package_id', '=', instance.id)
        ], order='sequence desc', limit=1).sequence or 0

        self.env['travel.itinerary.activity'].create({
            'itinerary_id': itinerary.id,
            'category': [(6, 0, [leisure_category.id])],
            'duration': activity_departure.duration,
            'age_limit': activity_departure.age_limit,
            'activity_name': activity_departure.activity_name,
            'sequence': last_seq + 1,
            'activity_desc': activity_departure.activity_desc,
            'activity_city_id': activity_departure.activity_city_id.id
        })

    def add_hotel_detail(self, package, city_night, hotel_leaving_date):
        Hotel = self.env['hotel']
        RoomType = self.env['room.type']
        HotelDetails = self.env['travel.hotel.details']

        # Search for a hotel matching the city and star rating
        hotel_obj = Hotel.search([('city_id', '=', city_night.city_id.id),
                                  ], limit=1)

        if hotel_obj:
            room_types = RoomType.search(
                [('category_id.hotel_id', '=', hotel_obj.id)], limit=1)
            per_night_price = room_types.price if room_types else 0
            total_price = per_night_price * city_night.nights

            # Create hotel detail
            hotel_detail = {
                "package_id": package.id,
                "hotel_id": hotel_obj.id,
                "check_in_date": hotel_leaving_date,
                "check_out_date": hotel_leaving_date + timedelta(days=city_night.nights),
                "number_of_rooms": package.number_of_rooms,
                "room_id": room_types.id if room_types else None,
                "meal_plans": room_types.meal_plan if room_types else None,
                "category": room_types.category_id.id,
                "total_price": total_price,
                "citynight_id": city_night.id,
            }
            HotelDetails.create(hotel_detail)
        else:
            hotel_detail = {
                "package_id": package.id,
                "check_in_date": hotel_leaving_date,
                "check_out_date": hotel_leaving_date + timedelta(days=city_night.nights),
                "number_of_rooms": package.number_of_rooms,
                "citynight_id": city_night.id,
            }
            HotelDetails.create(hotel_detail)

    def add_itinerary(self, package, city_night, itin_city_change_last_date):
        activity_qs = self.env['travel.activity'].search([
            ('activity_city_id', '=', city_night.city_id.id),
            ('activity_name', 'not ilike', 'Departure from'),
            ('activity_name', 'not ilike', 'Arrival at')
        ], order='sequence')

        # Create an iterator to cycle through activities
        activity_cycle = iter(activity_qs)
        leisure_category = self.env['travel.activity.category'].search(
            [('name', '=', 'Leisure')], limit=1)
        if not leisure_category:
            leisure_category = self.env['travel.activity.category'].create({
                                                                           'name': 'Leisure'})

        for i in range(city_night.nights):
            # Get the next activity or fall back to 'Day at Leisure'
            if i == 0:
                activity_arrival = self.env['travel.activity'].search([
                    ('activity_city_id', '=', city_night.city_id.id),
                    ('activity_name', '=',
                     f"Arrival at {city_night.city_id.name}"),

                ], order='sequence', limit=1)
                if not activity_arrival:

                    activity = self.env['travel.activity'].create({
                        'activity_name': f"Arrival at {city_night.city_id.name}",
                        'activity_city_id': city_night.city_id.id,
                        'activity_desc': f"Your journey in {city_night.city_id.name}.",
                        'category': [(6, 0, [leisure_category.id])]
                    })
                else:
                    activity = activity_arrival
            else:
                activity_leisure = self.env['travel.activity'].search([
                    ('activity_city_id', '=', city_night.city_id.id),
                    ('activity_name', '=', "Day at Leisure"),

                ], order='sequence', limit=1)
                if not activity_leisure:

                    activity_leisure = self.env['travel.activity'].create({
                        'activity_name': "Day at Leisure",
                        'activity_city_id': city_night.city_id.id,
                        'activity_desc': f"Explore {city_night.city_id.name} on your own.",
                        'category': [(6, 0, [leisure_category.id])]
                    })

                activity = next(activity_cycle, False) or activity_leisure

            itinerary_date = itin_city_change_last_date + timedelta(days=i)
            itinerary = self.env['travel.itinerary.days'].create({
                'package_id': package.id,
                'days': itinerary_date,
                'citynight_id': city_night.id,
            })

            last_seq = self.env['travel.itinerary.activity'].search([
                ('itinerary_id.package_id', '=', package.id)
            ], order='sequence desc', limit=1).sequence or 0

            self.env['travel.itinerary.activity'].create({
                'itinerary_id': itinerary.id,
                'category': [(6, 0, [leisure_category.id])],
                'duration': activity.duration,
                'age_limit': activity.age_limit,
                'activity_name': activity.activity_name,
                'sequence': last_seq + 1,
                'activity_desc': activity.activity_desc,
                'activity_city_id': activity.activity_city_id.id
            })

            itin_city_change_last_date = itinerary.days

    def add_road_transport(self, instance, destination,):
        print('============>destination', destination,
              int(instance.number_of_adults))
        rto = self.env['travel.road.transport.option'].search([
            ('seats', '>=', int(instance.number_of_adults))
        ],  order='seats asc', limit=1)
        print('rto', rto)
        if rto:
            val = {
                'package_id': instance.id,
                'road_transport_id': rto.id,
                'destination_id': destination,
                'pickup_from_id': instance.leaving_from_id.id
            }
            self.env['travel.road.transport.details'].create(val)
        else:
            val = {
                'package_id': instance.id,

                'destination_id': destination,
                'pickup_from_id': instance.leaving_from_id.id
            }
            self.env['travel.road.transport.details'].create(val)

    def action_save(self):
        vals = {
            'package_name': self.package_name or 'New Package',
            'customer_id': self.customer_id.id,
            'customer_name': self.customer_name,
            'leaving_from_id': self.leaving_from_id.id,
            'leaving_from': self.leaving_from,
            'nationality_id': self.nationality_id.id,
            'nationality': self.nationality,
            'leaving_on': self.leaving_on,
            'number_of_rooms': self.number_of_rooms,
            'number_of_adults': self.number_of_adults,
            'number_of_children': self.number_of_children,
            'company_id': self.company_id.id,
            'is_final': self.is_final,
            'interests': self.interests,
            'who_is_travelling': self.who_is_travelling,
            'pregnant_women': self.pregnant_women,
            'elderly_people': self.elderly_people,
            'with_walking_difficulty': self.with_walking_difficulty,
            'teenager': self.teenager,
            'women_only': self.women_only,
            'men_only': self.men_only,
            'room_type': self.room_type,
            'star_rating': self.star_rating,
            'add_transfers': self.add_transfers,
            'add_tours_and_travels': self.add_tours_and_travels,
            'status': self.status,
            'citynight_ids': [(6, 0, self.citynight_ids.ids)],
        }

        if not self.exists():
            self.create(vals)
        else:
            self.write(vals)



class CityNight(models.Model):
    _name = 'travel.city.night'
    _description = 'City Night'

    city_id = fields.Many2one('city.model', string="City" ,required=True)
    itinerary_id = fields.Many2one(
        'travel.itinerary', string="Package", required=True, ondelete='cascade')
    sequence = fields.Integer(string="Sequence", default=1)
    nights = fields.Integer(string="Nights", required=True)

    _order = 'sequence'

    @api.model
    def create(self, vals):
        # Auto-set sequence if not provided
        if 'sequence' not in vals or vals['sequence'] == 0:
            vals['sequence'] = self.search_count([]) + 1
        return super(CityNight, self).create(vals)

    def write(self, vals):
        if 'sequence' in vals:
            # Ensure sequence is recalculated when dragging and dropping
            sequence = vals.get('sequence')
            existing = self.search([('sequence', '=', sequence)])
            if existing:
                for record in existing:
                    record.sequence += 1
        return super(CityNight, self).write(vals)


class HotelDetails(models.Model):
    _name = 'travel.hotel.details'
    _description = 'Hotel Details'

    package_id = fields.Many2one('travel.itinerary', string='Itinerary')
    hotel_id = fields.Many2one('hotel', string='Hotel')
    citynight_id = fields.Many2one('travel.city.night', string='City Night')
    check_in_date = fields.Date(string='Check-In Date')
    check_out_date = fields.Date(string='Check-Out Date')
    room_id = fields.Many2one('room.type', string='Room')
    meal_plans = fields.Char(string='Meal Plans')
    category= fields.Many2one('room.category', string='Room category')
    # facilities = fields.Many2many('facility', string='Facilities')  # Assume there's a model 'facility'
    number_of_rooms = fields.Integer(string='Number of Rooms')
    total_price = fields.Float(
        string='Total Price', digits=(10, 2), default=0.0)
    additional_requests = fields.Text(string='Additional Requests')
    
    

class Activity(models.Model):
    _name = 'travel.activity'
    _description = 'Activity'

    # Assume there's a model 'activity.category'
    category = fields.Many2many('travel.activity.category', string='Category')
    duration = fields.Char(string='Duration')
    age_limit = fields.Char(string='Age Limit')
    activity_name = fields.Char(string='Activity Name')
    entry_fee = fields.Char(string='Entry Fee')
    sequence = fields.Integer(string='Sequence')
    activity_img = fields.Image(string='Activity Image')
    activity_desc = fields.Text(string='Activity Description')
    activity_city_id = fields.Many2one('city.model', string='Activity City')


class ItineraryDays(models.Model):
    _name = 'travel.itinerary.days'
    _description = 'Itinerary Days'

    package_id = fields.Many2one('travel.itinerary', string='Package')
    citynight_id = fields.Many2one('travel.city.night', string='City Night')
    days = fields.Date(string='Days')
    activity_input = fields.Text(string='Activity Input')

    def _latest_by_days(self):
        return self.search([], order='days desc', limit=1)


class ItineraryActivity(models.Model):
    _name = 'travel.itinerary.activity'
    _description = 'Itinerary Activity'

    itinerary_id = fields.Many2one('travel.itinerary.days', string='Itinerary')
    # Assume there's a model 'activity.category'
    category = fields.Many2many('travel.activity.category', string='Category')
    duration = fields.Char(string='Duration')
    age_limit = fields.Char(string='Age Limit')
    activity_name = fields.Char(string='Activity Name')
    sequence = fields.Integer(string='Sequence')
    activity_img = fields.Image(string='Activity Image')
    activity_desc = fields.Text(string='Activity Description')
    activity_city_id = fields.Many2one('city.model', string='Activity City')


class ActivityCategory(models.Model):
    _name = 'travel.activity.category'
    _description = 'Activity Category'

    name = fields.Char(string='Category Name', required=True)
    description = fields.Text(string='Description')


class RoadTransportOption(models.Model):
    _name = 'travel.road.transport.option'
    _description = 'Road Transport Option'

    vehicle_type = fields.Char(string='Vehicle Type', required=True)
    seats = fields.Integer(string='Seats', required=True)
    cost = fields.Float(string='Cost', digits=(10, 2), required=False)


class TransportDetails(models.Model):
    _name = 'travel.road.transport.details'
    _description = 'Travel Details'

    package_id = fields.Many2one(
        'travel.itinerary', string='Package', ondelete='cascade', required=False)
    road_transport_id = fields.Many2one(
        'travel.road.transport.option', string='Road Transport', ondelete='cascade',)
    pnr = fields.Char(string='PNR', required=False)
    destination_id = fields.Many2one(
        'city.model', string='Destination', ondelete='cascade', required=False)
    pickup_from_id = fields.Many2one(
        'city.model', string='Pickup From', ondelete='cascade', required=False)
