# pip install pdf2docx -q
# !pip install python-docx -q

import os
import docx
import argparse

from glob import glob
from pdf2docx import Converter

def convert_pdf_to_docx(pdf_path, docx_path=None):
    """
    Converts a specified PDF file to a DOCX file.

    Args:
        pdf_path (str): The full path to the input PDF file.
        docx_path (str, optional): The full path for the output DOCX file.
                                   If None, it saves the DOCX in the same
                                   directory as the PDF with the same name
                                   but a .docx extension. Defaults to None.

    Returns:
        bool: True if conversion was successful, False otherwise.
    """
    # Validate input PDF path
    if not os.path.exists(pdf_path):
        print(f"Error: Input PDF file not found at '{pdf_path}'")
        return False
    if not pdf_path.lower().endswith(".pdf"):
        print(f"Warning: Input file '{os.path.basename(pdf_path)}' might not be a PDF.")
        # Continue anyway, let pdf2docx handle potential errors

    # Determine output DOCX path if not provided
    if docx_path is None:
        base_name = os.path.splitext(pdf_path)[0]
        docx_path = base_name + ".docx"
    elif not docx_path.lower().endswith(".docx"):
         print(f"Warning: Specified output path '{docx_path}' doesn't end with .docx. Appending it.")
         docx_path += ".docx"


    print(f"Starting conversion: '{os.path.basename(pdf_path)}' -> '{os.path.basename(docx_path)}'")

    try:
        # Initialize the Converter object
        cv = Converter(pdf_path)

        # Perform the conversion
        # You can specify page ranges: cv.convert(docx_path, start=0, end=1) for first 2 pages
        cv.convert(docx_path, start=0, end=None) # end=None converts all pages

        # Close the converter object
        cv.close()

        if os.path.exists(docx_path):
             print(f"Successfully converted PDF to: '{docx_path}'")
             return True
        else:
             print(f"Conversion process completed, but output file not found at '{docx_path}'. Check permissions or disk space.")
             return False

    except Exception as e:
        print(f"\nAn error occurred during conversion:")
        print(f"------------------------------------")
        print(e)
        print(f"------------------------------------")
        print("Conversion failed.")
        # Clean up partially created file if it exists
        if os.path.exists(docx_path):
            try:
                # os.remove(docx_path) # Optional: uncomment to delete partial files on error
                print(f"Note: A potentially incomplete output file might exist at '{docx_path}'")
            except OSError as oe:
                 print(f"Could not access potentially incomplete output file: {oe}")
        return False
