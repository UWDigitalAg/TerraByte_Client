# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 20:56:24 2020

@author: M
"""
import functools
import threading
import logging
import traceback
import asyncio
from pandas import json_normalize
from dataclasses import dataclass, field
from typing import List

from client.simple_client import API_URL, USER_URL, get_files, send_req, \
    prezipped_download

logger = logging.getLogger("Client.Main")
logger.setLevel(logging.DEBUG)


# import this to your GUI
# command decorator
def bind_command(cmd):
    def bind_command_decorator(func):
        @functools.wraps(func)
        def bind_command_wrapper(gui, event):
            func(gui, event)
            gui.update_parameters(event=event)
            gui.result_label.SetLabelText("Processing...")
            gui.result_label_field.SetLabelText("Processing...")
            data = cmd(gui.gui_input)
            if "error" in data.keys():
                logger.error(data["error"])
            gui.update_gui(data)
            event.Skip()
            return data

        return bind_command_wrapper
    return bind_command_decorator


# logger decorator
def log_command(func):
    @functools.wraps(func)
    def wrapper_keep_log(gui_input, **kwargs):
        # Unpack gui_input
        query_data = json_normalize(
            gui_input["query_parameters"], sep="."
        ).to_dict(orient='records')[0]

        for k, v in query_data.items():
            if isinstance(v, list):
                query_data[k] = ",".join(v)

        query_data["dataset"] = gui_input["dataset"]
        query_data["sample_size"] = gui_input["sample_size"]

        # Send request
        arguments = {
            "username": gui_input["username"],
            "query_data": query_data,
            "sample_dir": gui_input["sample_dir"],
            "download_dir": gui_input["download_dir"]
        }
        # log function call
        logger.info(f"Executing command {func.__name__!r} with arguments:\n"
                    f"{arguments}"
                    )
        # call function
        value = func(**arguments, **kwargs)
        return value
    return wrapper_keep_log


# noinspection PyUnusedLocal
@log_command
def login_cmd(username="", password="", **kwargs):
    # Send request
    data = send_req(
        method="POST",
        endpoint=USER_URL,
        url="login",
        req_data={
            "username": username,
            "password": password
        },
        parameters=None
    )
    return data


# noinspection PyUnusedLocal
@log_command
def logout_cmd(**kwargs):
    # Send request
    data = send_req(
        method="POST",
        endpoint=USER_URL,
        url="logout",
        req_data=None,
        parameters=None
    )
    return data


# noinspection PyUnusedLocal
@log_command
def check_cmd(query_data=None, **kwargs):
    # Send request
    data = send_req(
        method="POST",
        endpoint=API_URL,
        url="check",
        req_data=query_data,
        parameters=None
    )
    return data


# noinspection PyUnusedLocal
@log_command
def sample_cmd(query_data=None, sample_dir=None, **kwargs):
    # Send Request
    data = send_req(
        method="POST",
        endpoint=API_URL,
        url="prepare",
        req_data=query_data,
        parameters=None
    )
    # Process response data
    if "error" not in data.keys():
        try:
            DownloadThread([0],
                           data["job_id"],
                           sample_dir)
        except Exception as e:
            logger.error("Unable to download sample files.")
            logger.error(type(e))
            logger.error(traceback.format_exc())
        finally:
            pass
    return data


# noinspection PyUnusedLocal
@log_command
def download_cmd(query_data=None, download_dir=None, **kwargs):
    # Send Request
    query_data["sample_size"] = 0
    data = send_req(
        method="POST",
        endpoint=API_URL,
        url="prepare",
        req_data=query_data,
        parameters=None
    )
    # Process response data
    if "error" not in data.keys():
        if data["archived"] is False:
            try:
                DownloadThread([x for x in range(data["parts"])],
                               data["job_id"],
                               download_dir)
            except Exception as e:
                logger.error("Unable to download files.")
                logger.error(type(e))
                logger.error(traceback.format_exc())
            finally:
                pass
        elif data["archived"] is True:
            try:
                logger.info("Downloading prezipped files")
                asyncio.run(
                    prezipped_download(data["parts"],
                                       archive_name=data["archive_name"],
                                       download_dir=download_dir)
                )

            except Exception as e:
                logger.error("Unable to download files.")
                logger.error(type(e))
                logger.error(traceback.format_exc())
            finally:
                pass
    return data


# noinspection PyUnusedLocal
@log_command
def update_archives_cmd(**kwargs):
    # Send request
    data = send_req(
        method="GET",
        endpoint=API_URL,
        url="list_archives",
        req_data=None,
        parameters=None
    )
    return data


# Helper Class Download-Thread
@dataclass(eq=False)
class DownloadThread(threading.Thread):
    part_numbers: List[int] = field(default_factory=list)
    job_id: str = ""
    directory: str = ""

    def __post_init__(self):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger("Client.DLThread")
        self.logger.setLevel(logging.DEBUG)

        self.start()
        self.total_wait_time_on_server = 0.0

    def run(self):
        self.logger.info(f"Starting Download Thread for job {self.job_id}")
        for part in self.part_numbers:
            self.logger.info(f"Getting part {part}")
            success, time_slept = asyncio.run(
                get_files(part, self.job_id, self.directory)
            )
            self.logger.info(f"Download successful: {success}. "
                             f"Time waited on server: {time_slept}")
            self.total_wait_time_on_server += time_slept
            parameters = {
                "job_id": self.job_id,
                "part_number": part,
                "final_part": (part == len(self.part_numbers) - 1)
            }
            send_req(
                method="GET",
                endpoint=API_URL,
                url="ack_download",
                req_data=None,
                parameters=parameters
            )
        self.logger.info(f"Download Thread for {self.job_id} FINISHED")
        self.logger.info("We waited {0} on server".format(
            self.total_wait_time_on_server)
        )
