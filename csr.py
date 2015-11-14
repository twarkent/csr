#! /usr/bin/python

# ------------------------------------------------------------------------------
# FILE NAME      : csr.py
# CURRENT AUTHOR : Tim Warkentin
# AUTHOR'S EMAIL : tim.warkentin@gmail.com
# ------------------------------------------------------------------------------
# KEYWORDS: CSR 
# ------------------------------------------------------------------------------
# PURPOSE: Read csr YAML files and generate register maps in RTL, HTML and text.
# ------------------------------------------------------------------------------
# TODO: 
# ------------------------------------------------------------------------------

import sys
import os
import math
import re
import shlex
import time
import argparse
import logging
import traceback
import collections
import yaml
import pprint

log = logging.getLogger('csr_logger')

# ------------------------------------------------------------------------------
def arg_parser():

  parser = argparse.ArgumentParser(description='Control Status Register Generator')

  parser.add_argument(
    '-l', 
    dest="logfile",
    default="csr.log",
    help='Name of log file (default set to csr.log).',
    metavar='FILE')

  parser.add_argument('yaml')

  parser.add_argument(
    '-r', '--rtl', 
    action='store_true',
    default=False,
    help='Generate RTL file')

  parser.add_argument(
    '--html', 
    action='store_true',
    default=False,
    help='Generate HTML file')

  parser.add_argument(
    '-t', '--txt', 
    action='store_true',
    default=False,
    help='Generate text file')

  parser.add_argument(
    '-v', '--verbose', 
    action='count',
    help="Increase logger output verbosity (eg: -vv is more than -v")

  parser.add_argument(
    '-c', '--console', 
    action='count',
    help="Increase logger output verbosity to console (eg: -cc is more than -c")

  args = parser.parse_args()

  return args


# ------------------------------------------------------------------------------
# Logging type available:
#   log.debug    ("debug message")
#   log.info     ("info message")
#   log.warn     ("warn message")
#   log.error    ("error message")
#   log.critical ("critical message")
# ------------------------------------------------------------------------------
def logger(args):

    file = os.path.basename(__file__)
    log = logging.getLogger('csr_logger')
    log.setLevel(logging.DEBUG)

    # Create file handler
    fh = logging.FileHandler(args.logfile)

    fh.setLevel(logging.DEBUG)
    if args.verbose == 1:                                                                              
        fh.setLevel(logging.DEBUG)
    else:
        fh.setLevel(logging.INFO)

    console = logging.StreamHandler()
    if args.console == 1:
        console.setLevel(logging.INFO)
    elif args.console == 2:
        console.setLevel(logging.DEBUG)
    else:
        console.setLevel(logging.ERROR)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)-15s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    fh.setFormatter(formatter)

    # Add the handlers to logger
    log.addHandler(console)
    log.addHandler(fh)

    return log 


