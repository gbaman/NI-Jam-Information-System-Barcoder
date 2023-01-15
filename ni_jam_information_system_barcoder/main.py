import json

import requests
from flask import Flask, render_template, request

from secrets.config import nijis_server_base_url, nijis_api_key, organisation_name, organisation_email, use_29mm_continuous_reel

import barcode
from PIL import Image, ImageDraw, ImageFont

import brother_ql
from brother_ql.raster import BrotherQLRaster
from brother_ql.backends.helpers import send

from barcode import UPCA
from barcode.writer import ImageWriter

PRINTER_IDENTIFIER = 'usb://0x04f9:0x2028'

app = Flask(__name__)

equipment_url = nijis_server_base_url + "/api/equipment/" + str(nijis_api_key)
equipment_groups_url = nijis_server_base_url + "/api/equipment_groups/" + str(nijis_api_key)
add_equipment_entries_url = nijis_server_base_url + "/api/add_equipment_entries/" + str(nijis_api_key)
add_equipment_url = nijis_server_base_url + "/api/add_equipment/"


@app.route("/")
def home():
    equipment_raw = requests.get(equipment_url)
    if equipment_raw.ok:
        equipment = equipment_raw.json()
        equipment_groups_raw = requests.get(equipment_groups_url)
        equipment_groups = equipment_groups_raw.json()
        return render_template("index.html", equipment=equipment, equipment_groups=equipment_groups,
                           equipment_json=json.dumps(equipment))
    else:
        return equipment_raw.text


@app.route("/print_labels", methods=['POST'])
def print_labels():
    equipment_id = int(request.form['equipment_id'])
    quantity = int(request.form['quantity'])
    equipment_name = request.form['equipment_name']
    label_data = requests.post(add_equipment_entries_url, data={"equipment_id": equipment_id, "quantity": quantity}).json()
    for label in label_data:
        create_label_image(label[0], label[1], equipment_name)
    return ""


@app.route("/reprint_label", methods=["POST"])
def reprint_label():
    entry_id = int(request.form['entry_id'])
    entry_code = (request.form['entry_code'])
    equipment_name = request.form['equipment_name']
    create_label_image(entry_id, entry_code, equipment_name)
    return ""


@app.route("/add_equipment", methods=["POST"])
def add_equipment():
    equipment_name = request.form['equipment_name']
    equipment_code = request.form['equipment_code']
    equipment_group_id = request.form['equipment_group_id']
    if requests.post(add_equipment_url,
                     data={"token": nijis_api_key, "equipment_name": equipment_name, "equipment_code": equipment_code,
                           "equipment_group_id": equipment_group_id}):
        return ""


def generate_barcode_2(data):
    b = barcode.get('upc', str(data).zfill(12), writer=ImageWriter())
    b = UPCA(str(data).zfill(12), writer=ImageWriter())
    return b.render(writer_options={"module_width":0.5})


def create_label_image(equipment_entry_id, equipment_entry_number, equipment_name):
    barcode_image = generate_barcode_2(equipment_entry_id)

    name_font = ImageFont.truetype("arial.ttf", 30)
    jam_font = ImageFont.truetype("arial.ttf", 27)
    qr_font = ImageFont.truetype("arial.ttf", 22)
    if use_29mm_continuous_reel:
        img = Image.new('L', (500, 306), color='white')
    else:
        img = Image.new('L', (991, 306), color='white')

    d = ImageDraw.Draw(img)
    img.paste(barcode_image.resize((580, 195), Image.ANTIALIAS), (-40, 0))
    w, h  = d.textsize(equipment_name, font=name_font)
    d.text((190, 182), equipment_entry_number, fill="black", font=name_font)
    d.text(((500-w)/2, 212), equipment_name, fill="black", font=name_font)
    d.text((86, 245), organisation_name, fill="black", font=qr_font)
    d.text((126, 270), organisation_email, fill="black", font=qr_font)

    #img.save('generated_badge.png')
    #time.sleep(0.1)
    #send_to_printer_file('generated_badge.png')
    send_to_printer_pil(img)


def send_to_printer_pil(pil_obj):
    if use_29mm_continuous_reel:
        label_size = '29'
    else:
        label_size = '29x90'
    printer = BrotherQLRaster('QL-570')
    print_data = brother_ql.brother_ql_create.convert(printer, [pil_obj], label_size, dither=False, rotate="90", hq=True)
    send(print_data, PRINTER_IDENTIFIER)

if __name__ == '__main__':
    app.run(port=5001)