from datetime import datetime
import sys

def generate_datecoded_filename(prefix, extension):
    """
    Please make sure that you simply include the extension type without the dot.

    eg. wav should just be generate_datecoded_filename(prefix,wav) and not generate_datecoded_filename(prefix,.wav).
    """
    datecode = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"data/{prefix}_{datecode}.{extension}"



def clear_input_buffer():
    if sys.platform == "win32":
        # For Windows
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    else:
        import termios
        # For MacOS and Linux
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)