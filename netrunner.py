import socket
import configparser
import networkscan
import getmac
import requests
import urllib3
import gi
import time
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, Pango
from getmac import get_mac_address
from mac_vendor_lookup import MacLookup

# Declare ConfigParser, read the configuration file into memory
config = configparser.ConfigParser()
config.read('netrunner_config.ini')

# declare the pool manager for network requests
http = urllib3.PoolManager()

# set up the ping tool
NetIP_puller = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# getting the hostname of the local machine
myMachine = socket.gethostname()

# getting the LAN IP address of the local machine
myIPAddress = socket.gethostbyname(myMachine)

# getting the net IP address of the local machine
NetIP_puller.connect(("8.8.8.8", 80))
myNetIPAddress = str(NetIP_puller.getsockname()[0])
NetIP_puller.close

# getting the network interfaces of the local machine
myNetworkInterfaces = socket.if_nameindex()

class ListBoxDataRow(Gtk.ListBoxRow):
    def __init__(self, data):
        super().__init__()
        #self.data = data
        #self.add(Gtk.Label(label=data))

# Describe the main operations window
class OpsWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)

        # Main window properties
        self.set_default_size(830,570)
        self.set_border_width(5)
        self.set_modal(False)
        self.set_resizable(True)

        # HeaderBar properties
        self.HeaderBar = Gtk.HeaderBar()
        self.HeaderBar.set_show_close_button(True)
        self.HeaderBar.set_title(self.get_title())
        self.set_titlebar(self.HeaderBar)
        self.HeaderBar.show()

        # HeaderBar left side container - SysBar
        self.SysBar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.SysBar.show()

#       Setting up the main actions toolbar container
        self.MainActionsBar = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.MainActionsBar.show()

