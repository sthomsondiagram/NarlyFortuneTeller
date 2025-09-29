import os
import subprocess

def _print_via_escpos(text: str):
    from escpos.printer import Usb
    vendor = int(os.getenv("ESCPOS_USB_VENDOR_ID", "0"), 16)
    product = int(os.getenv("ESCPOS_USB_PRODUCT_ID", "0"), 16)
    in_ep = int(os.getenv("ESCPOS_IN_EP", "0"), 16) if os.getenv("ESCPOS_IN_EP") else None
    out_ep = int(os.getenv("ESCPOS_OUT_EP", "0"), 16) if os.getenv("ESCPOS_OUT_EP") else None

    p = Usb(vendor, product, in_ep=in_ep, out_ep=out_ep, timeout=0)
    p.set(align="center", width=1, height=1)
    for line in text.split("\n"):
        p.text(line + "\n")
    p.cut()

def _print_via_os(text: str):
    printer = os.getenv("PRINTER_NAME", "")
    proc = subprocess.Popen(["lpr"] + (["-P", printer] if printer else []),
                            stdin=subprocess.PIPE)
    proc.communicate(input=text.encode("utf-8"))

def print_ticket(text: str):
    if os.getenv("ESCPOS_USB_VENDOR_ID"):
        _print_via_escpos(text)
    else:
        _print_via_os(text)
