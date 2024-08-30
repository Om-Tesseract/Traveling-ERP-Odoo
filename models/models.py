# -*- coding: utf-8 -*-

from odoo import models, fields, api



class Country(models.Model):
    _name = 'country.model'
    _description = 'Country'

    name = fields.Char(string="Name", required=True, )
    iso3 = fields.Char(string="ISO3", size=30)
    iso2 = fields.Char(string="ISO2", size=30)
    numeric_code = fields.Char(string="Numeric Code", size=20)
    phone_code = fields.Char(string="Phone Code", size=20)
    currency = fields.Char(string="Currency", size=50)
    currency_name = fields.Char(string="Currency Name", size=50)
    currency_symbol = fields.Char(string="Currency Symbol", size=50)
    region = fields.Char(string="Region", size=50)
    nationality = fields.Char(string="Nationality", size=50)
    country_states_set = fields.One2many('state.model', 'country', string="States")
    country_city_set = fields.One2many('city.model', 'country', string="Cities")

    def name_get(self):
        return [(record.id, record.name) for record in self]



class States(models.Model):
    _name = 'state.model'
    _description = 'State'

    name = fields.Char(string="Name", required=True, size=60)
    country = fields.Many2one('country.model', string="Country", ondelete='cascade', required=True)
    state_code = fields.Char(string="State Code", size=20)

    state_city_set = fields.One2many('city.model', 'state', string="Cities")

    # def name_get(self):
    #     return [(record.id, f"{record.name}") for record in self]

class Cities(models.Model):
    _name = 'city.model'
    _description = 'City'

    name = fields.Char(string="Name", required=True, size=60)
    state = fields.Many2one('state.model', string="State", ondelete='cascade', required=True)
    country = fields.Many2one('country.model', string="Country", ondelete='cascade', required=True)
    img = fields.Image(string="Image", attachment=True)


    # def name_get(self):
    #     return [(record.id, f"{record.name} {record.state.name}") for record in self]