# ------------------------------------------------------------------------------
class CsrMap(object):

    def __init__(self, yaml_file):
        self.files = []
        self.map   = self.yaml_load(yaml_file)
        self.files.append(yaml_file)
        try:
            design     = self.map['design']
            cpu        = design['cpu']
            blocks     = design['blocks']
        except:
            raise RuntimeError('Error: Yaml file must include sections for the following: design, cpu, blocks.')
        self.load_sub_blocks(blocks, yaml_file)

    def yaml_load(self, file, parent_file=""):
        try:
            fh = open(file, 'r')
        except:
            raise IOError('%s unable to read file: %s' % (parent_file, file))
        csr_map = yaml.load(fh)
        fh.close()
        return csr_map

    # Traverse all yaml files
    def load_sub_blocks(self, blocks, parent_file):
        if blocks == 0:
            return 0
        for index, block in enumerate(blocks):
            print "Load File: %s" % (block['file'])
            log.info( "%s : %s" %(block['name'], block['file']))

            csr_map = self.yaml_load(block['file'], parent_file)

            self.files.append(block['file'])
            blocks[index]['csr'] = csr_map
            try:
                sub_blocks = csr_map['blocks']
            except:
                sub_blocks = 0

            self.load_sub_blocks(sub_blocks, parent_file=block['file'])


    def rtl_gen(self):
        design = self.map['design']
        blocks = design['blocks']
        for block in blocks:
          for reg in block['csr']:
             print len(reg)
  

    # ------------------------------------------------------------------------------
    def rtl_header(self, cpu, cpu_clk, block_name):

	now = time.localtime()
	date = "%s/%02d/%02d" %(str(now.tm_year), now.tm_mon, now.tm_mday)
	year = str(now.tm_year)

	print '// --------------------------------------------------------------------------------------------------'
	print '// Copyright (c) %s  Ixia  All rights reserved.' % year
	print '//'
	print '//   This file includes unpublished proprietary source code of Ixia.  The copyright'
	print '//   notice above does not evidence any actual or intended publication of such'
	print '//   source code. You shall not disclose such source code (or any related information)'
	print '//   and shall use it only in accordance with the terms of the license or confidentiality'
	print '//   agreements you have entered into with Ixia. Distributed to licensed users or owners.'
	print '//'
	print '// --------------------------------------------------------------------------------------------------'
	print '// FILE NAME      : %s_csr.v' % block_name
	print '// CURRENT AUTHOR : csr script'          
	print '// --------------------------------------------------------------------------------------------------'
	print '// KEYWORDS: %s control status registers.' % block_name
	print '// --------------------------------------------------------------------------------------------------'
	print '// PURPOSE:  %s %s control status registers.' %(cpu, block_name)
	print '// --------------------------------------------------------------------------------------------------'
	print '// Parameters'
	print '//   NAME              DEFAULT      DESCRIPTION'
	print '//   ----------------- ------------ -----------------------------------------------------------------'
	print '// --------------------------------------------------------------------------------------------------'
	print '// Reuse Issues:'
	print '//   Reset Strategy:      Synchronous'
	print '//   Clock Domains:       %s' % cpu_clk
	print '//   Critical Timing:     None'
	print '//   Test Features:       None'
	print '//   Asynchronous I/F:    None'
	print '//   Synthesizable:       Yes'
	print '// --------------------------------------------------------------------------------------------------'
	print ''


    # ------------------------------------------------------------------------------
    def print_footer():

        now = time.localtime()
        date = "%s/%02d/%02d" %(str(now.tm_year), now.tm_mon, now.tm_mday)

        print "\n"
	print "endmodule\n"
	print "// -------------------------------------------------------------------------------------------------"
	print "// Release History"
	print "//   VERSION DATE       AUTHOR           DESCRIPTION"
	print "// --------- ---------- ---------------- -----------------------------------------------------------"
	print "//   1.0     %s csr script       Do not modify. Changes may be overwritten." % date
	print "// -------------------------------------------------------------------------------------------------"
  

def csr_txt(reg, base_addr, awidth, dwidth):
    margin = 1
    reg_addr = base_addr + reg['address']
    addr_disp = awidth/4 + 2
    data_disp = dwidth/4 + 2
    addr = "{0:#0{1}x}".format(reg_addr, addr_disp)

    print "  %s: %s - %s" % (addr, reg['name'], reg['desc'])

    lines = []
    chars = []

    # Line #1
    chars.append(unichr(0x250c))
    for i in range(dwidth-1):
        chars.append(unichr(0x2500)*2)
        chars.append(unichr(0x252c))
    chars.append(unichr(0x2500)*2)
    chars.append(unichr(0x2510))
    lines.append(chars)

    # Line #2
    chars = []
    chars.append(unichr(0x2502))
    for i in range(dwidth-1,-1,-1):
        chars.append("%02d" % i)
        chars.append(unichr(0x2502))
    lines.append(chars)

    # Line #3
    chars = []
    chars.append(unichr(0x251c))
    chars.append(unichr(0x2500)*(3*dwidth-1))
    chars.append(unichr(0x2524))
    lines.append(chars)

    # Line #4
    bit_pos = []
    chars = []
    chars.append(' ')
    chars.append(' ')
    chars.append(' ')
    vertical = unichr(0x2502)
    for b in range(dwidth):
        bit_pos.append('   ')
    chars[0] = vertical
    bit_pos[31] = "|  "
    bit_pos[0]  = "  |"
    bit_pos_max = 0
    bit_pos_min = 0
    for field in reg['fields']:
        field_bit_pos = field['bit_pos'].split(':')
        if len(field_bit_pos) == 2: 
            bit_pos_max = int(field_bit_pos[0])
            bit_pos_min = int(field_bit_pos[1])
        else:
            bit_pos_max = int(field_bit_pos[0])
            bit_pos_min = bit_pos_max
        print "MAX:", bit_pos_max, "MIN:", bit_pos_min
        for b in range(bit_pos_max, bit_pos_min-1, -1):
            bit_pos[b] = '---'
            if b == bit_pos_max:          bit_pos[b] = '|--'
            if b == 0:                    bit_pos[b] = '---|'
            if b == 31:                   bit_pos[b] = '|--'
            if b == 0 and b==bit_pos_max: bit_pos[b] = '|--|'
            if bit_pos_min==bit_pos_max:  bit_pos[b] = '|--'

    chars =  ''.join(bit_pos[::-1])
    lines.append(chars)

    # Line #5
    chars = []
    chars.append(unichr(0x2514))
    chars.append(unichr(0x2500)*(3*dwidth-1))
    chars.append(unichr(0x2518))
    lines.append(chars)

    chars = []
    lines.append(chars)

    chars = []
    chars.append(' Bit-Pos Field            Default     Attributes  Description')
    lines.append(chars)

    chars = []
    chars.append(' ')
    chars.append(unichr(0x2500)*7)
    chars.append(' ')
    chars.append(unichr(0x2500)*16)
    chars.append(' ')
    chars.append(unichr(0x2500)*11)
    chars.append(' ')
    chars.append(unichr(0x2500)*11)
    chars.append(' ')
    chars.append(unichr(0x2500)*46)
    lines.append(chars)

    for c in lines:
        print " "*margin,
        print "".join(c)

    for field in reg['fields']:
        bit_pos = '[%s]' % field['bit_pos']
        por =  int(field['por'])
        por = "{0:#0{1}x}".format(por, data_disp)
        attributes = ' '.join(field['attributes'])
        print "   %7s %-15s  %s  %-12s%s "% (bit_pos, field['name'], por, attributes, field['desc'])
    print ""
  

