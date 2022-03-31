import os
import re
import glob
import json
from xlsxwriter import Workbook
from tempfile import TemporaryDirectory
import requests


def detect_text(uri):
    from google.cloud import vision
    import io
    client = vision.ImageAnnotatorClient()
    print(f"OCR for {uri} is in progress..")

    # download to path
    content = None
    with TemporaryDirectory() as dir_path:
        path = os.path.join(dir_path, "debug.png")
        with open(path, "wb") as ref:
            ref.write(requests.get(uri).content)
        print(f"Save at {path}")

        # [START vision_python_migration_text_detection]
        with io.open(path, "rb") as image_file:
            content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if response.error.message:
        print(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(
                response.error.message))
        return -1, uri, []

    number_list = ["".join(re.findall(r"\d+", text.description)) for text in texts]
    number_list = [a for a in number_list if len(a) > 0]
    return 0, uri, list(set(number_list)) 


def main():
    image_urls = []
    for json_path in glob.glob("./crawler/*.json"):
        with open(json_path) as ref:
            data = json.load(ref)
            image_urls.extend(data)
            print(f"extend {len(data)} data")
    
    print(f"total data: {len(image_urls)} images")
   
 
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for idx, image_url in enumerate(image_urls):
            futures.append(executor.submit(detect_text, image_url))

        for idx, future in enumerate(concurrent.futures.as_completed(futures)):
            status, image_url, number_list = future.result()
            retry_count = 0
            while status == -1 and retry_count < 5:
                print(f"OCR for {image_url} failed! Retry..")
                status, image_url, number_list = detect_text(image_url)
                retry_count += 1


            file_name = os.path.splitext(os.path.basename(image_url))[0]
            with open(f"data/{file_name}.json", "w") as ref:
                json.dump({
                    "status": status,
                    "image_url": image_url,
                    "number_list": number_list
                }, ref)

    # create xlsx file
    wb = Workbook("data.xlsx")
    ws = wb.add_worksheet()
    ws.write(0, 0, "Image URL")
    ws.write(0, 1, "Bib Number")
    for idx, json_path in enumerate(glob.glob("data/*.json")):
        data = None
        with open(json_path) as ref:
            data = json.load(ref)
        status = data["status"]
        image_url = data["image_url"]
        number_list = data["number_list"]
        number_str = ",".join([a for a in number_list]) 

        ws.write_url(idx+1, 0, image_url)
        ws.write(idx+1, 1, number_str)
    
    wb.close()

if __name__ == "__main__":
    main()
