#!/usr/bin/env python3
"""
# USB-USB Serial Test
# Communicate from tot_console to pi slave with audio mux hat

Half-duplex serial communication between two Raspberry Pis over a single USB cable.

Uses a USB-to-USB null modem adapter (FTDI-based) plugged into a USB port on
each Pi.  On each Pi the adapter appears as /dev/ttyUSB0 (or /dev/ttyACM0).

Role        |  Port       |  What to run
------------|-------------|------------------------------
transmit Pi | /dev/ttyUSB0 | python3 serial_link.py --role master  --port /dev/ttyUSB0
receive Pi  | /dev/ttyUSB0 | python3 serial_link.py --role responder --port /dev/ttyUSB0

Dependencies:
    pip install pyserial

Permissions:
    sudo usermod -a -G dialout $USER   # then logout / login
"""

import argparse
import serial
import time
import sys

# ---------------------------------------------------------------------------
# Defaults — override via command-line arguments for portability
# ---------------------------------------------------------------------------
DEFAULT_PORT    = "/dev/ttyUSB0"
DEFAULT_BAUD    = 9600
DEFAULT_ROLE    = "master"          # "master" or "responder"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def open_serial(port, baud):
    """Open the serial port with sensible defaults for 8N1."""
    ser = serial.Serial(
        port=port,
        baudrate=baud,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1.0,
        write_timeout=1.0,
    )
    return ser


def send_and_receive(ser, command, timeout=2.0):
    """
    Half-duplex: send a newline-terminated command, then wait for a
    newline-terminated response.  Returns the response string (without the
    newline) or None on timeout.
    """
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    ser.write(f"{command}\n".encode())
    ser.flush()

    deadline = time.time() + timeout
    while time.time() < deadline:
        if ser.in_waiting > 0:
            line = ser.readline().decode(errors="replace").strip()
            if line:
                return line
        time.sleep(0.05)

    return None


# ---------------------------------------------------------------------------
# Master logic — Pi that sends commands and waits for replies
# ---------------------------------------------------------------------------
def run_master(ser):
    commands = [
        "PING",
        "TEMP?",
        "LED ON",
        "LED OFF",
        "QUIT",
    ]

    for cmd in commands:
        print(f"[MASTER] Sending: {cmd}", flush=True)
        reply = send_and_receive(ser, cmd, timeout=2.0)
        if reply is not None:
            print(f"[MASTER] Reply  : {reply}", flush=True)
        else:
            print("[MASTER] Timeout — no reply.", flush=True)
        time.sleep(0.5)


# ---------------------------------------------------------------------------
# Responder logic — Pi that listens for commands and replies
# ---------------------------------------------------------------------------
def run_responder(ser):
    print("[RESPONDER] Listening on", ser.port, flush=True)
    while True:
        if ser.in_waiting > 0:
            cmd = ser.readline().decode(errors="replace").strip()
            if not cmd:
                continue
            print(f"[RESPONDER] Got: {cmd}", flush=True)

            reply = None
            if cmd == "PING":
                reply = "PONG"
            elif cmd == "TEMP?":
                reply = "TEMP:23.5C"
            elif cmd == "LED ON":
                reply = "ACK:LED ON"
            elif cmd == "LED OFF":
                reply = "ACK:LED OFF"
            elif cmd == "QUIT":
                reply = "BYE"
                ser.write(f"{reply}\n".encode())
                ser.flush()
                print("[RESPONDER] Quitting.", flush=True)
                break
            else:
                reply = f"ERR:UNKNOWN:{cmd}"

            if reply:
                ser.write(f"{reply}\n".encode())
                ser.flush()

        time.sleep(0.02)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Half-duplex USB serial link between two Raspberry Pis"
    )
    parser.add_argument("--port",  default=DEFAULT_PORT,  help="Serial port (e.g. /dev/ttyUSB0)")
    parser.add_argument("--baud",  type=int, default=DEFAULT_BAUD, help="Baud rate")
    parser.add_argument("--role",  choices=["master", "responder"], default=DEFAULT_ROLE)
    args = parser.parse_args()

    try:
        ser = open_serial(args.port, args.baud)
    except serial.SerialException as exc:
        print(f"Error opening {args.port}: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"[{args.role.upper()}] Connected to {args.port} @ {args.baud} baud", flush=True)

    try:
        if args.role == "master":
            run_master(ser)
        else:
            run_responder(ser)
    except KeyboardInterrupt:
        print("\nInterrupted.", flush=True)
    finally:
        ser.close()
        print(f"[{args.role.upper()}] Port closed.", flush=True)


if __name__ == "__main__":
    main()
