
"""
This script is used to merge two files, one with descriptions and the other with transcriptions.
The script reads the files, merges the texts, and saves the output to a PDF file.
The script uses the fpdf library to create the PDF file.    
The script uses the argparse library to parse command line arguments.
The script uses the re library to parse the input files.
The script uses the googletrans library to translate text.
The script uses the reportlab library to create the PDF file.
The script defines functions to parse the description and transcription files.
Usage:
    python concat.py --description <description_file> --transcription <transcription_file> --output <output_file> --translate <True/False> --language <language> --header <header_file>
Author: Pavis
Date: 25/03/2024
"""
import re
from fpdf import FPDF
import argparse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from googletrans import Translator, LANGUAGES

def parse_descriptions(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
        chunks = re.findall(
            r'##\[(\d+ - \d+)\]:\n(.+?)(?=\n##\[|\Z)', content, re.DOTALL)

    # convert all timespans to a tuple of integers each divided by 10000
    chunks = [(tuple(map(int, timespan.split(' - '))), text)
              for timespan, text in chunks]
    
    #  divide all timespans by 10000 leavin it as numbers
    chunks = [((start // 10000, end // 10000), text) for (start, end), text in chunks]

    # convert all timespans to a string multiplied by 10000
    chunks = [(f"{start * 10000} - {end * 10000}", text)
              for (start, end), text in chunks]

    #print(chunks[2]) 
    return {timespan: text.strip() for timespan, text in chunks}


def parse_transcriptions(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

        chunks = re.findall(
            r'##\s*\[(\d+\s*-\s*\d+)\]:\s*(.+?)(?=\n##\[|\Z)', content, re.DOTALL)
        
    # convert all timespans to a tuple of integers each divided by 10000
    chunks = [(tuple(map(int, timespan.split(' - '))), text)
              for timespan, text in chunks]
    
    #  divide all timespans by 10000 leavin it as numbers
    chunks = [((start // 10000, end // 10000), text) for (start, end), text in chunks]

    # convert all timespans to a string multiplied by 10000
    chunks = [(f"{start * 10000} - {end * 10000}", text)
              for (start, end), text in chunks]
    
    #print(chunks[2])
    return {timespan: text.strip() for timespan, text in chunks}


def merge_texts(descriptions, transcriptions, google_translator, translate=False, language="en"):
    merged_text = ""
    for timespan in descriptions.keys():

        tran = transcriptions.get(timespan, "No transcription available")

        if tran == "No transcription available":
            continue

        desc = descriptions.get(timespan, "No description available")

        if translate:
            desc = google_translator.translate(desc, dest=language).text
            tran = google_translator.translate(tran, dest=language).text

        merged_text += f"##[{timespan}]:\nDescription:\n{desc}\n\nTranscription:\n{tran}\n\n"
    return merged_text


def save_to_pdf(text, output_filename, line_length=100):
    pdf = FPDF()
    pdf.add_page()

    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', '', 12)

    text_lines = text.split('\n')
    for line in text_lines:
        words = line.split(' ')
        current_line = ''
        for word in words:
            if len(current_line + word) <= line_length:
                current_line += word + ' '
            else:
                pdf.cell(0, 10, current_line, ln=True)
                current_line = word + ' '
        if current_line:
            pdf.cell(0, 10, current_line, ln=True)

    pdf.output(output_filename)


def save_to_pdf_reportlab(text, output_filename):
    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    c = canvas.Canvas(output_filename, pagesize=letter)
    c.setFont('Vera', 12)
    y_position = 750
    for line in text.split('\n'):
        c.drawString(72, y_position, line)
        y_position -= 12
        if y_position < 72:
            c.showPage()
            c.setFont('Vera', 12)
            y_position = 750
    c.save()


def save_to_txt(text, output_filename):
    with open(output_filename, 'w') as file:
        file.write(text)


def main():
    parser = argparse.ArgumentParser(
        description="Merge description and transcription files.")
    
    parser.add_argument("--description", type=str,
                        help="Path to the description file.")
    parser.add_argument("--transcription", type=str,
                        help="Path to the transcription file.")
    parser.add_argument("--output", type=str, default="merged_output.txt",
                        help="Path to the output PDF file.")
    parser.add_argument("--translate", type=bool, default=True,
                        help="Translate the output to English.")
    parser.add_argument("--language", type=str, default="en",
                        help="Language to translate to.")    
    parser.add_argument("--header", type=str,
                        help="Header to add to the output.")

    args = parser.parse_args()

    translate = False
    google_translator = None
    if args.translate:
        print("Translator service activate")
        google_translator = Translator()
        translate = True

    header = ""
    #open header file, same filename but txt extension
    with open(args.header, 'r', encoding='utf-8') as file:
        header = file.read()

    # translate the header
    if translate:
        header = google_translator.translate(header, dest=args.language).text

    header = header + "\nTime windows:\n"

    # parse the description and transcription files
    descriptions = parse_descriptions(args.description)

    # parse the transcription file
    transcriptions = parse_transcriptions(args.transcription)

    # merge the texts
    merged_text = merge_texts(
        descriptions, transcriptions, google_translator, translate, args.language)
    
    complete_text = header + merged_text

    # save the merged text to a file
    if args.output.endswith('.pdf'):
        save_to_pdf(complete_text, args.output)
    else:
        save_to_txt(complete_text, args.output)


if __name__ == "__main__":
    main()
