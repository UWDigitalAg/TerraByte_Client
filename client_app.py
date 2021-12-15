#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Michael Beck
#

# Core
import json
import logging
import datetime
import os
import sys

# Third party
import wx
import wx.adv

# Own
from client.commands import bind_command, check_cmd, sample_cmd, download_cmd, \
    login_cmd, logout_cmd, update_archives_cmd

if getattr(sys, 'frozen', False):
    Current_Path = os.path.dirname(sys.executable)
else:
    Current_Path = str(os.path.dirname(__file__))


VERSION = "1.0.0"

SAMPLE_SIZE = 10

JSON_LOCATION = os.path.join(Current_Path, "parameters.json")
METADATA_LOCATION = os.path.join(Current_Path, "metadata.json")


class Main(wx.Frame):
    def __init__(self, *args, **kwds):

        with open(METADATA_LOCATION, "r") as f:
            metadata = json.load(f)

        # Setup logger
        self.logger = logging.getLogger("Client.Main")
        self.logger.setLevel(logging.DEBUG)

        # Setup Frame
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((555, 479))
        self.SetTitle("TerraByte Client")

        self.tabs = wx.Notebook(self, wx.ID_ANY)

        self.eaglidata_tab = wx.Panel(self.tabs, wx.ID_ANY)
        self.tabs.AddPage(self.eaglidata_tab, "EAGL-I Data")

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        grid_sizer_2 = wx.FlexGridSizer(3, 4, 5, 5)
        sizer_1.Add(grid_sizer_2, 1, wx.EXPAND | wx.LEFT, 5)

        label_start_date = wx.StaticText(self.eaglidata_tab, wx.ID_ANY, "Start Date:")
        grid_sizer_2.Add(label_start_date, 0, wx.EXPAND, 0)

        self.datepicker_start_date = wx.adv.DatePickerCtrl(
            self.eaglidata_tab,
            wx.ID_ANY,
            dt=wx.DateTime(17, 3, year=2020),
            style=wx.adv.DP_DEFAULT | wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY
        )
        grid_sizer_2.Add(self.datepicker_start_date, 0, wx.EXPAND, 0)

        label_end_date = wx.StaticText(self.eaglidata_tab, wx.ID_ANY, "End Date:")
        grid_sizer_2.Add(label_end_date, 0, wx.EXPAND, 0)

        today = wx.DateTime().SetToCurrent()
        self.datepicker_end_date = wx.adv.DatePickerCtrl(
            self.eaglidata_tab,
            wx.ID_ANY,
            dt=today,
            style=wx.adv.DP_DEFAULT | wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY
        )
        grid_sizer_2.Add(self.datepicker_end_date, 0, wx.EXPAND, 0)

        label_age_min = wx.StaticText(self.eaglidata_tab, wx.ID_ANY, "Min. age in days:")
        grid_sizer_2.Add(label_age_min, 0, wx.EXPAND, 0)

        self.spin_age_min = wx.SpinCtrl(self.eaglidata_tab, wx.ID_ANY, "0", min=0, max=1000)
        grid_sizer_2.Add(self.spin_age_min, 0, wx.EXPAND, 0)

        label_age_max = wx.StaticText(self.eaglidata_tab, wx.ID_ANY, "Max. age in days:")
        grid_sizer_2.Add(label_age_max, 0, wx.EXPAND, 0)

        self.spin_age_max = wx.SpinCtrl(self.eaglidata_tab, wx.ID_ANY, "1000", min=0, max=1000)
        grid_sizer_2.Add(self.spin_age_max, 0, wx.EXPAND, 0)

        label_plants = wx.StaticText(self.eaglidata_tab, wx.ID_ANY, "Plants:")
        grid_sizer_2.Add(label_plants, 0, wx.EXPAND, 0)

        self.check_list_plants = wx.CheckListBox(
            self.eaglidata_tab,
            wx.ID_ANY,
            choices=metadata["eagli_plants"],
            style=wx.LB_ALWAYS_SB | wx.LB_EXTENDED | wx.LB_SORT
        )
        self.check_list_plants.SetMinSize((113, 80))
        grid_sizer_2.Add(self.check_list_plants, 0, wx.EXPAND, 0)

        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_2.Add(sizer_6, 1, wx.EXPAND, 0)

        label_plant_id = wx.StaticText(self.eaglidata_tab, wx.ID_ANY, "Plant ID:")
        sizer_6.Add(label_plant_id, 0, wx.EXPAND, 0)

        label_resolution_minimum = wx.StaticText(
            self.eaglidata_tab,
            wx.ID_ANY,
            "Min. Resolution (px):"
        )
        sizer_6.Add(label_resolution_minimum, 0, wx.TOP, 10)

        label_resolution_maximum = wx.StaticText(
            self.eaglidata_tab, wx.ID_ANY, "Max. Resolution (px):"
        )
        sizer_6.Add(label_resolution_maximum, 0, wx.TOP, 5)

        sizer_7 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_2.Add(sizer_7, 1, wx.EXPAND, 0)

        self.text_plant_id = wx.TextCtrl(self.eaglidata_tab, wx.ID_ANY, "")
        sizer_7.Add(self.text_plant_id, 0, wx.EXPAND, 0)

        self.spin_resolution_min = wx.SpinCtrl(
            self.eaglidata_tab, wx.ID_ANY, "0", min=0, max=4000
        )
        sizer_7.Add(self.spin_resolution_min, 0, wx.EXPAND, 0)

        self.spin_resolution_max = wx.SpinCtrl(
            self.eaglidata_tab, wx.ID_ANY, "4000", min=0, max=4000
        )
        sizer_7.Add(self.spin_resolution_max, 0, wx.EXPAND, 0)

        static_line_1 = wx.StaticLine(self.eaglidata_tab, wx.ID_ANY)
        sizer_1.Add(static_line_1, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 8)

        sizer_5 = wx.GridSizer(4, 2, 0, 0)
        sizer_1.Add(sizer_5, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        self.checkbox_single_plant_images = wx.CheckBox(
            self.eaglidata_tab, wx.ID_ANY, "Single Plant Images"
        )
        self.checkbox_single_plant_images.SetValue(1)
        sizer_5.Add(self.checkbox_single_plant_images, 0, wx.EXPAND, 0)

        label_archived_queries = wx.StaticText(self.eaglidata_tab, wx.ID_ANY, "Archived Queries:")
        sizer_5.Add(label_archived_queries, 0, wx.EXPAND, 0)

        self.checkbox_multiple_plant_images = wx.CheckBox(
            self.eaglidata_tab, wx.ID_ANY, "Multiple Plant Images"
        )
        sizer_5.Add(self.checkbox_multiple_plant_images, 0, wx.EXPAND, 0)

        plant_list = [""]
        plant_list.extend(metadata["eagli_archives"])
        self.combo_box_archived_queries = wx.ComboBox(
            self.eaglidata_tab,
            wx.ID_ANY,
            choices=plant_list,
            style=wx.CB_DROPDOWN | wx.CB_READONLY | wx.CB_SORT
        )
        sizer_5.Add(self.combo_box_archived_queries, 0, wx.EXPAND, 0)

        self.checkbox_bounding_box_images = wx.CheckBox(
            self.eaglidata_tab, wx.ID_ANY, "Bounding Box Images"
        )
        sizer_5.Add(self.checkbox_bounding_box_images, 0, wx.EXPAND, 0)

        sizer_5.Add((0, 0), 0, 0, 0)

        self.checkbox_json_files = wx.CheckBox(self.eaglidata_tab, wx.ID_ANY, "JSON Files")
        sizer_5.Add(self.checkbox_json_files, 0, wx.EXPAND, 0)

        sizer_5.Add((0, 0), 0, 0, 0)

        static_line_2 = wx.StaticLine(self.eaglidata_tab, wx.ID_ANY)
        sizer_1.Add(static_line_2, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 8)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        result_header_label = wx.StaticText(self.eaglidata_tab, wx.ID_ANY, "Result:")
        sizer_3.Add(result_header_label, 0, 0, 0)

        self.result_label = wx.StaticText(self.eaglidata_tab, wx.ID_ANY, "")
        sizer_3.Add(self.result_label, 0, wx.EXPAND, 0)

        grid_sizer_1 = wx.GridSizer(2, 3, 0, 0)
        sizer_1.Add(grid_sizer_1, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        self.check_button = wx.Button(self.eaglidata_tab, wx.ID_ANY, "Check Query")
        self.check_button.SetMinSize((125, 26))
        grid_sizer_1.Add(self.check_button, 0, 0, 0)

        self.sample_button = wx.Button(self.eaglidata_tab, wx.ID_ANY, "Get Sample")
        self.sample_button.SetMinSize((125, 26))
        grid_sizer_1.Add(self.sample_button, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        self.download_button = wx.Button(self.eaglidata_tab, wx.ID_ANY, "Download")
        self.download_button.SetMinSize((125, 26))
        grid_sizer_1.Add(self.download_button, 0, wx.ALIGN_RIGHT, 0)

        self.credentials_button = wx.Button(self.eaglidata_tab, wx.ID_ANY, "Set Credentials")
        self.credentials_button.SetMinSize((125, 26))
        grid_sizer_1.Add(self.credentials_button, 0, 0, 0)

        self.sample_path_button = wx.Button(self.eaglidata_tab, wx.ID_ANY, "Set Sample Path")
        self.sample_path_button.SetMinSize((125, 26))
        grid_sizer_1.Add(self.sample_path_button, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        self.download_path_button = wx.Button(self.eaglidata_tab, wx.ID_ANY, "Set Download Path")
        self.download_path_button.SetMinSize((125, 26))
        grid_sizer_1.Add(self.download_path_button, 0, wx.ALIGN_RIGHT, 0)

        self.fielddata_tab = wx.Panel(self.tabs, wx.ID_ANY)
        self.tabs.AddPage(self.fielddata_tab, "Fielddata")

        sizer_2 = wx.BoxSizer(wx.VERTICAL)

        grid_sizer_3 = wx.FlexGridSizer(3, 4, 5, 5)
        sizer_2.Add(grid_sizer_3, 1, wx.EXPAND | wx.LEFT, 5)

        label_start_date_field = wx.StaticText(self.fielddata_tab, wx.ID_ANY, "Start Date:")
        grid_sizer_3.Add(label_start_date_field, 0, 0, 0)

        self.datepicker_start_date_field = wx.adv.DatePickerCtrl(
            self.fielddata_tab,
            wx.ID_ANY,
            style=wx.adv.DP_DEFAULT | wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY
        )
        grid_sizer_3.Add(self.datepicker_start_date_field, 0, wx.EXPAND, 0)

        label_end_date_field = wx.StaticText(self.fielddata_tab, wx.ID_ANY, "End Date:")
        grid_sizer_3.Add(label_end_date_field, 0, 0, 0)

        self.datepicker_end_date_field = wx.adv.DatePickerCtrl(
            self.fielddata_tab,
            wx.ID_ANY,
            style=wx.adv.DP_DEFAULT | wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY
        )
        grid_sizer_3.Add(self.datepicker_end_date_field, 0, wx.EXPAND, 0)

        grid_sizer_3.Add((0, 0), 0, 0, 0)

        grid_sizer_3.Add((0, 0), 0, 0, 0)

        grid_sizer_3.Add((0, 0), 0, 0, 0)

        grid_sizer_3.Add((0, 0), 0, 0, 0)

        label_plants_field = wx.StaticText(self.fielddata_tab, wx.ID_ANY, "Plants:")
        grid_sizer_3.Add(label_plants_field, 0, 0, 0)

        self.check_list_plants_field = wx.CheckListBox(
            self.fielddata_tab,
            wx.ID_ANY,
            choices=metadata["field_plants"],
            style=wx.LB_ALWAYS_SB | wx.LB_EXTENDED | wx.LB_SORT
        )
        self.check_list_plants_field.SetMinSize((113, 80))
        grid_sizer_3.Add(self.check_list_plants_field, 0, 0, 0)

        grid_sizer_3.Add((0, 0), 0, 0, 0)

        grid_sizer_3.Add((0, 0), 0, 0, 0)

        static_line_3 = wx.StaticLine(self.fielddata_tab, wx.ID_ANY)
        sizer_2.Add(static_line_3, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 8)

        sizer_10 = wx.GridSizer(4, 2, 0, 0)
        sizer_2.Add(sizer_10, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        sizer_10.Add((0, 0), 0, 0, 0)

        label_archived_queries_field = wx.StaticText(
            self.fielddata_tab, wx.ID_ANY, "Archived Queries:"
        )
        sizer_10.Add(label_archived_queries_field, 0, 0, 0)

        sizer_10.Add((0, 0), 0, 0, 0)

        plant_list = [""]
        plant_list.extend(metadata["field_archives"])
        self.combo_box_archived_queries_field = wx.ComboBox(
            self.fielddata_tab,
            wx.ID_ANY,
            choices=plant_list,
            style=wx.CB_DROPDOWN | wx.CB_READONLY | wx.CB_SORT
        )
        sizer_10.Add(self.combo_box_archived_queries_field, 0, wx.EXPAND, 0)

        sizer_10.Add((0, 0), 0, 0, 0)

        sizer_10.Add((0, 0), 0, 0, 0)

        sizer_10.Add((0, 0), 0, 0, 0)

        sizer_10.Add((0, 0), 0, 0, 0)

        static_line_4 = wx.StaticLine(self.fielddata_tab, wx.ID_ANY)
        sizer_2.Add(static_line_4, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 8)

        sizer_4 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(sizer_4, 1, wx.EXPAND, 0)

        result_header_label_field = wx.StaticText(self.fielddata_tab, wx.ID_ANY, "Result:")
        sizer_4.Add(result_header_label_field, 0, 0, 0)

        self.result_label_field = wx.StaticText(self.fielddata_tab, wx.ID_ANY, "")
        sizer_4.Add(self.result_label_field, 0, wx.EXPAND, 0)

        grid_sizer_4 = wx.GridSizer(2, 3, 0, 0)
        sizer_2.Add(grid_sizer_4, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        self.check_button_field = wx.Button(self.fielddata_tab, wx.ID_ANY, "Check Query")
        self.check_button_field.SetMinSize((125, 26))
        grid_sizer_4.Add(self.check_button_field, 0, 0, 0)

        self.sample_button_field = wx.Button(self.fielddata_tab, wx.ID_ANY, "Get Sample")
        self.sample_button_field.SetMinSize((125, 26))
        grid_sizer_4.Add(self.sample_button_field, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        self.download_button_field = wx.Button(self.fielddata_tab, wx.ID_ANY, "Download")
        self.download_button_field.SetMinSize((125, 26))
        grid_sizer_4.Add(self.download_button_field, 0, wx.ALIGN_RIGHT, 0)

        grid_sizer_4.Add((0, 0), 0, 0, 0)

        grid_sizer_4.Add((0, 0), 0, 0, 0)

        grid_sizer_4.Add((0, 0), 0, 0, 0)

        self.info_tab = wx.Panel(self.tabs, wx.ID_ANY)
        self.tabs.AddPage(self.info_tab, "Info")

        sizer_8 = wx.BoxSizer(wx.VERTICAL)

        label_version = wx.StaticText(self.info_tab, wx.ID_ANY, "Version: "+VERSION)
        sizer_8.Add(label_version, 0, 0, 0)

        label_author = wx.StaticText(
            self.info_tab,
            wx.ID_ANY,
            "The TerraByte Client is developed by Michael Beck. "
            "Contact: m.beck@uwinnipeg.ca"
        )
        sizer_8.Add(label_author, 0, 0, 0)

        self.hyperlink_citation_info = wx.adv.HyperlinkCtrl(
            self.info_tab,
            wx.ID_ANY,
            "Citation Information and Terms of use",
            "https://terrabyte.acs.uwinnipeg.ca/resources.html#tools"
        )
        sizer_8.Add(self.hyperlink_citation_info, 0, 0, 0)

        self.hyperlink_parameter_explanation = wx.adv.HyperlinkCtrl(
            self.info_tab,
            wx.ID_ANY,
            "Manual",
            "https://terrabyte.acs.uwinnipeg.ca/resources.html#tools"
        )
        sizer_8.Add(self.hyperlink_parameter_explanation, 0, 0, 0)

        self.video_tutorial = wx.adv.HyperlinkCtrl(
            self.info_tab,
            wx.ID_ANY,
            "GitHub",
            "https://youtu.be/2MX4ascCTq0"
        )
        sizer_8.Add(self.video_tutorial, 0, 0, 0)

        self.github = wx.adv.HyperlinkCtrl(
            self.info_tab,
            wx.ID_ANY,
            "GitHub",
            "https://github.com/UWDigitalAg/TerraByte_Client"
        )
        sizer_8.Add(self.github, 0, 0, 0)

        self.info_tab.SetSizer(sizer_8)

        grid_sizer_3.AddGrowableRow(0)
        grid_sizer_3.AddGrowableRow(1)
        grid_sizer_3.AddGrowableCol(0)
        grid_sizer_3.AddGrowableCol(2)
        grid_sizer_3.AddGrowableCol(3)

        self.fielddata_tab.SetSizer(sizer_2)

        grid_sizer_2.AddGrowableRow(0)
        grid_sizer_2.AddGrowableRow(1)
        grid_sizer_2.AddGrowableRow(2)
        grid_sizer_2.AddGrowableCol(0)
        grid_sizer_2.AddGrowableCol(1)
        grid_sizer_2.AddGrowableCol(2)
        grid_sizer_2.AddGrowableCol(3)

        self.eaglidata_tab.SetSizer(sizer_1)

        self.Layout()

        # Give buttons dataset context
        for b in [self.check_button, self.sample_button, self.download_button]:
            b.dataset = "combined_images"  # EAGL-I data
        for b in [self.check_button_field, self.sample_button_field, self.download_button_field]:
            b.dataset = "field_images"  # Field data

        self.Bind(wx.EVT_BUTTON, self.send_check_request, self.check_button)
        self.Bind(wx.EVT_BUTTON, self.send_sample_request, self.sample_button)
        self.Bind(wx.EVT_BUTTON, self.send_download_request, self.download_button)
        self.Bind(wx.EVT_BUTTON, self.update_user_credentials, self.credentials_button)
        self.Bind(wx.EVT_BUTTON, self.change_sample_path, self.sample_path_button)
        self.Bind(wx.EVT_BUTTON, self.change_download_path, self.download_path_button)
        self.Bind(wx.EVT_BUTTON, self.send_check_request, self.check_button_field)
        self.Bind(wx.EVT_BUTTON, self.send_sample_request, self.sample_button_field)
        self.Bind(wx.EVT_BUTTON, self.send_download_request, self.download_button_field)
        # end wxGlade

        # Load parameters from last session
        try:
            with open(JSON_LOCATION, 'r') as f:
                self.parameters = json.load(f)
        except FileNotFoundError:
            self.username = ""
            self.password = ""
            os.mkdir("sample")
            os.mkdir("download")
            self.sample_dir = "./sample"
            self.download_dir = "./download"
            json_obj = {
                    "login": "",
                    "password": "",
                    "sample": "./sample",
                    "download": "./download"
                }
            with open(JSON_LOCATION, "w") as f:
                json.dump(json_obj, f)
            self.parameters = json_obj

        self.username = self.parameters["login"]
        self.password = self.parameters["password"]

        # Load directory locations from last session
        self.sample_dir = self.parameters["sample"]
        self.download_dir = self.parameters["download"]

        # Sample size
        self.sample_size = SAMPLE_SIZE

        # GUI-input package to be sent to commands
        self.query_parameters = {}
        self.eagli_parameters = {}
        self.field_query_parameters = {}
        self.gui_input = {}

        # Initialize parameters
        self.update_parameters()

        # Login User with previously given credentials
        data = login_cmd(
            self.gui_input, password=self.parameters["password"]
        )
        self.update_gui(data)

        # Get archive list
        self.update_gui(update_archives_cmd(self.gui_input))

    @bind_command(check_cmd)
    def send_check_request(self, event):  # wxGlade: Main.<event_handler>
        pass

    @bind_command(sample_cmd)
    def send_sample_request(self, event):  # wxGlade: Main.<event_handler>
        pass

    @bind_command(download_cmd)
    def send_download_request(self, event):  # wxGlade: Main.<event_handler>
        pass

    def update_user_credentials(self, event):  # wxGlade: Main.<event_handler>
        self.logger.info("Updating user credentials...")
        username_dialog = wx.TextEntryDialog(
            self, message="Username:"
        )
        if username_dialog.ShowModal() == wx.ID_OK:
            password_dialog = wx.PasswordEntryDialog(
                self, message="Password:"
            )
            if password_dialog.ShowModal() == wx.ID_OK:
                self.username = username_dialog.GetValue()
                self.password = password_dialog.GetValue()
            password_dialog.Destroy()
        username_dialog.Destroy()
        self.update_parameters(write_json=True)
        logout_cmd(self.gui_input)
        # password passed as extra argument to not have it appear in log files
        data = login_cmd(self.gui_input, password=self.password)
        self.update_gui(data)
        event.Skip()

    def change_sample_path(self, event):  # wxGlade: Main.<event_handler>
        self.logger.info("Update path to sample folder...")
        directory_dialog = wx.DirDialog(
            self, message="Choose folder for sample preview"
        )
        if directory_dialog.ShowModal() == wx.ID_OK:
            self.sample_dir = directory_dialog.GetPath()
        directory_dialog.Destroy()
        self.update_parameters(write_json=True)
        event.Skip()

    def change_download_path(self, event):  # wxGlade: Main.<event_handler>
        self.logger.info("Update path to download folder...")
        directory_dialog = wx.DirDialog(
            self, message="Choose download folder"
        )
        if directory_dialog.ShowModal() == wx.ID_OK:
            self.download_dir = directory_dialog.GetPath()
        directory_dialog.Destroy()
        self.update_parameters(write_json=True)
        event.Skip()

    def update_parameters(self, event=None, write_json=False):
        self.logger.info("Updating client parameters")
        if write_json:
            with open("./parameters.json", "w") as f:
                json.dump({
                    "login": self.username,
                    "password": self.password,
                    "download": self.download_dir,
                    "sample": self.sample_dir}, f
                )
        self.eagli_parameters = {
            "start_date": self._wxdate2pydate(self.datepicker_start_date.GetValue()),
            "end_date": self._wxdate2pydate(self.datepicker_end_date.GetValue()),
            "min_age": self.spin_age_min.GetValue(),
            "max_age": self.spin_age_max.GetValue(),
            "plants": list(self.check_list_plants.GetCheckedStrings()),
            "plant_id": self.text_plant_id.GetValue(),
            "min_res": self.spin_resolution_min.GetValue(),
            "max_res": self.spin_resolution_max.GetValue(),
            "single_plant_output": self.checkbox_single_plant_images.GetValue(),  # True/False
            "multiple_plant_output": self.checkbox_multiple_plant_images.GetValue(),
            "bounding_box_output": self.checkbox_bounding_box_images.GetValue(),
            "json_output": self.checkbox_json_files.GetValue(),
            "archive_selection": self.combo_box_archived_queries.GetValue(),
        }
        self.field_query_parameters = {
            "start_date": self._wxdate2pydate(self.datepicker_start_date_field.GetValue()),
            "end_date": self._wxdate2pydate(self.datepicker_end_date_field.GetValue()),
            "plants": list(self.check_list_plants_field.GetCheckedStrings()),
            "archive_selection": self.combo_box_archived_queries_field.GetValue(),
        }
        self.gui_input = {
            "username": self.username,
            "query_parameters": {
                "eagli_parameters": self.eagli_parameters,
                "field_parameters": self.field_query_parameters
            },
            "sample_size": self.sample_size,
            "sample_dir": self.sample_dir,
            "download_dir": self.download_dir,
        }
        if event:
            self.gui_input["dataset"] = event.GetEventObject().dataset
        else:
            self.gui_input["dataset"] = ""

    def update_gui(self, gui_output):
        if "message" in gui_output.keys():
            self.result_label.SetLabelText(gui_output["message"])
            self.result_label_field.SetLabelText(gui_output["message"])
        if "error" in gui_output.keys():
            msg = self.result_label.Label
            self.result_label.SetLabelText(msg + " Error: " + gui_output["error"])
            self.result_label_field.SetLabelText(msg + " Error: " + gui_output["error"])

        if "archive_list" in gui_output.keys():
            collections_list = {
                "combined_images": {
                    "combobox": self.combo_box_archived_queries,
                    "archives": [],
                    "tab": self.eaglidata_tab,
                    "JSON_name": "eagli_archives"
                },
                "field_images": {
                    "combobox": self.combo_box_archived_queries_field,
                    "archives": [],
                    "tab": self.fielddata_tab,
                    "JSON_name": "field_archives"
                },
            }
            # Split archive list by collection
            for row in gui_output["archive_list"]:
                for data_type in collections_list.keys():
                    if row[2] == data_type:
                        collections_list[data_type]["archives"].append(row)

            # Update Comboboxes
            for collection in collections_list.values():
                collection["combobox"].Clear()
                collection["combobox"].AppendItems([""])
                collection["combobox"].AppendItems([
                        row[1] + f" ({row[-1]} GB)" for row in collection["archives"]
                ])
                self.Update()
            # Update JSON-Files
            with open("metadata.json", "r") as f:
                self.logger.info("Updating metadata.json")
                old_metadata = json.load(f)
                for collection in collections_list.values():
                    old_metadata[collection["JSON_name"]] = [
                        row[1] + f" ({row[-1]} GB)" for row in collection["archives"]
                    ]
            with open("metadata.json", "w") as f:
                json.dump(old_metadata, f)

    @staticmethod
    def _wxdate2pydate(wx_date):
        f = wx_date.Format('%d/%m/%y %H:%M:%S')
        return datetime.datetime.strptime(f, '%d/%m/%y %H:%M:%S')

    # end of class Main


# noinspection PyAttributeOutsideInit
class TerraByteClient(wx.App):
    def OnInit(self):
        self.frame = Main(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

# end of class TerraByteClient


if __name__ == "__main__":
    TerraByte_Client = TerraByteClient(0)
    TerraByte_Client.MainLoop()