#       Setting up the button to open the local system's info popover
        self.btnSysInfo = Gtk.Button()
        icon = Gio.ThemedIcon(name="computer-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        image.show()
        self.btnSysInfo.add(image)
        self.btnSysInfo.set_size_request(35, -1)
        self.btnSysInfo.connect("clicked", self.task_SysInfo_clicked)
        self.btnSysInfo.show()

#       Placing the SysBar and its contents onto the HeaderBar
        self.SysBar.add(self.btnSysInfo)
        self.HeaderBar.pack_start(self.SysBar)

#       Describing a label with the local machine hostname, local and net IP addresses
        self.lblHostName = Gtk.Label()
        self.lblHostName.set_justify(Gtk.Justification.LEFT)
        self.lblHostName.set_markup(
            "<b>" + str(myMachine) + "</b>: \n" + 
            "Local IP: " + str(myIPAddress) + "\n" + 
            "Net IP: " + str(myNetIPAddress)
            )
        self.lblHostName.show()

#       Creating a popover to hold the local machine networki info
        self.LocalMachinePopover = Gtk.Popover()
        self.LocalMachinePopover.set_position(Gtk.PositionType.BOTTOM)
        self.LocalMachinePopover.set_border_width(5)
        self.LocalMachinePopover.add(self.lblHostName)

#       Setting up the main controlmode container
        self.OpsModesBar = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(self.OpsModesBar.get_style_context(), "linked")
        self.OpsModesBar.show()

#       Creating the button array to switch betwen operating modes
        self.btnOpsScan = Gtk.Button(label = "Scan")
        self.btnOpsScan.modify_bg(Gtk.StateType(0), Gdk.color_parse('#58482c'))
        self.btnOpsScan.modify_fg(Gtk.StateType(0), Gdk.color_parse('#d1c5c0'))
        self.btnOpsScan.connect("clicked", self.on_btnOpsScan_toggled)

        self.btnOpsMap = Gtk.Button(label = "Map")
        self.btnOpsMap.modify_bg(Gtk.StateType(0), Gdk.color_parse('#58482c'))
        self.btnOpsMap.modify_fg(Gtk.StateType(0), Gdk.color_parse('#d1c5c0'))
        self.btnOpsMap.connect("clicked", self.on_btnOpsMap_toggled)

        self.btnOpsRDP = Gtk.Button(label = "RDP")
        self.btnOpsRDP.modify_bg(Gtk.StateType(0), Gdk.color_parse('#58482c'))
        self.btnOpsRDP.modify_fg(Gtk.StateType(0), Gdk.color_parse('#d1c5c0'))
        self.btnOpsRDP.connect("clicked", self.on_btnOpsRDP_toggled)

        self.btnOpsTests = Gtk.Button(label = "Tests")
        self.btnOpsTests.modify_bg(Gtk.StateType(0), Gdk.color_parse('#58482c'))
        self.btnOpsTests.modify_fg(Gtk.StateType(0), Gdk.color_parse('#d1c5c0'))
        self.btnOpsTests.connect("clicked", self.on_btnOpsTests_toggled)
        
#       Placing OpsModesBar and all its buttons on the HeaderBar
        self.OpsModesBar.add(self.btnOpsScan)
        self.OpsModesBar.add(self.btnOpsMap)
        self.OpsModesBar.add(self.btnOpsRDP)
        self.OpsModesBar.add(self.btnOpsTests)
        self.HeaderBar.pack_start(self.OpsModesBar)

        # Setting up HeaderBar right side container - ControlBar
        self.ControlBar = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.ControlBar.show()

#       Creating a drop-down menu with interface names in it:

        # Setting up the ListStore to hold the data from the interfaces list
        IntList_store = Gtk.ListStore(int,str)
        
        # Parsing the interfaces string to the list and printing every list item in the terminal
        for IntData in myNetworkInterfaces: 
            IntList_store.append(IntData)
            print(IntData)
        
        # Creating a ComboBox instance
        self.InterfaceSelector = Gtk.ComboBox.new_with_model_and_entry(IntList_store)

        # Calling the text renderer to write the values into the ComboBox as text
        renderer_interfaces = Gtk.CellRendererText()

        # Starting the ComboBox instance
        self.InterfaceSelector.pack_start(renderer_interfaces, True)

        # Forcing the second column to be rendered in the ComboBox
        self.InterfaceSelector.set_entry_text_column(1)

        # Adding the column that will sort the values
        self.InterfaceSelector.add_attribute(renderer_interfaces, "text", 0)

        # Showing the result on the form
        self.InterfaceSelector.show()

        # Adding elements to ControlBar
        self.ControlBar.add(self.InterfaceSelector)
        self.HeaderBar.pack_end(self.ControlBar)

        # Adding the main window container
        self.MainContainer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.MainContainer)
        self.MainContainer.show()

#       Describing the welcome screen container
        self.Welcome_Screen = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.Welcome_Screen.set_border_width(35)
                
        # Creating elements for the Welcome screen
        self.lblWelcome = Gtk.Label()
        self.lblWelcome.set_markup(
            "<big>Netrunner</big>\n" +
            "Network device config monitoring tool"
        )
        self.Welcome_Screen.add(self.lblWelcome)

        self.chkWelcome = Gtk.CheckButton(label = "Show welcome screen at startup")
        self.chkWelcome.connect("toggled", self.on_chkWelcome_toggled)
        self.Welcome_Screen.add(self.chkWelcome)

#       Describing the Scan screen container and toolbar
        self.Scan_Screen = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing = 5)
        self.Scan_Screen_Toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.Scan_Screen.pack_start(self.Scan_Screen_Toolbar, True, True, 0)
        self.Scan_Screen_Toolbar.show()

        # Creating elements for the Scan screen toolbar
        self.btnScan_network = Gtk.Button(label = "Scan the network")
        self.btnScan_network.connect("clicked", self.on_btnScan_network_clicked)
        self.Scan_Screen_Toolbar.add(self.btnScan_network)

        self.LAN_IP_List = Gtk.ListBox()
        self.LAN_IP_List.set_selection_mode(Gtk.SelectionMode.NONE)
        self.Scan_Screen.add(self.LAN_IP_List)

