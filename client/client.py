"""
BSD 3-Clause License

Copyright (c) 2023, Shawn Armstrong

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import argparse
import socket
import sys
import os
from package import Package
from package_writer import PackageWriter

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Client for receiving robot data")
parser.add_argument(
    "-i",
    "--ip_address",
    default=socket.gethostbyname(socket.gethostname()),
    help="IP address of the robot (default: local IP address)",
)
parser.add_argument(
    "-m",
    "--max_reports",
    type=int,
    default=10,
    help="Maximum number of reports to write (default: 10)",
)
parser.add_argument(
    "-c",
    "--custom_report",
    action="store_true",
    help="Generate custom report based on watch_list.txt",
)
args = parser.parse_args()

if args.custom_report:
    if not os.path.exists("watch_list.txt"):
        print("Error: watch_list.txt not found.")
        sys.exit(1)

HOST = "localhost"
PORT = 30001

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:

    clientSocket.settimeout(4)
    try:
        clientSocket.connect((HOST, PORT))
    except socket.timeout as e:
        print(f"Timeout error: {e}")
        sys.exit(1)
    except socket.error as e:
        print(f"Could not connect to {HOST}:{PORT} Error: {e}")
        sys.exit(1)

    writer = PackageWriter(args.max_reports, args.custom_report)
    f = open("F:/Py program/VSCode/Test_send_program_to_UR/test.script", "rb")
    l = f.read(4096)
    clientSocket.sendall(l)
    while True:

        # Receives message from UR controller.
        new_message = clientSocket.recv(4096)

        # Creates package based on message received.
        new_package = Package(new_message)

        # Writes subpackage content to file.
        writer.append_package_to_file(new_package)

        # Demonstrates custom reports.
        if writer.custom_reports_enabled == True:
            writer.append_custom_report(new_package)

        # Demonstrates accessing subpackage data.
        # subpackage = new_package.get_subpackage("Robot Mode Data")
        # if subpackage is not None:
        #     print(f"subpackage.subpackage_variables.timestamp={subpackage.subpackage_variables.timestamp}")
