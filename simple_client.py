# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 20:56:24 2020

@author: M
"""

# Core
import logging
import time
import traceback
import shutil
import sys
import os

# Third Party
import requests
import certifi


if getattr(sys, 'frozen', False):
    Current_Path = os.path.dirname(sys.executable)
else:
    Current_Path = str(os.path.dirname(__file__))

# Setup logging
logger = logging.getLogger("Client")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s  %(levelname)s [%(name)s]: %(message)s'
)
filehandler = logging.FileHandler(os.path.join(Current_Path, 'client.log'))
filehandler.setLevel(logging.DEBUG)
filehandler.setFormatter(formatter)
logger.addHandler(filehandler)
streamhandler = logging.StreamHandler()
streamhandler.setLevel(logging.INFO)
streamhandler.setFormatter(formatter)
logger.addHandler(streamhandler)

logger.info("Logging started")
logging.captureWarnings(True)

# Portal endpoint
API_URL = "https://206.12.94.200:3000/api/"
USER_URL = "https://206.12.94.200:3000/user/"
# CERT = "../cert.pem"
CERT = os.path.join(Current_Path, "cert.pem")

# Setup query-delay parameters
BACK_OFF_TIME = 1.0
BACK_OFF_INCREMENT = 0.25
MAX_RETRIES = 20
# Download parameters
DL_CHUNK_SIZE = 4096

# Create session
s = requests.Session()

# Get cert (only needed once)
try:
    logger.info('Checking connection to Portal...')
    test = requests.get(API_URL)
    logger.info('Connection to Portal OK.')
except requests.exceptions.SSLError as err:
    logger.info('SSL Error. Adding custom certs to Certifi store...')
    ca_file = certifi.where()
    with open('cert.pem', 'rb') as infile:
        custom_ca = infile.read()
    with open(ca_file, 'ab') as outfile:
        outfile.write(custom_ca)
    logger.info('Certs added.')


def send_req(method="", endpoint="", url="", req_data=None, parameters=None, raw=False):
    # Remove password from logging
    if req_data:
        req_data_no_pw = req_data.copy()
        if "password" in req_data_no_pw.keys():
            req_data_no_pw["password"] = "HIDDEN"
    else:
        req_data_no_pw = {}
    # Log request
    logger.info(f"Sending {method} request to {endpoint}{url} with data:\n"
                f"{req_data_no_pw} \n "
                f"And parameters:\n"
                f"{parameters}")
    # Execute request
    method_using = s.get
    if method == "POST":
        method_using = s.post
    elif method == "GET":
        method_using = s.get
    else:
        logger.error("No method defined.")
        pass
    response = method_using(
        url=endpoint+url,
        data=req_data,
        params=parameters,
        verify=CERT
    )
    if raw:
        return response
    # Parse and return response
    parsed_response = response.json()
    logger.info(f"Response: {parsed_response}")

    return parsed_response


async def prezipped_download(parts, archive_name, download_dir=None):
    for part_number in range(parts):

        target = f"{archive_name}/{archive_name}_{part_number}.tar"
        try:
            logger.info(f"Trying tarball download. Part {part_number}")
            req_data = {
                "filepath": target
            }
            r = s.post(url=API_URL + "download_archive", data=req_data, verify=CERT)
            with open(f"{download_dir}\\{part_number}.tar", "wb") as f:
                for chunk in r.iter_content(chunk_size=DL_CHUNK_SIZE):
                    f.write(chunk)
            shutil.unpack_archive(f"{download_dir}\\{part_number}.tar",
                                  download_dir, 'tar')
            os.remove(f"{download_dir}\\{part_number}.tar")

        except Exception as e:
            logger.warning("Something went wrong.")
            logger.info(type(e))
            logger.info(traceback.format_exc())

    return True


async def get_files(part_number: int, job_id: str, target_folder):
    global BACK_OFF_TIME

    parameters = {
        "job_id": job_id,
        "part_number": part_number,
    }

    try_number = 0
    files_successfully_copied = False
    time_slept = 0.0

    while try_number < MAX_RETRIES and not files_successfully_copied:
        try_number += 1
        logger.debug(f"Try: {try_number} with back_off {BACK_OFF_TIME}")
        # Sending request for file
        response = send_req(
            method="GET",
            endpoint=API_URL,
            url="files_available",
            req_data=None,
            parameters=parameters
        )
        # Download data if ready on server
        if response["status"] == "ready" and len(response["file_list"]) > 0:
            BACK_OFF_TIME = BACK_OFF_TIME / 2

            part_id = job_id + "_" + str(part_number)
            buffer = "buffer1" if (part_number % 2) == 0 else "buffer2"

            try:

                logger.info(f"Trying to download {part_id}")
                # TODO: This should be processed server-side
                req_data = {
                    "filepath": job_id + "/" + buffer + "/" + part_id + ".tar"
                }
                data_response = send_req(
                    method="POST",
                    endpoint=API_URL,
                    url="download",
                    req_data=req_data,
                    parameters=None,
                    raw=True
                )
                with open(target_folder + "\\" + part_id + ".tar", "wb") as f:
                    for chunk in data_response.iter_content(chunk_size=DL_CHUNK_SIZE):
                        f.write(chunk)
                shutil.unpack_archive(target_folder + "\\" + part_id + ".tar",
                                      target_folder, 'tar')

                # Check all files had been copied
                downloaded = os.listdir(target_folder)
                files_successfully_copied = True
                for file in response["file_list"]:
                    files_successfully_copied &= file in downloaded

                if files_successfully_copied:
                    logger.debug(f"Download of {part_id} successful")
                    os.remove(target_folder + "\\" + part_id + ".tar")
                    return True, time_slept
            except Exception as e:
                logger.warning(f"While trying to download {part_id} an error occurred")
                files_successfully_copied = False
                logger.info(type(e))
                logger.info(traceback.format_exc())
        # Retry after Back-off interval, if data not ready
        else:
            logger.info("Data on server not ready")
            BACK_OFF_TIME += BACK_OFF_INCREMENT
        time_slept = time_slept + BACK_OFF_TIME
        time.sleep(BACK_OFF_TIME)
    logger.warning("Max tries exceeded. Moving to next part...")
    return False, time_slept


if __name__ == '__main__':
    # Login
    data = send_req(
        method="POST",
        endpoint=USER_URL,
        url="login",
        req_data={
            "username": "",
            "password": ""
        },
        parameters=None
    )
    # do things
    # In this example getting an overview of plants per months
    import datetime
    import pandas as pd
    month_row = []
    for year in [2020, 2021]:
        for month in range(1, 13):
            month_row.append(str(year)+"/"+str(month))
    df = pd.DataFrame({"Month": month_row})

    import json
    with open("metadata.json", "r") as f:
        metadata = json.load(f)

    for plant in metadata["eagli_plants"]:
        plant_row = []
        for year in [2020, 2021]:
            for month in range(1, 12):
                start_date = datetime.datetime(year, month, 1)
                end_date = datetime.datetime(year, month+1, 1)

                req_data = {
                    'eagli_parameters.start_date': start_date,
                    'eagli_parameters.end_date': end_date,
                    'eagli_parameters.min_age': 0,
                    'eagli_parameters.max_age': 1000,
                    'eagli_parameters.plants': [plant],
                    'eagli_parameters.plant_id': '',
                    'eagli_parameters.min_res': 0,
                    'eagli_parameters.max_res': 4000,
                    'eagli_parameters.single_plant_output': True,
                    'eagli_parameters.multiple_plant_output': False,
                    'eagli_parameters.bounding_box_output': False,
                    'eagli_parameters.json_output': False,
                    'eagli_parameters.archive_selection': '',
                    'eagli_parameters.custom_query_string': '',
                    'field_parameters.start_date': start_date,
                    'field_parameters.end_date': end_date,
                    'field_parameters.plants': '',
                    'field_parameters.archive_selection': '',
                    'field_parameters.custom_query_string': '',
                    'dataset': 'combined_images',
                    'sample_size': 10
                }
                data = send_req(
                    method="POST",
                    endpoint=API_URL,
                    url="check",
                    req_data=req_data,
                    parameters=None
                )
                # Process response data
                if "error" not in data.keys():
                    plant_row.append(data["number_files"])
                else:
                    plant_row.append(data["error"])
                # Return response data and gui-formatted response
            # December
            start_date = datetime.datetime(year, 12, 1)
            end_date = datetime.datetime(year+1, 1, 1)

            req_data = {
                'eagli_parameters.start_date': start_date,
                'eagli_parameters.end_date': end_date,
                'eagli_parameters.min_age': 0,
                'eagli_parameters.max_age': 1000,
                'eagli_parameters.plants': [plant],
                'eagli_parameters.plant_id': '',
                'eagli_parameters.min_res': 0,
                'eagli_parameters.max_res': 4000,
                'eagli_parameters.single_plant_output': True,
                'eagli_parameters.multiple_plant_output': False,
                'eagli_parameters.bounding_box_output': False,
                'eagli_parameters.json_output': False,
                'eagli_parameters.archive_selection': '',
                'eagli_parameters.custom_query_string': '',
                'field_parameters.start_date': start_date,
                'field_parameters.end_date': end_date,
                'field_parameters.plants': '',
                'field_parameters.archive_selection': '',
                'field_parameters.custom_query_string': '',
                'dataset': 'combined_images',
                'sample_size': 10
            }
            data = send_req(
                method="POST",
                endpoint=API_URL,
                url="check",
                req_data=req_data,
                parameters=None
            )
            # Process response data
            if "error" not in data.keys():
                plant_row.append(data["number_files"])
            else:
                plant_row.append(data["error"])
        # Write row
        df[plant] = plant_row

    # Return response data and gui-formatted response
    """from pandas import json_normalize
    normalized = json_normalize(sp_month_data)"""
    with open("../output_sp_by_plant.csv", "w") as f:
        df.to_csv(f)
