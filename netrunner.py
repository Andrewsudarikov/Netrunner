import socket
import configparser
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, Pango

# Declare ConfigParser, read the configuration file into memory
config = configparser.ConfigParser()
config.read('netrunner_config.ini')

# set up the ping tool
pinger = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# getting the hostname of the local machine
myMachine = socket.gethostname()

# getting the LAN IP address of the local machine
myIPAddress = socket.gethostbyname(myMachine)

# getting the net IP address of the local machine
pinger.connect(("8.8.8.8", 80))
myNetIPAddress = str(pinger.getsockname()[0])
pinger.close

# getting the network interfaces of the local machine
myNetworkInterfaces = socket.if_nameindex()

print(myNetworkInterfaces)

# Describe the main operations window
class OpsWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Netrunner")

        # Main window properties
        self.set_default_size(630,470)
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
        self.SysBar.set_border_width(3)
        self.SysBar.show()

        # Describing a label with the local machine hostname, local and net IP addresses
        self.lblHostName = Gtk.Label()
        self.lblHostName.set_justify(Gtk.Justification.LEFT)
        self.lblHostName.set_markup(
            "<b>" + str(myMachine) + "</b>: \n" + 
            "Local IP: " + str(myIPAddress) + "\n" + 
            "Net IP: " + str(myNetIPAddress)
            )
        self.lblHostName.show()

        # Adding labels to SysBar
        self.SysBar.add(self.lblHostName)
        self.HeaderBar.pack_start(self.SysBar)

        # HeaderBar right side container - ControlBar
        self.ControlBar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.ControlBar.set_border_width(5)
        self.ControlBar.show()

        # Creating a drop-down menu with interface names in it:

        # Setting up the ListStore to hold the data from the interfaces list
        IntList_store = Gtk.ListStore(int,str)
        
        # Parsing the interfaces string into the list and printing every list items into the terminal
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

window = OpsWindow()
window.connect("delete-event", Gtk.main_quit)
window.show_all()
Gtk.main()