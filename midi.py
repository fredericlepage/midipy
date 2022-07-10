import mido
import time

class color:
   PURPLE = '\033[95m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

DEVICE = "CASIO USB-MIDI:CASIO USB-MIDI MIDI 1 20:0"

track_list = {}      # Dictionary containing {track_name : recorded midi log}

def record(track):
    in_port = mido.open_input(DEVICE)

    midi_log = []
    event_time = time.time()

    print("[*] Recording '" + track + "'")
    print("Press CTRL + C to end recording")
    try:
        for msg in in_port:
            prev_time = event_time
            event_time = time.time()
            event = [event_time - prev_time, msg]
            midi_log.append(event)
            #print(event)       # Uncomment to print midi events as they are being recorded
    except KeyboardInterrupt:
        midi_log[0][0] = 0      # Set time delay of first midi event as 0 seconds
        track_list[track] = midi_log  # Add the midi log to the track_list dictionary
        print("\n[*] Finished recording '" + track + "'\n")

def play(track):
    out_port = mido.open_output(DEVICE)

    midi_log = track_list[track]

    print("[*] Playing '" + track + "'")
    for event in midi_log:
        time_delay = event[0]
        midi_msg = event[1]
        time.sleep(time_delay)
        out_port.send(midi_msg)
    print("[*] Finished playing '" + track + "'\n")

def list_devices():
    dev_names = mido.get_input_names()
    if len(dev_names) == 0:
        print("No midi device available")
    else:
        print(color.UNDERLINE + "Midi device list" + color.END)
        for i in range(len(dev_names)):
            if dev_names[i] == DEVICE:
                print(color.PURPLE + str(i + 1) + ": " + dev_names[i] + " (Currently selected)" + color.END )
            else:
                print(str(i + 1) + ": " + dev_names[i])
        print("")

def list_tracks():
    if track_list:
        print(color.UNDERLINE + "Track list" + color.END)
        for key in track_list.keys():
            print("  - " + str(key))
        print("")
    else:
        print("No tracks have been recorded yet.")
        print("Use 'rec [track_name]' to record one.")

def kill_notes():
    """Sends an off signal to all notes on midi device"""
    out_port = mido.open_output(DEVICE)

    for i in range(1,128):
        msg = mido.Message('note_off', note=i)
        out_port.send(msg)

def select_device(dev_name):
    global DEVICE
    dev_list = mido.get_input_names()

    if len(dev_name) == 1 and dev_name.isdigit():
        try:
            DEVICE = dev_list[int(dev_name)-1]
        except IndexError:
            print("[!] Select a device number between 1 and " + len(dev_list))

    else:
        DEVICE = dev_name
        if dev_name not in dev_list:
            print("[!] Warning: device '" + dev_name + "' is not detected.")

def print_help():
        print("""List of commands:
        rec [track_name]            - record a midi log from midi input
        play [track_name]           - play a recorded track
        list [object]               - list tracks or midi devices ('list help' for more info)
        sel [midi_device]           - select a midi device
        del [track_name]            - delete a recorded midi log
        kill                        - kill all notes on the midi device
        exit                        - exit the program
        help                        - print this help message
        """)

def lexer(u_input):
    tokens = []
    token = ""
    is_string = False
    for char in u_input.rstrip():
        if char == '"' or char == "'":
            is_string = not is_string
        if char != " " and not is_string:
            token += char
        else:
            tokens.append(token)
            token = ""
    tokens.append(token)
    token = ""
    return tokens

def parser(tokens):
    if tokens[0] == "rec":
        try:
            record(tokens[1])
        except IndexError:
            print("Syntax: rec [track_name]")
    elif tokens[0] == "play":
        try:
            if tokens[1] in track_list:
                play(tokens[1])
            else:
                print("[!] Track '" + tokens[1] + "' does not exist")
        except IndexError:
            print("Syntax: play [track_name]")
    elif tokens[0] == "list":
        try:
            if tokens[1] == "dev":
                list_devices()
            elif tokens[1] == "track":
                list_tracks()
            else:
                raise
        except:
            print("Syntax:\n\t list [object]")
            print("Object:\n\tlist track\t - shows a list of recorded tracks\n\tlist dev\t - shows a list of midi devices\n")
    elif tokens[0] == "del":
        try:
            if tokens[1] in track_list:
                del track_list[tokens[1]]
            elif tokens[1] not in track_list:
                print("[!] Track '" + tokens[1] + "' does not exist")
        except IndexError:
            print("Syntax: del [track_name]")
    elif tokens[0] == "help":
        print_help()
    elif tokens[0] == "kill":
        kill_notes()
    elif tokens[0] == "sel":
        try:
            select_device(tokens[1])
        except IndexError:
            print("Syntax: sel [midi_device]")
            print("\tUse either the midi device 'name' within quotation marks")
            print("\tor the device number from 'list dev'.")
    elif tokens[0] == "exit":
        exit()
    elif tokens[0] == "":
        pass
    else:
        print("Invalid command '" + tokens[0] + "'. Type 'help' for a list of commands.")

def main():
    print("""
██████╗ ██╗   ██╗     ███╗   ███╗██╗██████╗ ██╗
██╔══██╗╚██╗ ██╔╝     ████╗ ████║██║██╔══██╗██║
██████╔╝ ╚████╔╝█████╗██╔████╔██║██║██║  ██║██║
██╔═══╝   ╚██╔╝ ╚════╝██║╚██╔╝██║██║██║  ██║██║
██║        ██║        ██║ ╚═╝ ██║██║██████╔╝██║
╚═╝        ╚═╝        ╚═╝     ╚═╝╚═╝╚═════╝ ╚═╝
    """)
    print("Interface for interacting with midi devices.")
    print("Type 'help' for more information.\n")
    while True:
        u_input = input("> ")
        tokens = lexer(u_input)
        parser(tokens)

main()
