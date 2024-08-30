from odoo import models, fields

class Customer(models.Model):
    _name = 'travel.customers'
    _description = 'Customer'

    company_id = fields.Many2one('res.company', string="Company")
    name = fields.Char(string="Name", required=True)
    address = fields.Char(string="Address", required=False)
    mobile_number = fields.Char(string="Mobile Number", required=True)
    country_id = fields.Many2one('country.model', string="Country")
    state_id = fields.Many2one('state.model', string="State")
    city_id = fields.Many2one('city.model', string="City")
    email = fields.Char(string="Email")
