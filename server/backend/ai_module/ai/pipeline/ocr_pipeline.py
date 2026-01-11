# ai/pipeline/ocr_pipeline.py

from ai.ocr.pdf_to_image import pdf_to_images
from ai.ocr.ocr_clients import process_multiple_images


def run_ocr_pipeline(pdf_path, ocr_api_url, ocr_secret_key):
    image_paths = pdf_to_images(pdf_path)
    ocr_result = process_multiple_images(
        image_paths=image_paths,
        api_url=ocr_api_url,
        secret_key=ocr_secret_key
    )
    return ocr_result
