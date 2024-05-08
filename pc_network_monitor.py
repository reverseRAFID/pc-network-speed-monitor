import serial
import time
import wmi
import wx.adv
import wx
import threading
import pythoncom
from PIL import Image
import serial.tools.list_ports
ports = serial.tools.list_ports.comports()

arduino_port = ""
for port, desc, hwid in sorted(ports):
    if "CH340" in desc:
        arduino_port = port
        break

app = None  # Global variable to store the wx.App instance
def get_network_speed():
    pythoncom.CoInitialize()  # Initialize the COM library (required for WMI in a thread)
    # Connect to the WMI service
    w = wmi.WMI()
    try:

        # Get the default network interface
        network_interface = w.Win32_PerfFormattedData_Tcpip_NetworkInterface()[1]

        # Extract the bytes sent and received as integers
        tx_bytes = int(network_interface.BytesSentPersec)
        rx_bytes = int(network_interface.BytesReceivedPersec)

        # Calculate the speed in Mbps (1 byte = 8 bits, 1 Mbps = 1,000,000 bits)
        tx_speed_mbps = tx_bytes * 8 / 1_000_000
        rx_speed_mbps = rx_bytes * 8 / 1_000_000

    finally:
        pythoncom.CoUninitialize()  # Uninitialize the COM library

    return tx_speed_mbps, rx_speed_mbps

def send_data(ser, data_type, data):
    data_str = f"{data:.2f}"  # Convert data to string with 2 decimal places
    ser.write(data_type.encode('utf-8'))
    ser.write(bytearray(data_str, 'utf-8'))
    ser.write('\n'.encode('utf-8'))

def on_quit(event):
    app.ExitMainLoop()

def create_system_tray_icon():
    global app  # Access the global 'app' variable
    app = wx.App(False)  # Create a new wx.App instance
    frame = wx.Frame(None)
    icon_image = Image.open("D:/Network screen/cool.jpg")
    icon_image = icon_image.convert("RGBA")
    icon_bitmap = wx.Bitmap.FromBufferRGBA(icon_image.width, icon_image.height, icon_image.tobytes())
    icon = wx.adv.TaskBarIcon()
    icon.SetIcon(wx.Icon(wx.Bitmap(icon_bitmap)))
    icon.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, on_right_click)  # Change on_left_click to on_right_click
    icon.Bind(wx.adv.EVT_TASKBAR_RIGHT_DOWN, on_right_click)
    app.MainLoop()

def on_left_click(event):
    #print("Left clicked on the system tray icon")
    pass

def on_right_click(event):
    menu = wx.Menu()
    menu.Append(wx.ID_EXIT, "Quit")
    icon = event.GetEventObject()
    icon.Bind(wx.EVT_MENU, on_quit, id=wx.ID_EXIT)
    icon.PopupMenu(menu)
    menu.Destroy()

def main():
    ser = serial.Serial(arduino_port, 9600)  # Change 'COM8' to your Arduino's serial port
    time.sleep(0.5)  # Allow time for the Arduino to initialize

    while True:
        tx_speed_mbps, rx_speed_mbps = get_network_speed()
        #print(f"Tx Speed: {tx_speed_mbps} Mbps, Rx Speed: {rx_speed_mbps} Mbps")

        # Send the speed data to Arduino separately with their identifiers
        send_data(ser, 'T', tx_speed_mbps)  # 'T' indicates Tx speed
        send_data(ser, 'R', rx_speed_mbps)  # 'R' indicates Rx speed

        # Delay between updates (adjust as needed)
        time.sleep(0.25)

if __name__ == "__main__":
    # Start the main loop in the background
    main_loop_thread = threading.Thread(target=main)
    main_loop_thread.daemon = True
    main_loop_thread.start()

    # Create the system tray icon and start the event loop
    create_system_tray_icon()