def print_txt(csr):

    design = csr.map['design']
    blocks = design['blocks']
    cpu    = design['cpu']

    print '\n'
    print 'Design: %s - %s\n' % (design['name'], design['desc'])
    print '  CPU: %s  Bus: %s\n' % (cpu['name'], cpu['bus'])

    cpu_awidth = cpu['awidth']
    disp = cpu_awidth/4 + 2

    for block in blocks:
#       print block.viewkeys()
        base_addr = block['base_addr']
        print "  Block: %s %s (%s): %s" % ( block['csr']['name'], str(hex(block['base_addr'])), block['file'], block['csr']['desc'])
        awidth = block['csr']['awidth']
        dwidth = block['csr']['dwidth']
#       disp = awidth/4 + 2
        print "    AWIDTH = %s"   % awidth
        print "    DWIDTH = %s"   % dwidth
#       print "    Desc   = %s\n" % block['csr']['desc']

        for reg in block['csr']['registers']:
            csr_txt(reg, base_addr, awidth, dwidth)
#           reg_addr = base_addr + reg['address']
#           addr = "{0:#0{1}x}".format(reg_addr, disp)
#           print "  %s: %s - %s" % (addr, reg['name'], reg['desc'])
#           print "   ",reg.viewkeys()
#           for field in reg['fields']:
#               print "     FIELD: ", field['name'], field['attributes'], field['bit_pos']
#               print "     ", field.viewkeys()
#           print ""

        try:
            for b in block['csr']['blocks']:
                print "   Sub-block: %s" % b['name']
                print "   ",b.viewkeys()
        except:
            pass
        print ""
         
def main():

  args = arg_parser()

  cmd = 'rm -f ' + args.logfile
  os.system(cmd)

  # The logger must be setup/configured in order to create objects
  log = logger(args)

# log.info('----------------------------------')
# log.info('Control Status Register Generation')
# log.info('----------------------------------')
# log.info('Command-Line Arguments:')

  csr = CsrMap(args.yaml)
  print_txt(csr)

# design = csr.map['design']
# blocks = design['blocks']
# for block in blocks:
#     print block.viewkeys()
#     print "Block: %s %s (%s)" % ( block['csr']['name'], str(hex(block['base_addr'])), block['file'])
#     awidth = block['csr']['awidth']
#     disp = awidth/4 + 2
#     print "  AWIDTH = %s"   % block['csr']['awidth']
#     print "  DWIDTH = %s"   % block['csr']['dwidth']
#     print "  Desc   = %s\n" % block['csr']['desc']
#     for r in block['csr']['registers']:
#         addr = "{0:#0{1}x}".format(r['address'], disp)
#         print "  %s: %s - %s" % (addr, r['name'], r['desc'])
#         print "   ",r.viewkeys()
#         for f in r['fields']:
#             print "     FIELD: ", f['name'], f['attributes'], f['bit_pos']
#             print "     ", f.viewkeys()
#         print ""

  pp = pprint.PrettyPrinter(indent=2)
# pp.pprint(csr.map)


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    sys.exit(main())

# -----------------------------------------------------------------------------
# Release History
#   VERSION DATE        AUTHOR            DESCRIPTION
#   ------- ----------- ----------------- -------------------------------------
#   1.0     2015/11/07  Tim Warkentin     Initial Version.
# -----------------------------------------------------------------------------
  
