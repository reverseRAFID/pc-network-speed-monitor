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

app = None  
def get_network_speed():
    pythoncom.CoInitialize()  
    w = wmi.WMI()
    try:

        # place the index number of the interface(Ethernet/WiFi) that you want to monitor 
        network_interface = w.Win32_PerfFormattedData_Tcpip_NetworkInterface()[1]

        tx_bytes = int(network_interface.BytesSentPersec)
        rx_bytes = int(network_interface.BytesReceivedPersec)
        tx_speed_mbps = tx_bytes * 8 / 1_000_000
        rx_speed_mbps = rx_bytes * 8 / 1_000_000

    finally:
        pythoncom.CoUninitialize()

    return tx_speed_mbps, rx_speed_mbps

def send_data(ser, data_type, data):
    data_str = f"{data:.2f}"
    ser.write(data_type.encode('utf-8'))
    ser.write(bytearray(data_str, 'utf-8'))
    ser.write('\n'.encode('utf-8'))

def on_quit(event):
    app.ExitMainLoop()

def create_system_tray_icon():
    global app 
    app = wx.App(False) 
    frame = wx.Frame(None)
    icon_image = Image.open("D:/Network screen/cool.jpg") #place your desired image here
    icon_image = icon_image.convert("RGBA")
    icon_bitmap = wx.Bitmap.FromBufferRGBA(icon_image.width, icon_image.height, icon_image.tobytes())
    icon = wx.adv.TaskBarIcon()
    icon.SetIcon(wx.Icon(wx.Bitmap(icon_bitmap)))
    icon.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, on_right_click) 
    icon.Bind(wx.adv.EVT_TASKBAR_RIGHT_DOWN, on_right_click)
    app.MainLoop()

def on_left_click(event):
    pass

def on_right_click(event):
    menu = wx.Menu()
    menu.Append(wx.ID_EXIT, "Quit")
    icon = event.GetEventObject()
    icon.Bind(wx.EVT_MENU, on_quit, id=wx.ID_EXIT)
    icon.PopupMenu(menu)
    menu.Destroy()

def main():
    ser = serial.Serial(arduino_port, 9600) 
    time.sleep(0.5)

    while True:
        tx_speed_mbps, rx_speed_mbps = get_network_speed()

        send_data(ser, 'T', tx_speed_mbps)
        send_data(ser, 'R', rx_speed_mbps)

        time.sleep(0.25)

if __name__ == "__main__":

    main_loop_thread = threading.Thread(target=main)
    main_loop_thread.daemon = True
    main_loop_thread.start()
    
    create_system_tray_icon()
