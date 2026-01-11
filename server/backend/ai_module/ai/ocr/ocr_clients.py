import time
import json
import requests


# ======================================================
# OCR API 호출
# ======================================================
def process_multiple_images(image_paths, api_url, secret_key):
    all_images = []

    headers = {"X-OCR-SECRET": secret_key}

    for idx, image_path in enumerate(image_paths):
        request_json = {
            "version": "V2",
            "requestId": str(time.time()),
            "timestamp": int(time.time() * 1000),
            "enableTableDetection": True,
            "images": [
                {
                    "format": "jpg",
                    "name": f"page_{idx+1}"
                }
            ]
        }

        with open(image_path, "rb") as f:
            response = requests.post(
                api_url,
                headers=headers,
                data={"message": json.dumps(request_json)},
                files={"file": f}
            )

        response.raise_for_status()
        result = response.json()
        all_images.extend(result.get("images", []))

    return {"images": all_images}
