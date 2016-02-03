#!/bin/env python**
import subprocess

program_name = "ls"
arguments = ["-l", "-a"]

command = [program_name]
command.extend(arguments)

output = subprocess.Popen(command, stdout=subprocess.PIPE).communicate()[0]
print output
