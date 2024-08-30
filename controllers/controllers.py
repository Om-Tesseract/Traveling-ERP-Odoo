from odoo import http
from odoo.http import request
import json
import base64
from datetime import datetime

class TravelsErp(http.Controller):

    @http.route('/travels_erp/get_itinerary', auth='public', type='json', methods=['POST'], csrf=False)
    def get_itinerary(self, **kwargs):
        itinerary_id = kwargs.get('itinerary_id')
        if itinerary_id:
            itinerary = request.env['travel.itinerary'].sudo().browse(int(itinerary_id))
            if itinerary.exists():
                transport_details = request.env['travel.road.transport.details'].sudo().search([('package_id', '=', itinerary.id)])
                total_nights = sum(request.env['travel.city.night'].sudo().search([('itinerary_id', '=', itinerary.id)]).mapped('nights'))

                # Collect road transport details
                transport_data = [{
                    'road_transport_name': transport.road_transport_id.vehicle_type if transport.road_transport_id else '',
                    'road_transport_id': transport.road_transport_id.id if transport.road_transport_id else '',
                    'pnr': transport.pnr,
                    'id':transport.id,
                    'destination': transport.destination_id.name if transport.destination_id else '',
                    'destination_id': transport.destination_id.id if transport.destination_id else '',
                    'pickup_from': transport.pickup_from_id.name if transport.pickup_from_id else '',
                    'pickup_from_id': transport.pickup_from_id.id if transport.pickup_from_id else '',
                } for transport in transport_details]

                itinerary_data = {
                    'id': itinerary.id,
                    'package_name': itinerary.package_name,
                    'customer_name': itinerary.customer_name,
                    'leaving_from': itinerary.leaving_from,
                    'leaving_from_id': itinerary.leaving_from_id.id,
                    'nationality': itinerary.nationality,
                    'nationality_id': itinerary.nationality_id.id,
                        'total_nights': total_nights,
                    'customer_id': itinerary.customer_id.id,
                    'customer_ph_no': itinerary.customer_id.mobile_number,
                    'customer_email': itinerary.customer_id.email,
                    'leaving_on': itinerary.leaving_on.strftime('%Y-%m-%d') if isinstance(itinerary.leaving_on, datetime) else itinerary.leaving_on,
                    'number_of_rooms': itinerary.number_of_rooms,
                    'number_of_adults': itinerary.number_of_adults,
                    'number_of_children': itinerary.number_of_children,
                    'interests': itinerary.interests,
                    'who_is_travelling': itinerary.who_is_travelling,
                    'pregnant_women':itinerary.pregnant_women,
                    'elderly_people':itinerary.elderly_people,
                    'with_walking_difficulty':itinerary.with_walking_difficulty,
                    'teenager':itinerary.teenager,
                    'women_only':itinerary.women_only,
                    'men_only':itinerary.men_only,
                      'transport_details': transport_data,
                    'room_type': itinerary.room_type,
                    'star_rating': itinerary.star_rating,
                    'add_transfers': itinerary.add_transfers,
                    'add_tours_and_travels': itinerary.add_tours_and_travels,
                    'status': itinerary.status,
                    'city_nights': [{
                        'city_name': night.city_id.name,
                        'nights': night.nights,
                        'id': night.id,
                        'city_id': night.city_id.id,
                        'img': night.city_id.img,
                        "country":night.city_id.country.name,
                        'state': night.city_id.state.name,
                        'sequence': night.sequence,
                        'itinerary':[
                            {
                                'id':itinerary.id,
                               'days': itinerary.days.strftime('%d %b %Y') if itinerary.days else '',
                                'activity_input':itinerary.activity_input,
                                'activity':[
                                    {       'id':activity.id,
                                            'duration':activity.duration,
                                            'age_limit':activity.age_limit,
                                            'activity_name':activity.activity_name,
                                           'sequence':activity.sequence,
                                           'activity_img':activity.activity_img,
                                           'activity_desc':activity.activity_desc,
                                           'activity_city_id':activity.activity_city_id,
                                             'categories': [category.name for category in activity.category],
                                    }
                                    for activity in request.env['travel.itinerary.activity'].search([('itinerary_id', '=', itinerary.id)])
                                ] 
                            }
                            for itinerary in request.env['travel.itinerary.days'].search([('citynight_id', '=', night.id)])],
                        'hotels': [{
                            'id': hotel.id,
                            'hotel_name': hotel.hotel_id.name,
                            'check_in_date': hotel.check_in_date.strftime('%d %b %Y') if hotel.check_in_date else '',
                            'check_out_date': hotel.check_out_date.strftime('%d %b %Y') if hotel.check_out_date else '',
                            'hotel_id':hotel.hotel_id.id,
                           
                           
                            'room_id': hotel.room_id.id,
                            'room_name': hotel.room_id.rnm,
                            'meal_plans': hotel.meal_plans,
                            'star_rating':hotel.hotel_id.star_rating,
                            'rate':hotel.hotel_id.rate,
                            'desc':hotel.hotel_id.desc,
                            'address':hotel.hotel_id.address,
                            'area':hotel.hotel_id.area,
                            'review_count':hotel.hotel_id.review_count,
                            'star_icon':[i for i in range(1,hotel.hotel_id.star_rating)],
                            'hotel_img':hotel.hotel_id.img,
                            # 'facilities': [facility.name for facility in hotel.facilities],
                            'number_of_rooms': hotel.number_of_rooms,
                            'total_price': hotel.total_price,
                            'additional_requests': hotel.additional_requests,
                        } for hotel in request.env['travel.hotel.details'].search([('citynight_id', '=', night.id)])]
                    } for night in itinerary.citynight_ids]
                }
                return {'success': True, 'itinerary': itinerary_data}
        return {'success': False, 'message': 'Itinerary not found'}
    
    @http.route('/travel/hotel/details/get_hotel_details', type='json', auth='user')
    def get_hotel_details(self, hotel_id):
        # Get hotel details by ID
        hotel = request.env['travel.hotel.details'].sudo().browse(hotel_id)
        
        # Ensure the hotel exists
        if not hotel.exists():
            return {'error': 'Hotel not found'}

        # Prepare the data to return
        hotel_data = {
            'id': hotel.id,
            'name': hotel.name,
            'room_categories': [
                {
                    'id': category.id,
                    'name': category.name,
                    'rooms': [
                        {
                            'id': room.id,
                            'rnm': room.rnm
                        } for room in category.rooms
                    ]
                } for category in hotel.room_categories
            ],
            'meal_plan': hotel.meal_plan,
            'additional_request': hotel.additional_request,
        }

        return {'hotel_data': hotel_data}
    @http.route('/travels_erp/hotel', auth='public', type='json', methods=['POST'], csrf=False)
    def get_hotels(self, *args, **kwargs):
        hotel_id = kwargs.get('hotel_id', None)
        
        hotels = request.env['hotel'].search([('id', '=',hotel_id)])
        # Prepare a list to store the data
        hotel_data = {}

        for hotel in hotels:
            # Extract hotel details
            hotel_info = {
                    'id':hotel.id,

                'name': hotel.name,
                'address': hotel.address,
                'area': hotel.area,
                'link': hotel.link,
                'city': hotel.city_id.name,
                'star_rating': hotel.star_rating,
                'rate': hotel.rate,
                'review_count': hotel.review_count,
                'desc': hotel.desc,
                'contact_info': hotel.contact_info,
                'image_url': hotel.image_url,
                'img': hotel.img if hotel.img else None,
                'ln': hotel.ln,
                'lat': hotel.lat,
                'amenities': hotel.amenities,
                'cleanliness_rate': hotel.cleanliness_rate,
                'service_rate': hotel.service_rate,
                'star_icon':[i for i in range(1,hotel.star_rating)],
                'comfort_rate': hotel.comfort_rate,
                'amenities_rate': hotel.amenities_rate,
                'hotel_imgs': [
                    {'image': img.image if img.image else None, 'img_url': img.img_url,'id':img.id}
                    for img in hotel.hotel_imgs
                ],
                'room_categories': []
            }

            # Extract room categories
            for category in hotel.room_category:
                category_info = {
                    'id':category.id,
                    'name': category.name,
                    'desc': category.desc,
                    'view_name': category.view_name,
                    'room_size': category.room_size,
                    'bed_type': category.bed_type,
                    'room_imgs': [
                        {'image': img if img.img else None, 'img_url': img.img_url}
                        for img in category.room_img
                    ],
                    'rooms': []
                }

                # Extract room types
                for room in category.rooms:
                    room_info = {
                        'id': room.id,
                        'rnm': room.rnm,
                        'cur': room.cur,
                        'meal_plan': room.meal_plan,
                        'price': room.price,
                        'availability': room.availability,
                        'amenity': room.amenity,
                        'key': room.key,
                        'meal_includes': room.meal_includes,
                    }
                    category_info['rooms'].append(room_info)

                hotel_info['room_categories'].append(category_info)

            hotel_data=hotel_info

        return hotel_data
    @http.route('/travels_erp/all_hotels', auth='public', type='json', methods=['POST'], csrf=False)
    def get_all_hotels(self,*args, **kwargs):
        city_id = kwargs.get('city_id')
        hotel_data = []

        if city_id:
           
            hotels = request.env['hotel'].search([('city_id','=',city_id)])
            for hotel in hotels:
                # Extract hotel details
                room_name=None
                meal_plan=None
                meal_includes=None
                if hotel.room_category:
                  # Access the first room category
                  room_category = hotel.room_category[0]
                  if room_category.rooms:
                      # Access the first room within the room category
                      room = room_category.rooms[0]
                      room_name = room.rnm
                      meal_plan = room.meal_plan
                      meal_includes = room.meal_includes
                hotel_info = {
                    'id':hotel.id,
                    'name': hotel.name,
                    'address': hotel.address,
                    'area': hotel.area,
                    'link': hotel.link,
                    'city': hotel.city_id.name,
                    'star_rating': hotel.star_rating,
                    'rate': hotel.rate,
                    'review_count': hotel.review_count,
                    'desc': hotel.desc,
                    'star_icon':[i for i in range(1,hotel.star_rating)],

                    'contact_info': hotel.contact_info,
                    'image_url': hotel.image_url,
                    'img': hotel.img if hotel.img else None,
                    'ln': hotel.ln,
                    'lat': hotel.lat,
                    'amenities': hotel.amenities,
                    'cleanliness_rate': hotel.cleanliness_rate,
                    'service_rate': hotel.service_rate,
                    'comfort_rate': hotel.comfort_rate,
                    'amenities_rate': hotel.amenities_rate,
                      'room_name': room_name,
                'meal_plan': meal_plan,
                'meal_includes': meal_includes
                    }
                hotel_data.append(hotel_info)
        return hotel_data
