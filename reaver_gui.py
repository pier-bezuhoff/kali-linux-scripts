#!/usr/bin/env python3
# python3.6 compatiable (due to format strings and Path as str)
"""The module contains simple GUI for Wi-Fi penetration testing tools (aircrack-ng, reaver, ...)
you should first install the tools (full list you can find in dependencies.txt)
ALSO: a bit of code use module filesystem (TODO: remove), so it's necessary too.
`lib` path is global, so it should be configured manually.
File structure:
----------------------
reaver_gui.py
lib/
----tmp/ # empty
----reaver_help.txt
----wash_help.txt
----short_help.txt
----[last_session.*]
----[wifi_database.*]
----[...]
----dependencies.txt
----------------------
"""
import tkinter as tk
from tkinter import filedialog as fd
from collections import OrderedDict
import threading
from itertools import chain
# import queue
from time import time, sleep
from os import system
from pathlib import Path
import os
import dbm
import pickle
import shelve
# NOTE: size: *.csv < *.pkl < *.db < *[shelve].db
# FEATURES:
# *.csv:        human readable and lightest
# *.pkl:        computer easy readable (python inborn)
# *.db:         key access
# *[shelve].db: key access, computer easy readable (but weight)
# All the properties depend on data

# wlan0mon -> interface
# f"str" -> str.format(...)
# TODO: add more flexible default arguments and store initial commands in file
# TODO: add changing interface
# TODO: add some usual terminal commands to the top menu
# TODO: move settings to .json and add its editor

lib = Path(__file__).parent / "lib"
assert lib.exists(), "lib directory {} does not exist".format(lib)
tmp = lib / "tmp"
if not tmp.exists():
    tmp.mkdir()
else:
    for x in os.listdir(tmp):
        os.remove(tmp / x)
wifi_database_file = lib / "wifi_database.pkl"
last_wifi_list_file = lib / "last_session.pkl"
default_tool_arguments_file = lib / "default_tool_arguments.pkl"
initial_commands_file = lib / "initial_commands.pkl"
help_file = lib / "short_help.txt"
estimate_file = tmp / "estimate.txt"
estimate_file.open('w').close() # create/truncate file
interface = 'wlo1mon' # 'wlan0mon'

