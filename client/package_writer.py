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

import os
import sys
from tabulate import tabulate
from collections import deque
from collections import namedtuple
from datetime import datetime


class PackageWriter:

    def __init__(self, max_packages, custom_report):

        self.max_packages = max_packages
        self.custom_report = None
        self.custom_reports_enabled = custom_report

        # If custom reports is enabled, create container for desired variables.
        if self.custom_reports_enabled == True:
            variables = self.read_watch_list()
            CustomReportsStructure = namedtuple("CustomReportsStructure", variables)
            self.custom_report = CustomReportsStructure(*([None] * len(variables)))

        # Ensure output directory exists.
        output_directory = "F:/Py program/VSCode/PrimaryInterface/test1/UR_Primary_Client_Python_Library/client/output"
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Create a file for every package type in output directory.
        self.file_paths = [
            (-1, os.path.join(output_directory, "disconnect.txt")),
            (16, os.path.join(output_directory, "robot_state.txt")),
            (20, os.path.join(output_directory, "robot_message.txt")),
            (22, os.path.join(output_directory, "hmc_message.txt")),
            (5, os.path.join(output_directory, "modbus_info_message.txt")),
            (23, os.path.join(output_directory, "safety_setup_broadcast_message.txt")),
            (
                24,
                os.path.join(
                    output_directory, "safety_compliance_tolerances_message.txt"
                ),
            ),
            (25, os.path.join(output_directory, "program_state_message.txt")),
        ]
        for _, file_path in self.file_paths:
            with open(file_path, "w") as file:
                file.write("")

        # Manages user defined capacity constraints.
        self.package_counts = [(key, 0) for key, _ in self.file_paths]
        self.package_deques = {
            key: deque(maxlen=self.max_packages) for key, _ in self.file_paths
        }

    # Function writes all subpackages within `package` to file `packagetype`.txt .
    def append_package_to_file(self, package):
        message_type = package.type
        file_path = None

        # Identifies the file related to `package.package_type`.
        for index, (key, path) in enumerate(self.file_paths):
            if key == message_type:
                file_path = path

                # Increment the counter for the matching package type only if the deque is not full.
                if len(self.package_deques[key]) < self.max_packages:
                    self.package_counts[index] = (
                        key,
                        self.package_counts[index][1] + 1,
                    )
                break

        # Performs write operation to file.
        if file_path:
            self.package_deques[message_type].append(f"{package}\n{'#' * 80}\n")
            with open(file_path, "w") as file:
                for pkg_str in self.package_deques[message_type]:
                    file.write(pkg_str)
        else:
            print(f"Unknown message type: {message_type}")

        # Displays current count to console.
        self.print_package_counts()

    def append_custom_report(self, package):
        self.update_custom_report(package)

        # If custom_reports_deque is not defined, create it with maxlen equal to max_packages
        if not hasattr(self, "custom_reports_deque"):
            self.custom_reports_deque = deque(maxlen=self.max_packages)

        # Prepare the table data with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-4]
        table_data = [timestamp] + [
            getattr(self.custom_report, field) for field in self.custom_report._fields
        ]

        # Append the table data to custom_reports_deque
        self.custom_reports_deque.append(table_data)

        # Create headers
        headers = ["Timestamp"] + list(self.custom_report._fields)

        # Write the contents of custom_reports_deque to the file
        output_directory = "output"
        custom_report_path = os.path.join(output_directory, "custom_report.txt")
        with open(custom_report_path, "w") as file:
            file.write(
                tabulate(self.custom_reports_deque, headers=headers, tablefmt="grid")
            )

    def print_package_counts(self):
        sys.stdout.write("\r")
        sys.stdout.write(
            f"RECEIVED: {self.package_counts[0][0]}:{self.package_counts[0][1]}, {self.package_counts[1][0]}:{self.package_counts[1][1]}, {self.package_counts[2][0]}:{self.package_counts[2][1]}, {self.package_counts[3][0]}:{self.package_counts[3][1]}, {self.package_counts[4][0]}:{self.package_counts[4][1]}, {self.package_counts[5][0]}:{self.package_counts[5][1]}, {self.package_counts[6][0]}:{self.package_counts[6][1]}, {self.package_counts[7][0]}:{self.package_counts[7][1]}"
        )
        sys.stdout.flush()

    def read_watch_list(self):
        variables = []
        with open("watch_list.txt", "r") as file:
            for line in file:
                package_name, var_name = line.strip().split(",")
                variables.append(
                    f"{package_name.replace(' ', '_')}_{var_name.replace(' ', '_')}"
                )
        return variables

    def update_custom_report(self, package):
        # Get the set of fields in CustomReportsStructure
        custom_reports_fields = set(self.custom_report._fields)

        for subpackage in package.subpackage_list:

            # Get the set of fields in the object's subpackage_variables named tuple
            subpackage_variable_fields = set(subpackage.subpackage_variables._fields)

            # Create copy of subpackage name without spaces.
            subpackage_name = subpackage.subpackage_name.replace(" ", "_")

            # Replace spaces with underscores in field names and prepend the subpackage name
            updated_field_names = [
                f"{subpackage_name}_{field.replace(' ', '_')}"
                for field in subpackage_variable_fields
            ]

            # Create a new namedtuple with the updated field names
            CopySubpackageVariables = namedtuple(subpackage_name, updated_field_names)

            # Retrieve the original values from subpackage.subpackage_variables
            original_values = [
                getattr(subpackage.subpackage_variables, field)
                for field in subpackage_variable_fields
            ]

            # Create an instance of the new namedtuple with the original values
            updated_subpackage_variables = CopySubpackageVariables(*original_values)

            # Find the shared fields
            shared_fields = custom_reports_fields.intersection(updated_field_names)

            # Update the shared fields in the CustomReportsStructure instance
            self.custom_report = self.custom_report._replace(
                **{
                    field: getattr(updated_subpackage_variables, field)
                    for field in shared_fields
                }
            )
