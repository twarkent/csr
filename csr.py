#! /usr/bin/env python
# encoding: utf-8

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

class color:
    PURPLE    = '\033[95m'
    CYAN      = '\033[96m'
    DARKCYAN  = '\033[36m'
    BLUE      = '\033[94m'
    GREEN     = '\033[92m'
    YELLOW    = '\033[93m'
    RED       = '\033[91m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'
    END       = '\033[0m'

#line_chars = {
#    'a':'┌',   '~':'─',   'v':'┬',   'b':'┐', 
#    'l':'│',   '+':'┼',   'k':'╷', 
#    '>':'├',                         '<':'┤',
#    'c':'└',              '^':'┴',   'd':'┘',   
#}

# ┌ ─ ─┬ ─┬ ── ─ ─┬ ──┐  
# │    ┼  │          ╷ 
# ├       ┤
# └   ┴   ┘


#print "┌──┬──┬──┬──┐"
#print "│  │  │  │  │"
#print "└──┴──┴──┴──┘"
#print "├ ─ ┤"
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

    def yaml_load(self, file, parent_file=''):
        if parent_file != '':
            pfile = os.path.split(os.path.abspath(parent_file))
            file = pfile[0] + '/' + file
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

            csr_map = self.yaml_load(block['file'], parent_file=parent_file)

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
  

def print_csr_txt(reg, base_addr, awidth, dwidth):
    margin = 3
    reg_addr = base_addr + reg['address']
    addr_disp_len = awidth/4 + 2
    data_disp_len = dwidth/4 + 2

    addr = "{0:#0{1}x}".format(reg_addr, addr_disp_len)

    print ''
    print '    REGISTER: ' + addr + ': ' + reg['name'] + ' - ' + reg['desc']
   

    lines = []

    # Line #1
    #print "┌ ─ ─ ┬ ─ ─ ┬ ─ ─ ┬ ─ ─ ┐"
    #print "│     │     │     │     │"
    #print "└ ─ ─ ┴ ─ ─ ┴ ─ ─ ┴ ─ ─ ┘"
    #print "├ ─ ─ ┼                 ┤"
    #print "│     │     │     │     │"
    #print "└ ─ ─ ┴ ─ ─ ┴ ─ ─ ┴ ─ ─ ┘"
    line = '┌'
    for i in range(dwidth-1):
        line = line + '──┬'
    line = line + '──┐'
    lines.append(line)

    # Line #2
    line = '│'
    for i in range(dwidth-1,-1,-1):
        line = line + str('%02d' % i)
        line = line + '│'
    lines.append(line)

    # Line #3
    line = '├'
    line = line + '─' * (3*dwidth-1)
    line = line + '┤'
    lines.append(line)

    # Line #4
    bits = [0] * dwidth
    bit_pos = []
    for b in range(dwidth):
        bit_pos.append('|  ') 
      
    bit_pos[dwidth-1] = '│  '
    bit_pos[0]  = '   │' 

    bit_pos_max = 0
    bit_pos_min = 0
    for field in reg['fields']:
        field_bit_pos = field['bit_pos'].split(':')
        bit_pos_max = int(field_bit_pos[0])
        bit_pos_min = bit_pos_max
        if len(field_bit_pos) == 2: 
            bit_pos_min = int(field_bit_pos[1])

        for b in range(bit_pos_max, bit_pos_min-1, -1):
            bits[b] = True
            bit_pos[b] = '---'
            if b == bit_pos_max:            bit_pos[b] = '|--'
            if b == 0:                      bit_pos[b] = '---│'
            if b == (dwidth-1):             bit_pos[b] = '│--'
            if b == 0 and b==bit_pos_max:   bit_pos[b] = '|--│'
            elif bit_pos_min==bit_pos_max:  bit_pos[b] = '|--'

    chars =  ''.join(bit_pos[::-1])
    lines.append(chars)

    # Line #5
    line = '└'
    line = line + '─' * (3*dwidth-1)
    line = line + '┘'
    lines.append(line)
    lines.append('')

    # Determine length of longest field name
    field_max = 0
    for field in reg['fields']:
        if len(field['name']) > field_max:
            field_max = len(field['name'])

    label = []
    label.append('Bit-Pos')
    label.append('Field')
    label.append('Default')
    label.append('Attributes')
    label.append('Description')
 
    if data_disp_len < 8:
        default_max = 8 
    else:
        default_max = data_disp_len + 1

    col_width = [8, field_max+2, default_max, 15, 40]
    underline = '─' 

    line = ''
    for i in range(len(col_width)):
        line = line + '{:{}s}{}'.format(label[i], col_width[i], ' ')
    lines.append(line)

    line = ''
    for i in range(len(col_width)):
        line = line + '{:{}s}{}'.format(underline*col_width[i],col_width[i], ' ')
    lines.append(line)

    for line in lines:
        print ' '*margin,
        print ''.join(line)
      
    for field in reg['fields']:
        bit_pos = '[%s]' % field['bit_pos']
        por =  int(field['por'])
        por = "{0:#0{1}x}".format(por, data_disp_len)
        attributes = ','.join(field['attributes'])

        data = []
        data.append(bit_pos)
        data.append(field['name'])
        data.append(por)
        data.append(attributes)
        data.append(field['desc'])

        print ' '*margin,
        # Right justify first column (bit-width)
        line = '{:>8}{}'.format(bit_pos,' ') 
        for i in range(1, len(col_width)):
            line = line + '{:{}s}{}'.format(data[i], col_width[i], ' ')
        print line

    print ""
    print ""

  
def print_txt_blocks(blocks):
    for block in blocks:
        base_addr = block['base_addr']
        print "  BLOCK: %s %s (%s): %s" % ( block['csr']['name'], str(hex(block['base_addr'])), block['file'], block['csr']['desc'])
        awidth = block['csr']['awidth']
        dwidth = block['csr']['dwidth']
        print "    AWIDTH = %s"   % awidth
        print "    DWIDTH = %s"   % dwidth

        for reg in block['csr']['registers']:
            print_csr_txt(reg, base_addr, awidth, dwidth)

        try:
            for b in block['csr']['blocks']:
                print_txt_blocks(block['csr']['blocks'])
        except:
            pass
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

    print_txt_blocks(blocks) 
         

def main():

  args = arg_parser()

  cmd = 'rm -f ' + args.logfile
  os.system(cmd)

  # The logger must be setup/configured in order to create objects
  log = logger(args)


  csr = CsrMap(args.yaml)
  print_txt(csr)


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
  
