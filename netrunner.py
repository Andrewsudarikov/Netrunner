import socket
import configparser
import multiprocessing
import subprocess
import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, Pango

# Declare ConfigParser, read the configuration file into memory
config = configparser.ConfigParser()
config.read('netrunner_config.ini')

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

#   Operating the local machine info button
    def task_SysInfo_clicked(self, btnSysInfo):
        self.LocalMachinePopover.set_relative_to(btnSysInfo)
        self.LocalMachinePopover.show_all()
        self.LocalMachinePopover.popup()

#   Operating the Scan toggle button
    def on_btnOpsScan_toggled(self, btnOpsScan):
        self.btnOpsScan.modify_bg(Gtk.StateType(0), Gdk.color_parse('#fcec0c'))
        self.btnOpsScan.modify_fg(Gtk.StateType(0), Gdk.color_parse('#000000'))
        self.btnOpsMap.modify_bg(Gtk.StateType(0), Gdk.color_parse('#58482c'))
        self.btnOpsRDP.modify_bg(Gtk.StateType(0), Gdk.color_parse('#58482c'))
        self.btnOpsTests.modify_bg(Gtk.StateType(0), Gdk.color_parse('#58482c'))

#   Operating the Map toggle button
    def on_btnOpsMap_toggled(self, btnOpsMap):
        self.btnOpsMap.modify_bg(Gtk.StateType(0), Gdk.gdk.color_parse('#fcec0c'))
        
#   Operating the RDP toggle button
    def on_btnOpsRDP_toggled(self, btnOpsRDP):
        self.btnOpsRDP.modify_bg(Gtk.StateType(0), Gdk.color_parse('#fcec0c'))

#   Operating the Tests toggle button
    def on_btnOpsTests_toggled(self, btnOpsTests):
        self.btnOpsTests.modify_bg(Gtk.StateType(0), Gdk.color_parse('#fcec0c'))

    def pinger(job_q, results_q):
        DEVNULL = open(os.devnull, 'w')
        while True:

            myIPAddress = job_q.get()

            if myIPAddress is None:
                break

            try:
                subprocess.check_call(['ping', '-c1', myIPAddress],
                                    stdout=DEVNULL)
                results_q.put(myNetIPAddress)
            except:
                pass

    def task_network_mapper(pool_size=128):
        
        # Create the container to hold IP addresses
        IP_list = list()

        # get local machine's IP and compose a base like 192.168.1.xxx
        IP_parts = myIPAddress.split(".")
        base_IP = IP_parts[0] + "." + IP_parts[1] + "." + IP_parts[2] +"."

        # Describing the jobs quu and the results stack (same thing, actually)
        JobsQueue = multiprocessing.Queue()
        ResultsStack = multiprocessing.Queue()

        # Describing the jobs pool structure and process
        pool = [multiprocessing.Process(target=pinger, args=(JobsQueue, ResultsStack)) for i in range(pool_size)]

        for GO in pool:
            GO.start()

window = OpsWindow()
window.connect("delete-event", Gtk.main_quit)
window.show_all()
Gtk.main()