#       Describing the screen load sequence
        config.read('netrunner-config.ini')
        Config_welcome = str(config.get('STARTUP', 'welcome_screen'))
        Config_screen = int(config.get('STARTUP', 'active_tab'))
        if Config_welcome == 'True':
            print("Welcome screen is enabled")
            self.chkWelcome.set_active(True)
            self.MainContainer.add(self.Welcome_Screen)
            self.Welcome_Screen.show()

        if Config_welcome == 'False':
            print("Welcome screen is disabled")
            self.Welcome_Screen.hide()
            if Config_screen == 1:
                self.MainContainer.add(self.Scan_Screen)
                self.Scan_Screen.show()
                self.btnOpsScan.modify_bg(Gtk.StateType(0), Gdk.color_parse('#fcec0c'))
                self.btnOpsScan.modify_fg(Gtk.StateType(0), Gdk.color_parse('#000000'))

#   Operating the local machine info button
    def task_SysInfo_clicked(self, btnSysInfo):
        self.LocalMachinePopover.set_relative_to(btnSysInfo)
        self.LocalMachinePopover.show_all()
        self.LocalMachinePopover.popup()

#   Operating the Show welcome screen at startup checkbox
    def on_chkWelcome_toggled(self, chkWelcome):
        config.read('netrunner-config.ini')
        Config_welcome = bool(config.get('STARTUP', 'welcome_screen'))
        if self.chkWelcome.get_active():
            config.set('STARTUP', 'welcome_screen', 'False')
            with open('netrunner-config.ini', 'w') as config_file:
                config.write(config_file)
        
#   Operating the Scan toggle button
    def on_btnOpsScan_toggled(self, btnOpsScan):
        self.btnOpsScan.modify_bg(Gtk.StateType(0), Gdk.color_parse('#fcec0c'))
        self.btnOpsScan.modify_fg(Gtk.StateType(0), Gdk.color_parse('#000000'))
        self.btnOpsMap.modify_bg(Gtk.StateType(0), Gdk.color_parse('#58482c'))
        self.btnOpsMap.modify_fg(Gtk.StateType(0), Gdk.color_parse('#d1c5c0'))
        self.btnOpsRDP.modify_bg(Gtk.StateType(0), Gdk.color_parse('#58482c'))
        self.btnOpsRDP.modify_fg(Gtk.StateType(0), Gdk.color_parse('#d1c5c0'))
        self.btnOpsTests.modify_bg(Gtk.StateType(0), Gdk.color_parse('#58482c'))
        self.btnOpsTests.modify_fg(Gtk.StateType(0), Gdk.color_parse('#d1c5c0'))

        # show the container with controls:
        self.MainContainer.add(self.Scan_Screen)
        self.Scan_Screen.show()

        # write the active tab number into config to open at next startup:
        config.read('netrunner-config.ini')
        config.set('STARTUP', 'active_tab', '1')
        with open('netrunner-config.ini', 'w') as config_file:
            config.write(config_file)

#   Operating the Map toggle button
    def on_btnOpsMap_toggled(self, btnOpsMap):
        self.btnOpsScan.modify_bg(Gtk.StateType(0), Gdk.color_parse('#58482c'))
        self.btnOpsScan.modify_fg(Gtk.StateType(0), Gdk.color_parse('#d1c5c0'))
        self.btnOpsMap.modify_bg(Gtk.StateType(0), Gdk.color_parse('#fcec0c'))
        self.btnOpsMap.modify_fg(Gtk.StateType(0), Gdk.color_parse('#000000'))
        self.btnOpsRDP.modify_bg(Gtk.StateType(0), Gdk.color_parse('#58482c'))
        self.btnOpsRDP.modify_fg(Gtk.StateType(0), Gdk.color_parse('#d1c5c0'))
        self.btnOpsTests.modify_bg(Gtk.StateType(0), Gdk.color_parse('#58482c'))
        self.btnOpsTests.modify_fg(Gtk.StateType(0), Gdk.color_parse('#d1c5c0'))

        config.read('netrunner-config.ini')
        config.set('STARTUP', 'active_tab', '2')
        with open('netrunner-config.ini', 'w') as config_file:
            config.write(config_file)
        
