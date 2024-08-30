from odoo import models, fields, api

from odoo import api, fields, models

class InvoiceMaster(models.Model):
    _name = 'travels.invoice.master'
    _description = 'Invoice Master'
    _rec_name="invoice_no"
    invoice_no = fields.Char(string="Invoice No", required=True, copy=False, readonly=True, index=True, default=lambda self: ('New'))
    invoice_type = fields.Char(string="Invoice Type", required=True)
    company_id = fields.Many2one('res.company', string="Company", ondelete='cascade', default=lambda self: self.env.company.id)
    package_id = fields.Many2one('travel.itinerary', string="Package", ondelete='cascade', required=True)
    customer_name= fields.Char(string="Customer")
    invoice_date = fields.Date(string="Invoice Date", required=True)
    gst = fields.Float(string="GST(%)", digits=(10, 2), default=0.0)
    tax_amt = fields.Float(string="Tax Amount", digits=(10, 2), compute="_compute_tax_amt", store=True)
    discount_amt = fields.Float(string="Discount Amount", digits=(10, 2), default=0.0)
    gross_amt = fields.Float(string="Gross Amount", digits=(10, 2), required=True)
    net_amt = fields.Float(string="Net Amount", digits=(10, 2), compute="_compute_net_amt", store=True)
    notes = fields.Text(string="Notes")
    narration = fields.Text(string="Narration")

    @api.model
    def create(self, vals):
        if vals.get('invoice_no', ('New')) == ('New'):
            vals['invoice_no'] = self.env['ir.sequence'].next_by_code('travels.invoice.master') or ('New')
        return super(InvoiceMaster, self).create(vals)

    @api.depends('gross_amt', 'gst')
    def _compute_tax_amt(self):
        """Compute the tax amount based on the GST percentage and gross amount."""
        for record in self:
            record.tax_amt = (record.gross_amt * record.gst) / 100 if record.gst else 0.0

    @api.depends('gross_amt', 'tax_amt', 'discount_amt')
    def _compute_net_amt(self):
        """Compute the net amount after applying the tax and discount."""
        for record in self:
            record.net_amt = record.gross_amt + record.tax_amt - record.discount_amt
    @api.onchange('package_id')
    def _onchange_package_id(self):
        """Set customer_name based on the selected package's customer."""
        if self.package_id and self.package_id.customer_id:
            self.customer_name = self.package_id.customer_name
        else:
            self.customer_name = False  # Clear the field if no package or customer is selected

    def print_invoice(self):
        return self.env.ref('travels_erp.action_travel_erp_report_invoice').report_action(self)



class ExpenseDetail(models.Model):
    _name = 'travels.expense.detail'
    _description = 'Expense Detail'
    _rec_name="expense_no"
    expense_no = fields.Char(string="Expense No", required=True, copy=False, readonly=True, index=True, default=lambda self: ('New'))
    package_id = fields.Many2one('travel.itinerary', string='Package', required=True, ondelete='cascade')
    category = fields.Char(string='Category', required=True)
    date = fields.Date(string='Date', required=True)
    tax = fields.Float(string='Tax')
    company_id = fields.Many2one('res.company', string='Company',  ondelete='cascade', default=lambda self: self.env.company.id)
    purposes = fields.Text(string='Purposes')
    amount = fields.Float(string='Amount', required=True, digits=(20, 2))
    total_amount = fields.Float(string='Total Amount', required=True, digits=(20, 2))

    @api.onchange('amount', 'tax')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = record.amount + record.tax if record.amount and record.tax else 0.0
    @api.model
    def create(self, vals):
        if vals.get('expense_no', ('New')) == ('New'):
            vals['expense_no'] = self.env['ir.sequence'].next_by_code('travels.expense.detail') or ('New')
        return super(ExpenseDetail, self).create(vals)
