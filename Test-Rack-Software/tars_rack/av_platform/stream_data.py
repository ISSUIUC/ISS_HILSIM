import serial
import time
import os
import serial.tools.list_ports
import av_platform.csv_datastream as csv_datastream
import pandas
import traceback
import io
import util.communication.packets as packet


def raw_csv_to_dataframe(raw_csv):
    # Get column names
    header = raw_csv.split('\n')[0].split(",")
    csv = "\n".join(raw_csv.split('\n')[1:])
    csvStringIO = io.StringIO(csv)
    return pandas.read_csv(csvStringIO, sep=",", header=None, names=header)


def get_runtime(raw_csv):
    csv = raw_csv_to_dataframe(raw_csv)
    return (len(csv) * 10) / 1000 + 10


def run_hilsim(raw_csv: str, serial_port: serial.Serial, update_callback):
    print("(stream_data) Processing run request")
    hilsim_return_log = ""
    csv = raw_csv_to_dataframe(raw_csv)
    csv_list = csv.iterrows()
    print("(stream_data) Successfully parsed CSV")

    last_time = time.time() * 1000
    start_time = last_time

    approx_time_sec = (len(csv) * 10) / 1000 + 5
    print(
        "(stream_data) Request accepted: Approximate runtime: " +
        str(approx_time_sec) +
        "s")
    print("(stream_data) Awaiting serial connection (5s)...")
    update_callback(packet.construct_job_status(True, "spin_up", "Accepted"))

    watchdog_start = time.time()
    cur_line = 0

    while (True):
        if (abs(watchdog_start - time.time()) > 3):
            print("(stream_data) Watchdog timer tripped")
            return hilsim_return_log
        if time.time() * 1000 > last_time + 10:
            last_time += 10
            if time.time() * 1000 < start_time + 5000:
                pass
            else:
                if (cur_line == 0):
                    packet.construct_job_status(
                        True, "running", f"Running (Data streaming started)")
                cur_line += 1

                if (cur_line % 300 == 0):
                    update_callback(
                        packet.construct_job_status(
                            True,
                            "running",
                            f"Running ({cur_line/len(csv)*100:.2f}%) [{cur_line} processed out of {len(csv)} total]"))

                line_num, row = next(csv_list, (None, None))
                if line_num is None:
                    update_callback(
                        packet.construct_job_status(
                            True, "done", f"Finished data streaming"))
                    break
                data = csv_datastream.csv_line_to_protobuf(row)
                if not data:
                    update_callback(
                        packet.construct_job_status(
                            True,
                            "error",
                            f"Expected data to insert, but found none."))
                    return hilsim_return_log
                try:
                    serial_port.write(data)
                except BaseException:
                    update_callback(
                        packet.construct_job_status(
                            True,
                            "error",
                            f"Exception during serial write: " +
                            traceback.format_exc()))
                    return hilsim_return_log
        if serial_port.in_waiting:
            data = serial_port.read_all()
            string = data.decode("utf8")

            if string:
                watchdog_start = time.time()
                string = string[0: (len(string) - 1)]
                hilsim_return_log += string + "\n"
        else:
            watchdog_start = time.time()
    return hilsim_return_log