#   Operating the RDP toggle button
    def on_btnOpsRDP_toggled(self, btnOpsRDP):
        self.btnOpsRDP.modify_bg(Gtk.StateType(0), Gdk.color_parse('#fcec0c'))
        self.btnOpsRDP.modify_fg(Gtk.StateType(0), Gdk.color_parse('#000000'))
        self.btnOpsScan.modify_bg(Gtk.StateType(0), Gdk.color_parse('#58482c'))
        self.btnOpsScan.modify_fg(Gtk.StateType(0), Gdk.color_parse('#d1c5c0'))
        self.btnOpsMap.modify_bg(Gtk.StateType(0), Gdk.color_parse('#58482c'))
        self.btnOpsMap.modify_fg(Gtk.StateType(0), Gdk.color_parse('#d1c5c0'))
        self.btnOpsTests.modify_bg(Gtk.StateType(0), Gdk.color_parse('#58482c'))
        self.btnOpsTests.modify_fg(Gtk.StateType(0), Gdk.color_parse('#d1c5c0'))

        config.read('netrunner-config.ini')
        config.set('STARTUP', 'active_tab', '3')
        with open('netrunner-config.ini', 'w') as config_file:
            config.write(config_file)

#   Operating the Tests toggle button
    def on_btnOpsTests_toggled(self, btnOpsTests):
        self.btnOpsTests.modify_bg(Gtk.StateType(0), Gdk.color_parse('#fcec0c'))
        self.btnOpsTests.modify_fg(Gtk.StateType(0), Gdk.color_parse('#000000'))
        self.btnOpsScan.modify_bg(Gtk.StateType(0), Gdk.color_parse('#58482c'))
        self.btnOpsScan.modify_fg(Gtk.StateType(0), Gdk.color_parse('#d1c5c0'))
        self.btnOpsMap.modify_bg(Gtk.StateType(0), Gdk.color_parse('#58482c'))
        self.btnOpsMap.modify_fg(Gtk.StateType(0), Gdk.color_parse('#d1c5c0'))
        self.btnOpsRDP.modify_bg(Gtk.StateType(0), Gdk.color_parse('#58482c'))
        self.btnOpsRDP.modify_fg(Gtk.StateType(0), Gdk.color_parse('#d1c5c0'))

        config.read('netrunner-config.ini')
        config.set('STARTUP', 'active_tab', '4')
        with open('netrunner-config.ini', 'w') as config_file:
            config.write(config_file)

#       Operating the Scan_network button
    def on_btnScan_network_clicked(self, btnScan_network):
        local_network = "192.168.1.0/24"
        vendor_check_url = "https://api.macvendors.com/%s"
        lan_scan = networkscan.Networkscan(local_network)
        NetworkAddressStorage = Gtk.ListStore(str, str, str, str)
        lan_scan.run()
        for active_found_IP in lan_scan.list_of_hosts_found:
            FQDN_Test = socket.getfqdn(active_found_IP)
            if FQDN_Test == active_found_IP:
                FQDN_Test = "-"
            if active_found_IP == myNetIPAddress:
                Current_mac_address = str(get_mac_address(hostname = "localhost"))
            else:
                Current_mac_address = str(get_mac_address(ip = active_found_IP))
            Vendor_name = requests.get(url=str(vendor_check_url) %Current_mac_address)
            IPListIter = NetworkAddressStorage.append([str(active_found_IP), 
										            str(FQDN_Test),
										            str(Current_mac_address),
                                                    str(Vendor_name.text)])
            print(active_found_IP + " :: " + FQDN_Test + " :: " + Current_mac_address + " :: Getting vendor info...")
            time.sleep(10)
        IP_Scan_Tree = Gtk.TreeView(model = NetworkAddressStorage)
        renderer = Gtk.CellRendererText()
        for i, column_title in enumerate(
        ["IP Address", "FQDN", "MAC Address", "Device vendor"]
        ):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            IP_Scan_Tree.append_column(column)
        self.Scan_Screen.pack_end(IP_Scan_Tree, True, True, 0)
        IP_Scan_Tree.show()
        self.btnScan_network.set_sensitive(False)

window = OpsWindow()
window.connect("delete-event", Gtk.main_quit)
window.show_all()
Gtk.main()