class App:

    programs = ('reaver', 'wash', 'aircrack-ng', 'airodump-ng', 'aireplay-ng')
    order = ('essid', 'bssid', 'channel', 'wps', 'auth', 'power', 'macs')
    airodump_updatable_options = ('essid', 'power', 'speed', 'macs', 'auth')
    wash_updatable_options = ('essid', 'wps',)
    database_updatable_options = ('essid', 'channel', 'wps', 'auth', 'macs', 'speed')

    menu_font = 'ubuntu 12' # in 'add_cascade'
    submenu_font = 'ubuntu 11' # in 'add_command'
    checkbutton_font = 'ubuntu 12' # in 'select_action', option name
    description_label_font = 'ubuntu 11' # in 'select_action', description of option
    wifi_label_font = 'ubuntu 14' # in 'list_wifis'
    cmd_entry_font = 'ubuntu 14' # in 'select_action'
    request_label_font = 'ubuntu 15' # in 'request_option/other'
    request_entry_font = 'ubuntu 16' # in 'request_option/other'
    button_font = 'ubuntu 12' # in 'request_option/other'

    frame_bg = 'grey'
    wifi_key_label_bg = 'black'
    wifi_key_label_fg = 'lightblue'
    wifi_label_bg = 'grey'
    wifi_label_fg = 'lightgreen'
    wifi_enlighted_label_bg = 'lightgrey'
    wifi_enlighted_label_fg = 'darkgreen'

    def __init__(self):
        self.filters = lambda x: x
        self.wifi_list = []
        self.viewed_list = self.wifi_list
        self.wifi_database = []
        self.generate_helps()
        self.load_tool_options()
        self.load_default_arguments()

        print("Loading GUI...", end=' ')

        self.root = tk.Tk()
        self.root.title("Wi-Fi GUI")
        wifikey_icon = tk.PhotoImage(file=str(lib/"wifikey.png"), format='png')
        self.root.tk.call('wm', 'iconphoto', self.root._w, wifikey_icon) # setting up icon
        ## Top menu
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        #   'File' menu
        file_menu = tk.Menu(menu)
        file_menu.add_command(label="Load...", font=App.submenu_font, command=lambda: self.load_wifi_list(relist=True))
        file_menu.add_command(label="Load last", font=App.submenu_font, command=lambda: self.load_last_wifi_list(relist=True))
        file_menu.add_command(label="Save", font=App.submenu_font, command=self.save_wifi_list)
        file_menu.add_command(label="Save all", font=App.submenu_font, command=self.save)
        file_menu.add_command(label="Save as...", font=App.submenu_font, command=self.save_as_wifi_list)
        file_menu.add_command(label="Exit", font=App.submenu_font, command=self.escape_and_save)
        menu.add_cascade(label="File", font=App.menu_font, menu=file_menu)
        self.file_menu = file_menu
        #   'Wi-Fi database' menu
        wifi_database_menu = tk.Menu(menu)
        wifi_database_menu.add_command(label="Load database", font=App.submenu_font, command=self.load_wifi_database)
        wifi_database_menu.add_command(label="Update from database", font=App.submenu_font, command=lambda: self.update_from_wifi_database(relist=True))
        wifi_database_menu.add_command(label="Update database", font=App.submenu_font, command=self.update_wifi_database)
        wifi_database_menu.add_command(label="Import from .db", font=App.submenu_font, command=lambda: self.update_wifi_database(L=import_db()))
        wifi_database_menu.add_command(label="Import from .csv", font=App.submenu_font, command=lambda: self.update_wifi_database(L=import_csv()))
        wifi_database_menu.add_command(label="Export to .db", font=App.submenu_font, command=lambda: export_db(L=self.wifi_database))
        wifi_database_menu.add_command(label="Export to .csv", font=App.submenu_font, command=lambda: export_csv(L=self.wifi_database))
        self.disable_menu(wifi_database_menu, "Update from database")
        self.disable_menu(wifi_database_menu, "Update database")
        self.disable_menu(wifi_database_menu, "Import from .db")
        self.disable_menu(wifi_database_menu, "Import from .csv")
        self.disable_menu(wifi_database_menu, "Export to .db")
        self.disable_menu(wifi_database_menu, "Export to .csv")
        menu.add_cascade(label="Wi-Fi database", font=App.menu_font, menu=wifi_database_menu)
        self.wifi_database_menu = wifi_database_menu
        #   'Tools' menu
        tool_menu = tk.Menu(menu)
        tool_menu.add_command(label=f"Prepare {interface}", font=App.submenu_font, command=lambda: self.execute(f"./prepare_inteface_mon.sh {interface}"))
        tool_menu.add_command(label="See ifconfig", font=App.submenu_font, command=lambda: self.execute("ifconfig"))
        tool_menu.add_command(label="Start macchanger", font=App.submenu_font, command=lambda: self.execute("macchanger -h"))
        self.disable_menu(tool_menu, "See ifconfig")
        menu.add_cascade(label="Tools", font=App.menu_font, menu=tool_menu)
        self.tool_menu = tool_menu
        #   'Scan' menu
        scan_menu = tk.Menu(menu)
        scan_menu.add_command(label="Scan with airodump-ng", font=App.submenu_font, command=self.start_airmodump_search)
        scan_menu.add_command(label="Scan with wash", font=App.submenu_font, command=self.start_wash_search)
        scan_menu.add_command(label="Update from airodump-ng", font=App.submenu_font, command=lambda: self.update_from_airodump_list(relist=True))
        scan_menu.add_command(label="Update from wash", font=App.submenu_font, command=lambda: self.update_from_wash_list(relist=True))
        scan_menu.add_command(label="Stop updating", font=App.submenu_font, command=self.stop_thread)
        self.disable_menu(scan_menu, "Update from airodump-ng")
        self.disable_menu(scan_menu, "Update from wash")
        self.disable_menu(scan_menu, "Stop updating")
        menu.add_cascade(label="Scan", font=App.menu_font, menu=scan_menu)
        self.scan_menu = scan_menu
        #   'View' menu
        view_menu = tk.Menu(menu)
        filter_menu = tk.Menu(view_menu)
        filter_menu.add_command(label="All", font=App.submenu_font, command=lambda: self.set_filters(lambda x: x))
        filter_menu.add_command(label="WPA/WPA2 only", font=App.submenu_font, command=lambda: self.set_filters(lambda x: 'wpa' in x['auth'].lower()))
        filter_menu.add_command(label="WPS only", font=App.submenu_font, command=lambda: self.set_filters(lambda x: len(x['wps']) > 1))
        filter_menu.add_command(label="WEP only", font=App.submenu_font, command=lambda: self.set_filters(lambda x: 'wep' in x['auth'].lower()))
        filter_menu.add_command(label="Known WPS PIN", font=App.submenu_font, command=lambda: self.set_filters(lambda x: 'wps_pin' in x))
        filter_menu.add_command(label="Known WPA PSK", font=App.submenu_font, command=lambda: self.set_filters(lambda x: 'wpa_psk' in x))
        filter_menu.add_command(label="Pixie-Dust: not crackable", font=App.submenu_font, command=lambda: self.set_filters(lambda x: x.get('pixie', None) == 'no'))
        filter_menu.add_command(label="Pixie-Dust: cracked", font=App.submenu_font, command=lambda: self.set_filters(lambda x: x.get('pixie', None) == 'yes'))
        filter_menu.add_command(label="Pixie-Dust: unknown", font=App.submenu_font, command=lambda: self.set_filters(lambda x: len(x['wps']) > 1 and x.get('pixie', '') == ''))
        filter_menu.add_command(label="WPS PIN bruteforce: tried", font=App.submenu_font, command=lambda: self.set_filters(lambda x: 'p1_index' in x or 'p2_index' in x))
        filter_menu.add_command(label="WPS PIN bruteforce: not tried", font=App.submenu_font, command=lambda: self.set_filters(lambda x: len(x['wps']) > 1 and not ('p1_index' in x or 'p2_index' in x)))
        filter_menu.add_command(label="Unknown only", font=App.submenu_font, command=lambda: self.set_filters(lambda x: x['auth'] == x['wps'] == '' or x['essid'] == ''))
        filter_menu.add_command(label="Show unknown", font=App.submenu_font, command=lambda: self.or_filters(lambda x: x['auth'] == x['wps'] == ''))
        filter_menu.add_command(label="Hide unknown", font=App.submenu_font, command=lambda: self.and_filters(lambda x: not (x['auth'] == x['wps'] == '' or x['essid'] == '')))
        # filter_menu.add_command(label="Recent only", font=App.submenu_font, command=...)

        sort_menu = tk.Menu(view_menu)
        sort_menu.add_command(label="Ascending/descending order", font=App.submenu_font, command=lambda: ...)
        ...
        view_menu.add_cascade(label="Filter", font=App.submenu_font, menu=filter_menu)
        view_menu.add_cascade(label="Sorting", font=App.submenu_font, menu=sort_menu)
        view_menu.add_command(label="Default", font=App.submenu_font, command=self.reset_view)
        menu.add_cascade(label="View", font=App.menu_font, menu=view_menu)
        self.view_menu = view_menu
        #   'Help' menu
        help_menu = tk.Menu(menu)
        help_menu.add_command(label="Short help", font=App.submenu_font, command=self.display_help)
        menu.add_cascade(label="Help", font=App.menu_font, menu=help_menu)
        ## end of the top menu

        # start
        self.sorting = None
        self.reversed_sorting = False
        self.list_frame = None
        self.list_wifis()
        self.root.bind('<Escape>', lambda event: self.escape_and_save())
        print("Done")
        print("Application started")
        self.root.mainloop()

    def generate_helps(self):
        """generate option helps for program in App.programs and macchanger"""
        print("Generating helps...", end=' ')
        for program in App.programs + ("macchanger",):
            redirect = f"{program} --help >"
            if program in ("reaver", "wash"): # they print help to stderr...
                redirect = f"{program} --help 2>"
            self.generate_help(program, redirect)
        print("Done")

    def generate_help(self, cmd, redirect):
        """dynamic generation helps on option from <program> --help and save import them as tmp/<program>_description.txt"""
        cmd = cmd.split()[0]
        system("{} {}/{}_help.txt".format(redirect, tmp, cmd))
        description = "@{}\n".format(cmd)
        option = 'header'
        if 'macchanger' in cmd:
            option = "Option"
        with open("{}/{}_help.txt".format(tmp, cmd), 'r') as file:
            for s in file:
                if s.strip().lower().endswith("options:") or s.strip().lower().endswith("arguments:") or s.strip().lower().endswith("modes:"):
                    option = s.strip()[:-2]
                elif option == 'header':
                    description += s
                elif len(s.strip()) != 0 and s.strip().startswith('-'):
                    s = s.strip()
                    description += "@{}\n".format(s.split()[0].split(',')[0])
                    description += ' '.join(s.replace(" : ", " # ").split()) + '\n'
                    # description += option + '\n'
                elif len(s.strip()) != 0 and not s.strip().startswith('-'):
                    description += ' '.join(s.strip().split()) + '\n'
        with open("{}/{}_description.txt".format(tmp, cmd), 'w') as file:
            file.write(description)

    def load_tool_options(self):
        """load options for every program in App.programs from previously generated tmp/<program>_description.txt"""
        print("Loading tool options...", end=' ')
        App.tool_options = {program: self.load_options(program) for program in App.programs}
        print("Done")

    def load_options(self, program):
        """decode tmp/<program>_description.txt and return list of option"""
        with open("{}/{}_description.txt".format(tmp, program), 'r') as file:
            L = [s[1:].strip() for s in file.readlines()[1:] if s.strip().startswith('@')]
        return L

    def load_default_arguments(self, file=default_tool_arguments_file):
        """with previously loaded App.tool_options load saved in .pkl default arguments (you can add them)"""
        print("Loading default tool arguments...", end=' ')
        App.tool_arguments = {program: {option: ("", '') for option in App.tool_options[program]} for program in App.programs}
        with file.open('rb') as fd:
            d = pickle.load(fd)
        for program in d:
            for option, key, value in d[program]:
                App.tool_arguments[program][option] = (value, key)
        print("Done")

    def enable_menu(self, menu, label):
        menu.entryconfig(label, state="normal")

    def disable_menu(self, menu, label):
        menu.entryconfig(label, state="disabled")

    def list_wifis(self, master=None, wifi_list=None):
        if master is None:
            master = self.root
        if wifi_list is None:
            wifi_list = self.viewed_list
            self.sort_wifi_list(wifi_list=wifi_list)
        if self.list_frame is not None:
            self.list_frame.destroy()
        if master.winfo_exists():
            self.list_frame = tk.Frame(master, bg=App.frame_bg, bd=1)
            self._list_wifis(master, self.list_frame, wifi_list, App.order)
            self.list_frame.pack(side='bottom', fill='both', expand=True)
            if len(wifi_list) >= 2:
                master.geometry("1361x672+0+0")
            else:
                master.geometry("928x100+0+0")

    def sort_wifi_list(self, option='power', wifi_list=None):
        if wifi_list is None:
            wifi_list = self.viewed_list
        def key_f(wifi):
            if option == 'power':
                if isinstance(wifi['power'], str):
                    return -300 - int(wifi['power'][1:])
                return wifi['power']
            else:
                return wifi[option]
        wifi_list.sort(key=key_f, reverse=True)

    def _list_wifis(self, master, list_frame, wifi_list, order):
        def get_value(wifi, key):
            if key == 'macs': # 'macs' is list
                return len((wifi[key] or [''])[0])
            else:
                return len(str(wifi[key]))
        max_lengths = {key: max(max([get_value(wifi, key) for wifi in wifi_list], default=0), len(key)) + 3 for key in order}
        # TODO: add 'sorting by' arrows
        canvas = tk.Canvas(list_frame, bd=0, bg=App.frame_bg)
        main_frame = tk.Frame(canvas, bg=App.frame_bg, bd=1)
        y_scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        x_scrollbar = tk.Scrollbar(list_frame, orient="horizontal", command=canvas.xview)
        canvas.configure(xscrollcommand=x_scrollbar.set,yscrollcommand=y_scrollbar.set)
        y_scrollbar.pack(side="right", fill="y")
        x_scrollbar.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=main_frame, anchor="center")
        def on_frame_configure(event, canvas=canvas):
            canvas.configure(scrollregion=canvas.bbox("all"))
        main_frame.bind("<Configure>", on_frame_configure)

        frame = tk.Frame(main_frame)
        for j, key in enumerate(order): # key labels
            label = tk.Label(
                master=frame,
                text=str(key).upper(),
                width=max_lengths[key],
                bg=App.wifi_key_label_bg,
                fg=App.wifi_key_label_fg,
                font=App.wifi_label_font
            )
            label.key = key
            label.reversed_sorting = False
            label.grid(row=0, column=j, sticky='we')
            # "sorting by" actions
            def sort_action(label): # TODO: move out from 'for' loop
                if self.sorting == label.key:
                    self.reversed_sorting = not self.reversed_sorting
                def key_f(wifi):
                    if label.key == 'power' and isinstance(wifi[label.key], str):
                        return -300 - int(wifi[label.key][1:])
                    return wifi[label.key]
                wifi_list.sort(key=key_f, reverse=self.reversed_sorting)
                list_frame.destroy()
                self.list_wifis(master, wifi_list=wifi_list)
                self.sorting = label.key
            label.bind('<Button-1>', lambda event: sort_action(event.widget), add='+')
        frame.grid(row=0, column=0)
        for i, wifi in enumerate(wifi_list): # wifi_labels
            frame = tk.Frame(main_frame)
            wifi = OrderedDict([(key, wifi[key]) for key in order])
            frame.wifi = wifi
            for j, key in enumerate(wifi.keys()):
                if key == 'macs':
                    value = str((wifi[key] or [''])[0])
                else:
                    value = str(wifi[key])
                label = tk.Label(
                    master=frame,
                    text=value,
                    width=max_lengths[key],
                    bg=App.wifi_label_bg,
                    fg=App.wifi_label_fg,
                    font=App.wifi_label_font
                )
                label.wifi = wifi
                label.grid(row=0, column=j, sticky='w')
                label.bind('<Button-1>', lambda event: self.select_action(event.widget.wifi), add='+')
            frame.bind('<Enter>', lambda event: self.enlight_childs(event.widget, 'in'), add='+')
            frame.bind('<Leave>', lambda event: self.enlight_childs(event.widget, 'out'), add='+')
            frame.grid(row=i+1, column=0)

    def enlight_childs(self, widget, where): # move in '_list_wifis'
        for child in widget.children.values():
            self.enlight(child, where)

    def enlight(self, widget, where): # move in '_list_wifis'
        if where == 'in':
            bg = App.wifi_enlighted_label_bg
            fg = App.wifi_enlighted_label_fg
        else:
            bg = App.wifi_label_bg
            fg = App.wifi_label_fg
        widget.config(bg=bg, fg=fg)

    def display_help(self, file=help_file):
        with file.open('r') as fd:
            text = fd.read()
        print(text)

    def select_action(self, wifi):
        master = tk.Toplevel()
        master.title("Actions with {essid}".format(**wifi))
        lockedwifi_icon = tk.PhotoImage(file=str(lib/"lockedwifi.png"), format='png')
        master.tk.call('wm', 'iconphoto', master._w, lockedwifi_icon)
        master.geometry("1500x400")
        menu = tk.Menu(master)
        # 'Tools' menu
        tool_menu = tk.Menu(menu)

        airodump_menu = tk.Menu(tool_menu)
        airodump_menu.add_command(label="Search clients (airodump-ng)", font=App.submenu_font, command=lambda: set_cmd_string("airodump-ng --search"))
        airodump_menu.add_command(label="Listen & write (airodump-ng)", font=App.submenu_font, command=lambda: set_cmd_string("airodump-ng --write"))
        tool_menu.add_cascade(label="airodump-ng", font=App.menu_font, menu=airodump_menu)

        reaver_menu = tk.Menu(tool_menu)
        reaver_menu.add_command(label="WPS Pixie Dust attack (reaver)", font=App.submenu_font, command=lambda: set_cmd_string("reaver --pixie"))
        reaver_menu.add_command(label="WPS brute force attack (reaver)", font=App.submenu_font, command=lambda: set_cmd_string("reaver --brute"))
        tool_menu.add_cascade(label="reaver", font=App.menu_font, menu=reaver_menu)

        aireplay_menu = tk.Menu(tool_menu)
        aireplay_menu.add_command(label="Deauth", font=App.submenu_font, command=lambda: set_cmd_string("aireplay-ng --deauth"))
        aireplay_menu.add_command(label="Fake auth", font=App.submenu_font, command=lambda: set_cmd_string("aireplay-ng --fakeauth"))
        aireplay_menu.add_command(label="ARP request", font=App.submenu_font, command=lambda: set_cmd_string("aireplay-ng --arp"))
        aireplay_menu.add_command(label="Injection test", font=App.submenu_font, command=lambda: set_cmd_string("aireplay-ng --inject"))
        tool_menu.add_cascade(label="aireplay-ng", font=App.menu_font, menu=aireplay_menu)

        aircrack_menu = tk.Menu(tool_menu)
        aircrack_menu.add_command(label="Crack PSK", font=App.submenu_font, command=lambda: set_cmd_string("aircrack-ng"))
        tool_menu.add_cascade(label="aircrack-ng", font=App.menu_font, menu=aircrack_menu)

        menu.add_cascade(label="Tools", font=App.menu_font, menu=tool_menu)
        # 'Request' menu
        request_menu = tk.Menu(menu)
        request_menu.add_command(label="Other...", font=App.submenu_font, command=lambda: self.request_other(wifi))
        request_menu.add_command(label="BSSID", font=App.submenu_font, command=lambda: self.request_option(wifi, 'bssid'))
        request_menu.add_command(label="ESSID", font=App.submenu_font, command=lambda: self.request_option(wifi, 'essid'))
        request_menu.add_command(label="Channel", font=App.submenu_font, command=lambda: self.request_option(wifi, 'channel'))
        request_menu.add_command(label="Power", font=App.submenu_font, command=lambda: self.request_option(wifi, 'power'))
        request_menu.add_command(label="WPS", font=App.submenu_font, command=lambda: self.request_option(wifi, 'wps'))
        request_menu.add_command(label="Authentication", font=App.submenu_font, command=lambda: self.request_option(wifi, 'auth'))
        request_menu.add_command(label="Speed", font=App.submenu_font, command=lambda: self.request_option(wifi, 'speed'))
        request_menu.add_command(label="MAC's", font=App.submenu_font, command=lambda: self.request_option(wifi, 'macs'))
        request_menu.add_command(label="WPS PIN", font=App.submenu_font, command=lambda: self.request_option(wifi, 'wps_pin'))
        request_menu.add_command(label="WPA PSK", font=App.submenu_font, command=lambda: self.request_option(wifi, 'wpa_psk'))
        request_menu.add_command(label="p1 index", font=App.submenu_font, command=lambda: self.request_option(wifi, 'p1_index'))
        request_menu.add_command(label="p2 index", font=App.submenu_font, command=lambda: self.request_option(wifi, 'p2_index'))
        request_menu.add_command(label="pixie dust crackable", font=App.submenu_font, command=lambda: self.request_option(wifi, 'pixie'))
        request_menu.add_command(label="note", font=App.submenu_font, command=lambda: self.request_option(wifi, 'note'))

        menu.add_cascade(label="Request", font=App.menu_font, menu=request_menu)
        # 'Help' menu
        menu.add_command(label="Help", font=App.menu_font, command=lambda: self.execute("{} --help".format(self.tool)))
        master.config(menu=menu)
        # default commands
        def get_mac(wifi, first=" -c "):
            if wifi['macs']:
                return first + wifi['macs'][0]
            else:
                return ''
        initial_commands = {
            "airodump-ng --search": lambda wifi: "airodump-ng {interface} --bssid {bssid} -c {channel} --showack --wps".format(interface=interface, **wifi),
            "airodump-ng --write": lambda wifi: "airodump-ng {interface} --bssid {bssid} -c {channel} -w lib/{essid}_output".format(interface=interface, **wifi),
            "reaver --pixie": lambda wifi: "reaver -i {interface} -b {bssid} -c {channel} -vvv -K 1 -f".format(interface=interface, **wifi),
            "reaver --brute": lambda wifi: "reaver -i {interface} -b {bssid} -c {channel} -vvv -S".format(interface=interface, **wifi),
            "aireplay-ng --deauth": lambda wifi: "aireplay-ng {interface} --deauth 10 -a {bssid}{mac}".format(interface=interface, bssid=wifi['bssid'], mac=get_mac(wifi)),
            "aireplay-ng --fakeauth": lambda wifi: "aireplay-ng {interface} --fakeauth 5 -a {bssid}{mac}".format(interface=interface, bssid=wifi['bssid'], mac=get_mac(wifi)),
            "aireplay-ng --arp": lambda wifi: "aireplay-ng {interface} --arpreplay -b {bssid}{mac}".format(interface=interface, bssid=wifi['bssid'], mac=get_mac(wifi, first=" -h ")),
            "aireplay-ng --inject": lambda wifi: "aireplay-ng {interface} --test -a {bssid}".format(interface=interface, **wifi),
            "aircrack-ng": lambda wifi: "aircrack-ng -b {bssid} <files>".format(**wifi)
        }

        # simple CLI
        cmd_frame = tk.Frame(master, bg='orange', bd=2)
        cmd_frame.grid(row=0, columnspan=20, sticky='we')
        cmd_frame.grid_columnconfigure(0, weight=1)
        cmd_string = tk.StringVar(master, value="Welcome!")
        def set_cmd_string(tool_name=None):
            cmd_string.set(initial_commands[tool_name](wifi))
            self.tool = cmd_string.get().split()[0]
            for x in master.grid_slaves(row=1):
                x.destroy()
            load_options(self.tool)
        def update_cmd_string(option, value, tool='reaver'):
            cmd_str = cmd_string.get()
            if isinstance(value, bool):
                if value:
                    cmd_string.set("{} {}{}".format(cmd_str, option, self.get_default_tool_argument(tool, option, wifi)))
                else:
                    start = cmd_str.index(' '+ option)
                    end = cmd_str.find(' -', start + 1)
                    if end != -1:
                        cmd_string.set(cmd_str[:start] + cmd_str[end:])
                    else:
                        cmd_string.set(cmd_str[:start])
        cmd_entry = tk.Entry(cmd_frame, textvariable=cmd_string, font=App.cmd_entry_font)
        cmd_entry.grid(sticky='we')
        cmd_entry.bind('<Return>', lambda event: self.execute(cmd_string.get()))
        cmd_entry.bind('<KeyPress>', lambda event: update_checkbuttons(), add='+')
        cmd_entry.focus()
        master.grid_columnconfigure(0, weight=1, pad=0)
        self.bool_options = []
        def load_options(tool='reaver'):
            n_columns = 10
            option_frame = tk.Frame(master)
            option_frame.grid(row=1, rowspan=5, sticky='we')
            option_frame.grid_columnconfigure(n_columns, weight=1, pad=0)
            checkbuttons = []
            options = App.tool_options[tool]
            self.bool_options = [tk.BooleanVar(master, value=opt in cmd_string.get()) for opt in options]
            description_frame = tk.Frame(option_frame)
            description_frame.grid(row=10, columnspan=10*n_columns, sticky='we')
            description_label = tk.Label(description_frame, text=self.get_description(tool, tool), font=App.description_label_font)
            description_label.pack()
            def update_description(event):
                description_label.config(text=self.get_description(options[checkbuttons.index(event.widget)], tool))
            for i in range(len(options)):
                option = options[i]
                checkbutton = tk.Checkbutton(option_frame, text=option, font=App.checkbutton_font, variable=self.bool_options[i], onvalue=True, offvalue=False)
                checkbutton.grid(row=i//n_columns+1, column=i%n_columns)
                checkbutton.bind('<Button-1>', lambda event: update_cmd_string(event.widget['text'], not self.bool_options[checkbuttons.index(event.widget)].get(), tool))
                checkbutton.bind('<Button-1>', update_description, add='+')
                checkbuttons.append(checkbutton)
            update_checkbuttons()
        def update_checkbuttons():
            for i in range(len(App.tool_options[self.tool])):
                self.bool_options[i].set((' ' + App.tool_options[self.tool][i]) in cmd_string.get())
        set_cmd_string(tool_name='reaver --pixie')
        master.bind('<Escape>', lambda event: master.destroy())
        master.mainloop()

    def get_default_tool_argument(self, program, option, wifi):
        value, key = App.tool_arguments[program][option]
        if key == 'mac':
            return value.format((wifi.get('macs', ['']) + [''])[0])
        else:
            return value.format(wifi.get(key, ''))

    def get_description(self, option, program='reaver', filename=None):
        """find and return from previously generated tmp/<program>_description.txt"""
        if filename is None:
            filename = "{}/{}_description.txt".format(tmp, program)
        with open(filename) as file:
            text = file.read()
        start = text.index('@'+option)+len(option)+2 # @<option>:\n<description>
        end = text.find("\n@", start)
        return text[start:end]

    def execute(sefl, cmd, hold_on=True):
        """execute command in new terminal"""
        # we want not exit terminal when `cmd` is done, so '&& cat' at the end
        cmd = cmd + " && cat" if hold_on else cmd
        print("Executed command: {}".format(cmd))
        system(f"gnome-terminal -- bash -c \"{cmd}\"")
        # system("exo-open --launch TerminalEmulator {}".format(cmd))

    def request_option(self, wifi, option):
        bssid = wifi['bssid']
        result = ''
        bssids = [wifi['bssid'] for wifi in self.wifi_list]
        if bssid in bssids:
            i = bssids.index(bssid)
            result = value2str(self.wifi_list[i], option)
        if self.wifi_database:
            db_bssids = [wifi['bssid'] for wifi in self.wifi_database]
            if bssid in db_bssids:
                i = db_bssids.index(bssid)
                db_result = value2str(self.wifi_database[i], option)
                if result == '' or len(db_result) > len(result):
                    result = db_result
        master = tk.Toplevel()
        request_string = tk.StringVar(master, value=str(result))
        frame = tk.Frame(master, bg=App.frame_bg, border=1)
        frame.grid(columnspan=20, sticky='we')
        frame.grid_columnconfigure(0, weight=1)
        request_label = tk.Label(frame, text=str(option) + ": ", font=App.request_label_font)
        request_label.grid(row=0, column=0)
        request_entry = tk.Entry(frame, textvariable=request_string, font=App.request_entry_font)
        request_entry.grid(row=0, column=1, columnspan=2, sticky='e')
        # request_entry.grid_columnconfigure(0, weight=1)
        request_entry.focus()
        def quit_and_write(wifi, option, value):
            master.destroy()
            self.write_option(wifi, option, value)
        request_entry.bind('<Return>', lambda event: quit_and_write(wifi, option, request_string.get()))
        def search_key(wifi, option):
            request_string.set(self.search_option(wifi, option))
        # buttons
        request_button = tk.Button(frame, text="Request", font=App.button_font, command=lambda: search_key(wifi, option))
        request_button.grid(row=1, column=0)
        write_button = tk.Button(frame, text="Save value", font=App.button_font, command=lambda: self.write_option(wifi, option, request_string.get()))
        write_button.grid(row=1, column=1)
        cancel_button = tk.Button(frame, text="Cancel", font=App.button_font, command=master.destroy)
        cancel_button.grid(row=2, column=0, columnspan=3)
        master.grid_columnconfigure(0, weight=1, pad=0)
        master.bind('<Escape>', lambda event: master.destroy())

    def request_other(self, wifi):
        bssid = wifi['bssid']
        master = tk.Toplevel()
        key_string = tk.StringVar(master, value='')
        request_string = tk.StringVar(master, value='')
        frame = tk.Frame(master, bg=App.frame_bg, border=1)
        frame.grid(columnspan=20, sticky='we')
        frame.grid_columnconfigure(0, weight=1)
        key_entry = tk.Entry(frame, textvariable=key_string, font=App.request_label_font)
        key_entry.grid(row=0, column=0)
        request_entry = tk.Entry(frame, textvariable=request_string, font=App.request_entry_font)
        request_entry.grid(row=0, column=1, columnspan=2, sticky='e')
        key_entry.focus()
        # request_entry.grid_columnconfigure(0, weight=1, pad=0)
        def search_key(wifi, option):
            request_string.set(self.search_option(wifi, option))
        def quit_and_write(wifi, option, value):
            master.destroy()
            self.write_option(wifi, option, value)
        key_entry.bind('<Return>', lambda event: search_key(wifi, key_string.get().strip()))
        request_entry.bind('<Return>', lambda event: quit_and_write(wifi, key_string.get().strip(), request_string.get().strip()))
        # buttons
        request_button = tk.Button(frame, text="Request", font=App.button_font, command=lambda: search_key(wifi, key_string.get().strip()))
        request_button.grid(row=1, column=0)
        write_button = tk.Button(frame, text="Save value", font=App.button_font, command=lambda: self.write_option(wifi, option, request_string.get()))
        write_button.grid(row=1, column=1)
        cancel_button = tk.Button(frame, text="Cancel", font=App.button_font, command=master.destroy)
        cancel_button.grid(row=2, column=0, columnspan=3)
        master.grid_columnconfigure(0, weight=1)
        master.bind('<Escape>', lambda event: master.destroy())

    def search_option(self, wifi, option):
        result = ''
        bssid = wifi['bssid']
        bssids = [wifi['bssid'] for wifi in self.wifi_list]
        if bssid in bssids:
            i = bssids.index(bssid)
            result = value2str(self.wifi_list[i], option)
        if self.wifi_database:
            db_bssids = [wifi['bssid'] for wifi in self.wifi_database]
            if bssid in db_bssids:
                i = db_bssids.index(bssid)
                db_result = value2str(self.wifi_database[i], option)
                if result == '' or len(db_result) > len(result):
                    result = db_result
        return result

    def write_option(self, wifi, option, s):
        bssid = wifi['bssid']
        bssids = [wifi['bssid'] for wifi in self.wifi_list]
        assert bssid in bssids, "Wi-Fi {} not found".format(wifi)
        i = bssids.index(bssid)
        value = str2value(s, option)
        self.wifi_list[i][option] = value
        if self.wifi_database:
            db_bssids = [wifi['bssid'] for wifi in self.wifi_database]
            if bssid in db_bssids:
                i = db_bssids.index(bssid)
                self.wifi_database[i][option] = value

    def start_thread(self, func, pargs=None, kwargs=None, interval=10, first_interval=5):
        self.enable_menu(self.scan_menu, "Stop updating")
        self.disable_menu(self.scan_menu, "Scan with airodump-ng")
        self.disable_menu(self.scan_menu, "Scan with wash")
        self.updating = threading.Thread(target=self.start_updating, kwargs={
            'func': func,
            'pargs': pargs,
            'kwargs': kwargs,
            'interval': interval,
            'first_interval': first_interval})
        self.updating.start()

    def stop_thread(self):
        self.stop_updating = True
        self.updating.join()
        self.disable_menu(self.scan_menu, "Stop updating")
        self.enable_menu(self.scan_menu, "Scan with airodump-ng")
        self.enable_menu(self.scan_menu, "Scan with wash")

    def start_updating(self, func, pargs=None, kwargs=None, interval=10, first_interval=5):
        if pargs is None:
            pargs = []
        if kwargs is None:
            kwargs = {}
        sleep(first_interval)
        t = time()
        self.stop_updating = False
        while not self.stop_updating:
            ct = time()
            if ct - t >= interval:
                t = ct
                func(*pargs, **kwargs)


    def start_airmodump_search(self, interval=1):
        f = tmp / "airo-01.csv"
        if f.exists():
            os.remove(f)
        self.execute(f"airodump-ng {interface} --wps --output-format csv --write {tmp}/airo --write-interval {interval}")
        self.enable_menu(self.scan_menu, "Update from airodump-ng")
        self.start_thread(func=self.update_from_airodump_list, kwargs={'relist': True})

    def load_airodump_list(self, prefix="airo"):
        assert (tmp / f"{prefix}-01.csv").exists(), "Scan first"
        L = []
        with open("{}/{}-01.csv".format(tmp, prefix), 'r') as file:
            lines = file.readlines()
        # order = [x.strip() for x in lines[1].split(',')
        for s in lines[2:]:
            ls = [x.strip() for x in s.split(',')]
            if len(ls) >= 13:
                if int(ls[8]) == -1:
                    power = -100
                else:
                    power = int(ls[8])
                wifi = {'bssid': ls[0], 'channel': int(ls[3]), 'auth': ls[5], 'speed': ls[4], 'power': power, 'essid': ls[13], 'wps': '', 'macs': []}
                L.append(wifi)
            elif len(ls) == 7 and len(ls[5]) == 17: # len(bssid) == 17
                li = list(filter(lambda i: L[i]['bssid'] == ls[5], range(len(L))))
                if len(li) == 1 and ls[0] not in L[li[0]]:
                    L[li[0]]['macs'].append(ls[0])
        return L

    def update_from_airodump_list(self, prefix="airo", relist=False):
        airodump_list = self.load_airodump_list(prefix=prefix)
        bssids = [wifi['bssid'] for wifi in self.wifi_list]
        for wifi in airodump_list:
            bssid = wifi['bssid']
            if bssid in bssids:
                i = bssids.index(bssid)
                for option in App.airodump_updatable_options:
                    if option == 'macs':
                        self.wifi_list[i][option] = list(set(self.wifi_list[i][option] + wifi[option]))
                    else:
                        self.wifi_list[i][option] = wifi[option]
            else:
                self.wifi_list.append(wifi)
        if relist:
            self.list_wifis()

    def start_wash_search(self):
        estimate_file.clear()
        self.execute(f"wash -i {interface} --all --out-file={estimate_file}")
        self.enable_menu(self.scan_menu, "Update from wash")
        self.start_thread(func=self.update_from_wash_list, kwargs={'relist': True})

    def load_wash_list(self, file=estimate_file):
        L = []
        with file.open('r') as fd:
            lines = fd.readlines()
        assert next(filter(lambda line: len(line.strip()) != 0, lines), None) != None, "Scan first"
        # order = lines[0].split()
        for i, s in enumerate(lines[2:]):
            ls = s.split("  ")
            if ls[-2] == 'No':
                wps = 'Open'
            elif ls[-2] == 'Yes':
                wps = 'Locked'
            elif ls[-2].strip() == '':
                wps = '-'
            else:
                wps = ''
            wifi = {'bssid': ls[0].strip(), 'channel': int(ls[1]), 'wps': wps, 'essid': ls[-1].strip(), 'power': '#'+str(i+1), 'auth': '', 'speed': '', 'macs': []}
            L.append(wifi)
        return L

    def update_from_wash_list(self, file=estimate_file, relist=False):
        wash_list = self.load_wash_list(file=file)
        bssids = [wifi['bssid'] for wifi in self.wifi_list]
        for wifi in wash_list:
            bssid = wifi['bssid']
            if bssid in bssids:
                i = bssids.index(bssid)
                for option in App.wash_updatable_options:
                    self.wifi_list[i][option] = wifi[option]
            else:
                self.wifi_list.append(wifi)
        if relist:
            self.list_wifis()

    def save_wifi_list(self, file=last_wifi_list_file):
        print("Saving Wi-Fi list...", end=' ')
        with file.open('wb') as fd:
            pickle.dump(self.wifi_list, fd)
        print("Done")

    def load_wifi_database(self, file=wifi_database_file):
        print("Loading Wi-Fi database...", end=' ')
        with file.open('rb') as fd:
            self.wifi_database = pickle.load(fd)
        self.enable_menu(self.wifi_database_menu, "Update from database")
        self.enable_menu(self.wifi_database_menu, "Update database")
        self.enable_menu(self.wifi_database_menu, "Import from .db")
        self.enable_menu(self.wifi_database_menu, "Import from .csv")
        self.enable_menu(self.wifi_database_menu, "Export to .db")
        self.enable_menu(self.wifi_database_menu, "Export to .csv")
        print("Done")

    def update_wifi_database(self, L=None, file=wifi_database_file):
        print("Updating Wi-Fi database...", end=' ')
        if L is None:
            L = self.wifi_list
        assert self.wifi_database, "wifi_database is not loaded"
        db_bssids = [wifi['bssid'] for wifi in self.wifi_database]
        for wifi in L:
            if wifi['bssid'] in db_bssids:
                i = db_bssids.index(wifi['bssid'])
                db_wifi = self.wifi_database[i]
                for option in wifi:
                    if option == 'macs':
                        self.wifi_database[i][option] = list(set(db_wifi[option] + wifi[option]))
                    elif len(value2str(wifi, option)) >= len(value2str(db_wifi, option)):
                        self.wifi_database[i][option] = wifi[option]
            else:
                self.wifi_database.append(wifi)
        with file.open('wb') as fd:
            pickle.dump(self.wifi_database, fd)
        print("Done")

    def update_from_wifi_database(self, relist=False):
        print("Updating Wi-Fi list from Wi-Fi database...", end=' ')
        assert self.wifi_database, "wifi_database is not loaded"
        db_bssids = [wifi['bssid'] for wifi in self.wifi_database]
        for j, wifi in enumerate(self.wifi_list):
            if wifi['bssid'] in db_bssids:
                i = db_bssids.index(wifi['bssid'])
                db_wifi = self.wifi_database[i]
                new_options = set(db_wifi.keys()) - set(wifi.keys())
                for option in chain(App.database_updatable_options, new_options):
                    if option == 'macs':
                        self.wifi_list[j][option] = list(set(self.wifi_list[j][option] + db_wifi[option]))
                    elif len(value2str(wifi, option)) < len(value2str(db_wifi, option)):
                        self.wifi_list[j][option] = db_wifi[option]
        if relist:
            self.list_wifis()
        print("Done")

    def set_wifi_list(self, L):
        self.wifi_list = L
        self.viewed_list = list(filter(self.filters, self.wifi_list))

    def load_wifi_list(self, file=None, relist=False):
        if file is None:
            file = Path(fd.askopenfilename(filetypes=(
                ("Pickled list", '*.pkl'),
                ("Database", '*.db'),
                ("Shelve database", '*.shelve.db'),
                ("CSV table", '*.csv'),
                ("All files", '*.*'))))
        filename = str(file)
        if filename.endswith('.pkl'):
            self.set_wifi_list(load_pkl(file))
        elif filename.endswith('.db') and 'shelve' in filename:
            self.set_wifi_list(load_shelf(Path(filename[:-3])))
        elif filename.endswith('.db'):
            self.set_wifi_list(load_db(Path(filename[:-3])))
        elif filename.endswith('.csv'):
            self.set_wifi_list(load_csv(file))
        else:
            raise TypeError("File '{}' can not be loaded: invalid extension '{}'".format(filename, filename.rsplit('.')[-1]))
        if relist:
            self.list_wifis()

    def load_last_wifi_list(self, file=last_wifi_list_file, relist=False):
        with file.open('rb') as fd:
            self.set_wifi_list(pickle.load(fd))
        if relist:
            self.list_wifis()
        self.enable_menu(self.file_menu, "Save")
        self.enable_menu(self.file_menu, "Save all")
        self.enable_menu(self.file_menu, "Save as...")

    def save_as_wifi_list(self, file=None):
        if file is None:
            file = Path(fd.asksaveasfilename(filetypes=(
                ("Pickled list", '*.pkl'),
                ("Database", '*.db'),
                ("Shelve database", '*.shelve.db'),
                ("CSV table", '*.csv'),
                ("All files", '*.*'))))
        filename = str(file)
        if filename.endswith('.pkl'):
            save_pkl(self.wifi_list, file)
        elif filename.endswith('.db') and 'shelve' in filename:
            save_shelf(self.wifi_list, Path(filename[:-3]))
        elif filename.endswith('.db'):
            save_db(self.wifi_list, Path(filename[:-3]))
        elif filename.endswith('.csv'):
            save_csv(self.wifi_list, file)
        else:
            raise TypeError("File '{}' can not be saved: invalid extension '{}'".format(filename, filename.rsplit('.')[-1]))

    def escape_and_save(self):
        if not self.wifi_database:
            self.load_wifi_database()
        self.root.destroy()
        self.update_wifi_database()
        self.save_wifi_list()
        print("Application closed")

    def save(self):
        if not self.wifi_database:
            self.load_wifi_database()
        self.update_wifi_database()
        self.save_wifi_list()

    def or_filters(self, f, relist=True):
        g = self.filters
        self.set_filters(lambda x: f(x) or g(x), relist=relist)

    def and_filters(self, f, relist=True):
        g = self.filters
        self.set_filters(lambda x: f(x) and g(x), relist=relist)

    def set_filters(self, f, relist=True):
        self.filters = f
        self.viewed_list = list(filter(self.filters, self.wifi_list))
        if relist:
            self.list_wifis()

    def reset_view(self, relist=True):
        self.viewed_list = self.wifi_list
        self.filters = lambda x: x
        # reset sorting
        if relist:
            self.list_wifis()

# format functions

def value2str(wifi, key):
    """wifi, key -> str(wifi[key])"""
    result = wifi.get(key, '')
    if isinstance(result, list):
        return ','.join(map(str, result))
    else:
        return str(result)

def str2value(s, option=None, sep=','):
    """str -> value"""
    s = s.strip()
    if option == 'macs':
        if len(s) != 17 and sep not in s:
            return []
        elif len(s) == 17:
            return [s]
        elif sep in s:
            return s.split(sep)
    if option == 'power' and s.isdigit():
        return int(s)
    else:
        return s

# import/export converters
# TODO: filename -> file
def export_pkl(L, filename=None):
    if filename is None:
        filename = fd.asksaveasfilename(filetypes=(("Pickled list", '*.pkl'), ("All files", '*.*')))
    save_pkl(L, Path(filename))

def save_pkl(L, file):
    with file.open('wb') as fd:
        pickle.dump(L, fd)

def import_pkl(filename=None):
    if filename is None:
        filename = fd.askopenfilename(filetypes=(("Pickled list", '*.pkl'), ("All files", '*.*')))
    return load_pkl(Path(filename))

def load_pkl(file):
    with file.open('rb') as fd:
        L = pickle.load(fd)
    return L

def export_db(L, filename=None):
    if filename is None:
        filename = fd.asksaveasfilename(filetypes=(("Database", '*.db'),))
        if filename.endswith('.db'):
            filename = filename[:-3]
    save_db(L, Path(filename))

def save_db(L, file):
    with dbm.open(str(file), 'c') as file:
        file['bssid'] = ';'.join(App.order)
        for wifi in L:
            if isinstance(wifi['bssid'], str):
                s = ';'.join(map(lambda key: value2str(wifi, key), App.order))
                other_keys = list(filter(lambda key: key not in App.order, wifi))
                if other_keys:
                    s += ';'
                    s += ';'.join(map(lambda key: "{}:{}".format(key, value2str(wifi, key)), other_keys))
                bssid = wifi['bssid']
                file[bssid] = s

def import_db(filename=None):
    if filename is None:
        filename = fd.askopenfilename(filetypes=(("Database", '*.db'),))
        if filename.endswith('.db'):
            filename = filename[:-3]
    return load_db(Path(filename))

def load_db(file):
    L = []
    with dbm.open(str(file), 'r') as file:
        for bssid in file:
            wifi = {}
            L = file[bssid].split(';')
            assert len(L) >= len(App.order), "too few values stored: {}".format(L)
            for key, i in enumerate(App.order):
                wifi[key] = str2value(L[i])
                del L[i]
            for s in filter(lambda s: ':' in s, L):
                key, rest = s.split(':', maxsplit=1)
                wifi[key] = str2value(rest)
            L.append(wifi)
    return L

def export_csv(L, filename=None):
    if filename is None:
        filename = fd.asksaveasfilename(filetypes=(("CSV table", '*.csv'),))
    save_csv(L, Path(filename))

def save_csv(L, file):
    def get_value(wifi, key):
        if key == 'macs':
            return ' '.join(wifi['macs'])
        else:
            return str(wifi[key])
    with file.open('w') as file:
        file.write('**' + ','.join(App.order) + '[,<key>:<value>,...]**\n')
        for wifi in L:
            s = ','.join([get_value(wifi, key) for key in App.order])
            if len(App.order) < len(wifi):
                s += ','
            s += ','.join(["{}:{}".format(key, str(wifi[key]).replace(',', ' ')) for key in wifi if key not in App.order]) + '\n'
            file.write(s)

def import_csv(filename=None):
    if filename is None:
        filename = fd.askopenfilename(filetypes=(("CSV table", '*.csv'),))
    return load_csv(Path(filename))

def load_csv(file):
    L = []
    with file.open('r') as file:
        for line in file:
            if line.startswith('**') and line.endswith('**'): # comment
                continue
            list_ = [x.strip() for x in line.split(',')]
            wifi = {key: str2value(list_.pop(0), key, sep=' ') for key in App.order}
            for x in list_: # rest (not in App.order)
                key, str_value = x.split(':', maxsplit=1)
                key, str_value = key.strip(), str_value.strip()
                wifi[key] = str2value(str_value, option=key, sep=' ')
            L.append(wifi)
    return L

def export_shelf(L, filename=None):
    if filename is None:
        filename = fd.asksaveasfilename(filetypes=(("Shelve database", '*.db'),))
        if filename.endswith('.db'):
            filename = filename[:-3]
    save_shelf(L, Path(filename))

def save_shelf(L, file):
    with shelve.open(str(file)) as shelf:
        for wifi in L:
            shelf[wifi['bssid']] = wifi

def import_shelf(filename=None):
    if filename is None:
        filename = fd.askopenfilename(filetypes=(("Shelve database", '*.db'),))
        if filename.endswith('.db'):
            filename = filename[:-3]
    return load_shelf(Path(filename))

def load_shelf(file):
    with shelve.open(str(file)) as shelf:
        L = list(shelf.values())
    return L

# simple API

def get_last_wifi_list(filename=str(last_wifi_list_file)):
    with open(filename, 'rb') as file:
        L = pickle.load(file)
    return L

def set_last_wifi_list(L, filename=str(last_wifi_list_file)):
    with open(filename, 'wb') as file:
        pickle.dump(L, file)

def get_wifi_database(filename=str(wifi_database_file)):
    return load_pkl(filename)

def set_wifi_database(db, file=wifi_database_file, __safe=True):
    if __safe:
        last_db = get_wifi_database()
        assert len(db) >= len(last_db), "attempt to reduce wifi_database rejected (safe mode)"
    save_pkl(db, file)

def get_initial_commands(file=initial_commands_file):
    return load_pkl(file)

def set_initial_commands(d, file=initial_commands_file, __safe=True):
    """{'<cmd name>': f :: wifi -> str, ...}"""
    if __safe:
        last_d = get_initial_commands()
        assert len(d) >= len(last_d), "attempt to reduce initial_commands rejected (safe mode)"
    save_pkl(d, file)

def get_default_arguments(file=default_tool_arguments_file):
    """syntax: {<program>: [([-, --]<option name>, <wifi_key or ''>, <formatting string>), ...], ...}"""
    return load_pkl(file)

def set_default_arguments(d, file=default_tool_arguments_file, __safe=True):
    """syntax: {<program>: [([-, --]<option name>, <wifi_key or ''>, <formatting string>), ...], ...}"""
    if __safe:
        last_dargs = get_default_arguments()
        assert len(d) >= len(last_dargs), "attempt to reduce default_arguments rejected (safe mode)"
    save_pkl(d, file)

def generate_cracked(dir_path, location='?', L=None):
    """create file per cracked wifi (default: in wifi_database)"""
    assert Path(dir_path).exists(), "invalid `dir_path`"
    L = L if L is not None else get_wifi_database()
    for wifi in L:
        if 'wpa_psk' in wifi:
            f = Path(dir_path) / + wifi['essid']
            pin = "\n{wps_pin}".format(**wifi) if 'wps_pin' in wifi else ''
            with f.open('w') as file:
                file.write("ESSID: {essid}\nWPA: {wpa_psk}{0}\nBSSID: {bssid}\npower ~ {power}\n{channel}\n\nLocation: {1}\n".format(pin, location, **wifi))

def add_wifi(wifi):
    """`wifi` == {'bssid': <'bssid'>[, 'essid': ...][, 'channel': ...][, 'wps': ...][, 'auth': ...][, 'power': ...][, 'macs': [<'mac1'>, ...][, ...]]}"""
    db = get_wifi_database()
    assert 'bssid' in wifi, "'bssid' not specified"
    if 'essid' not in wifi: wifi['essid'] = ''
    if 'channel' not in wifi: wifi['channel'] = -1
    if 'wps' not in wifi: wifi['wps'] = ''
    if 'auth' not in wifi: wifi['auth'] = ''
    if 'power' not in wifi: wifi['power'] = -100
    if 'macs' not in wifi: wifi['macs'] = []
    db.append(wifi)
    set_wifi_database(db)
    return wifi

if __name__ == '__main__':
    App()
