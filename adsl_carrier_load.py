#!/usr/bin/env python3
# Plot ADSL carrier load with gnuplot
# (Output format used by Telewell EA-510v2)
#
# Copyright (C) 2011 by Joonas Kuorilehto
# License: MIT License
#
#SAMPLE_DATA = """
#carrier load : number of bits per symbol(tone)
#tone    0- 31:00 00 00 79 aa bb bc dd dd dd dd dd dc cb ba 00 
#tone   32- 63:00 00 02 34 45 67 89 9a ab bb bb bc cc cc cc cc 
#tone   64- 95:0c cc ba cc cc cc cc cc cc cc cc cc cc cc cc cc 
#tone   96-127:cc cc cc cc cb cb cb bb bb bb bb bb bb bb bb ab 
#tone  128-159:aa ab aa aa aa aa aa aa aa aa aa aa aa aa aa aa 
#tone  160-191:aa aa aa 99 99 99 99 99 99 99 99 99 99 99 99 99 
#tone  192-223:99 99 99 a9 99 99 99 9a aa 99 99 99 99 99 99 99 
#tone  224-255:99 99 99 99 99 89 99 99 99 99 99 88 88 77 66 54 
#"""
#with open('test.txt', 'w') as f:
#    f.write(SAMPLE_DATA.encode("UTF-8"))

import subprocess
import sys
import os.path

from optparse import OptionParser

plot_script = """
    set ylabel "Bits per tone";
    set xlabel "Carrier tone index";
    set terminal png;
    set output "%(png_filename)s";
    plot [:] [0:15] "-" with steps title "%(title)s";
"""

def parse_tones(line):
    tones_hex = line.split(':')[1].strip().replace(' ', '')
    tones = [int(tone, 16) for tone in tones_hex]
    return tones

def plot(data, png_filename):
    title = 'ADSL carrier load'
    cmd = ['gnuplot', '-e', plot_script % vars()]
    program = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    # Send data to gnuplot through stdin
    for i in range(0, len(data)):
        line = "%d %d\n" % (i, data[i])
        program.stdin.write(line.encode("UTF-8"))
    program.stdin.write("e".encode("UTF-8"))
    program.stdin.close()

def main():
    usage = "usage: %prog [options] FILE"
    parser = OptionParser(usage=usage)
    parser.add_option('-o', '--output', dest="png_filename", default=None,
                      help="write output PNG to FILE", metavar="FILE")
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_usage()
        exit(1)
    fname = args[0]
    if not os.path.exists(fname):
        print("Input file does not exist")
        exit(1)

    if options.png_filename:
        png_filename = options.png_filename
    else:
        png_filename = fname.rstrip(".txt") + ".png"

    print("Output file name:", png_filename)

    with open(fname, 'r') as f:
        in_carrier_section = False

        for line in f:
            if in_carrier_section:
                if line.startswith('tone'):
                    all_tones += parse_tones(line)
                else:
                    in_carrier_section = False
            else:
                if "carrier load" in line:
                    all_tones = []
                    in_carrier_section = True
                else:
                    continue
    if not all_tones:
        print("The file %s format is invalid" % fname)
        exit(1)
    plot(all_tones, png_filename)

if __name__ == '__main__':
    main()
