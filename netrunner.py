import socket
import configparser
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, Pango

# Declare ConfigParser, read the configuration file into memory
config = configparser.ConfigParser()
config.read('netrunner_config.ini')

# getting the hostname of the local machine
myMachine = socket.gethostname()

# getting the IP address of the local machine
myIPAddress = socket.gethostbyname(myMachine)

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

        self.SysBar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.SysBar.show()

        # Describing a label with the local machine hostname
        self.lblHostName = Gtk.Label()
        self.lblHostName.set_justify(Gtk.Justification.LEFT)
        self.lblHostName.set_text(str(myMachine))
        self.lblHostName.show()

        # Describing a label with the local machine IP address
        self.lblIP = Gtk.Label()
        self.lblIP.set_justify(Gtk.Justification.LEFT)
        self.lblIP.set_text(str(myIPAddress))
        self.lblIP.show()

        # Adding labels to SysBar
        self.SysBar.add(self.lblHostName)
        self.SysBar.add(self.lblIP)
        self.HeaderBar.pack_start(self.SysBar)

        # Adding the main window container
        self.MainContainer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.MainContainer)
        self.MainContainer.show()

window = OpsWindow()
window.connect("delete-event", Gtk.main_quit)
window.show_all()
Gtk.main()