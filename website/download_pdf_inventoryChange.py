from fpdf import FPDF
from flask import Response
from .models import Tracking_ids
# from flask import Flask, render_template, request, redirect, url_for
# from flask_sqlalchemy import SQLAlchemy
# from flask import Blueprint, render_template, request, flash, jsonify
# from flask_login import login_required, current_user
# from . import db
#from.database import load_queue_from_db
from .amazonAPI import produce_pdf

# tracking_ids = Tracking_ids.query.filter_by(user_id=current_user.id).all()


def download_queue_and_inventory_change_data(user_id, refresh_token):
    response = produce_pdf(user_id, refresh_token)
    Quantity_of_SKUS = response[0]
    queue_to_increase =response[1]
    final_inventory = response[2]
    pdf = PDF()
    return (pdf.generate_pdf( Quantity_of_SKUS, queue_to_increase, final_inventory))

class PDF(FPDF):
    def __init__(self):
        super().__init__(format='A4')
        self.alias_nb_pages()
        self.add_page()
        self.set_font('Arial', '', 12)
      
    def header(self):
        # Logo
        # self.image('app/static/images/logo.jpg', 180, 8, 12)
        self.set_font('Arial', 'B', 15)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(50, 10, 'Queue Demo', 1, 0, 'C')
        # Line break
        self.ln(20)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', '', 8)
        self.set_text_color(128)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

    def table(self, Quantity_of_SKUS, queue_to_increase, final_inventory):
        # Colors, line width and bold font
        self.set_font('Arial', 'B', 10)
        self.set_fill_color(255, 0, 0)
        self.set_text_color(255)
        self.set_draw_color(128, 0, 0)
        self.set_line_width(.3)
        self.set_font('', 'B')
        # Header
        self.cell(50, 10, 'SKU', 1, 0, 'C', 1)
        self.cell(40, 10, 'Original Inventory', 1, 0, 'C', 1)
        self.cell(40, 10, 'Inventory Change', 1, 0, 'C', 1)
        self.cell(40, 10, 'Final Inventory', 1, 0, 'C', 1)
        self.ln()
        # Data
        self.set_text_color(0)
        self.set_font('Arial', '', 8)
        for sku in queue_to_increase.keys():
            self.cell(50, 10, sku, 1, 0, 'C')
            self.cell(40, 10, Quantity_of_SKUS[sku], 1, 0, 'C')
            self.cell(40, 10, f' +{queue_to_increase[sku]}', 1, 0, 'C')
            self.cell(40, 10, str(final_inventory[sku]), 1, 1, 'C')
            
        # Closing line
        self.cell(0, 10, '', 0, 1)

    def generate_pdf(self, Quantity_of_SKUS, queue_to_increase, final_inventory):
        self.table(Quantity_of_SKUS, queue_to_increase,  final_inventory)
        return( Response(self.output(dest='S'), mimetype='application/pdf'))
        # self.output('website/static/files/InventoryUpdate.pdf', 'F')