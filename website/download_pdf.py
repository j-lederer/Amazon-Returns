from fpdf import FPDF
from .models import Tracking_ids
# from flask import Flask, render_template, request, redirect, url_for
# from flask_sqlalchemy import SQLAlchemy
# from flask import Blueprint, render_template, request, flash, jsonify
# from flask_login import login_required, current_user
# from . import db
from.database import load_queue_from_db

# tracking_ids = Tracking_ids.query.filter_by(user_id=current_user.id).all()


def download_queue_data(user_id):
    tracking_ids = load_queue_from_db(user_id)
    print("TRACKING_IDS_QUEUE")
    print(tracking_ids)
    pdf = PDF()
    pdf.generate_pdf(tracking_ids)


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

    def table(self, tracking_ids):
        # Colors, line width and bold font
        self.set_font('Arial', 'B', 16)
        self.set_fill_color(255, 0, 0)
        self.set_text_color(255)
        self.set_draw_color(128, 0, 0)
        self.set_line_width(.3)
        self.set_font('', 'B')
        # Header
        self.cell(25, 10, 'Tracking', 1, 0, 'C', 1)
        self.cell(10, 10, 'SKU', 1, 0, 'C', 1)
        self.cell(75, 10, 'Return Quantity', 1, 0, 'C', 1)
        self.cell(40, 10, 'Phone', 1, 0, 'C', 1)
        self.cell(45, 10, 'Email', 1, 0, 'C', 1)
        self.ln()
        # Data
        self.set_text_color(0)
        self.set_font('Arial', '', 8)
        for tracking_id in tracking_ids:
            self.cell(25, 10, tracking_id['tracking'], 1, 0, 'C')
            self.cell(10, 10, str(tracking_id['SKU']), 1, 0, 'C')
            self.cell(75, 10, tracking_id['return_quantity'], 1, 0, 'C')
            self.cell(40, 10, 'test', 1, 0, 'C')
            self.cell(45, 10, 'test@gmail.com', 1, 1, 'C')
        # Closing line
        self.cell(0, 10, '', 0, 1)

    def generate_pdf(self, tracking_ids):
        self.table(tracking_ids)
        self.output('website/static/files/queue.pdf', 'F')