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
import textwrap

log = logging.getLogger('csr_logger')

# Register
# Type      Description
# ------------------------------------------------------------------------------------
# COR:      Clear on Read.
# DECR:     A read-only decrementing counter that is commonly cleared using COR, 
#           or W1C and naturally rolls-over. A single-bit input signal is used 
#           as the trigger. The bit_pos field is used to determine the counters bit-width.
# DECRS:    A read-only decrementing (saturate to all 0's) counter that is commonly cleared 
#           using COR, or W1C.
# DOR:      Decrement on read. The field is decremented when the address is read.
# DORS:     Decrement on read saturating
# INCR:     A read-only incrementing counter that is commonly cleared using COR, 
#           or W1C and naturally rolls-over.
# INCRS:    A read-only incrementing (saturate to all 1's) counter that is commonly cleared 
#           using COR, or W1C.
# IOR:      Increment on read
# IORS:     Increment on read saturating.
# INTERNAL: Field is not an input nor an output of this module. eg: a INCR register
#           may only have an single-bit input event signal and the multi-bit register
#           is internal to the module.
# RO:       Read-Only
# RP(A):    Read-Pulse with optional acknowledge
# SOR:      Set on read. The field is set to all 1's when the address is read.
# STO:      Sticky-low. This is like sticky (ST1), but the sticky values stays 0 if the 
#           nominal value is ever 0.
# ST1:      Register bits that are set and remain set in response to an event.
#           This field type is commonly cleared using COR, or W1C.
# SUB:      Subset. If several fields/addresses are combined to form a larger field.
# W1C:      Write-1-to-clear. The field is reset to 0 when the address is written to
#           and the corresponding bit(s) is/are 1.
# W1S:      Write-1-to-set. The field is set to 1's when the address is written and the
#           corrresponding bit(s) is/are 1, but is not altered if the bit(s) is/are 0.
# WO:       write-only
# WP(A):    Write-Pulse with optional acknowledge. The Pulse remains asserted if an 
#           acknowledge is expected.
# RAM<n>:   Implement using a RAM <n> words deep.

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
            log.debug("Load File: %s" % (block['file']))
            log.info( "%s : %s" %(block['name'], block['file']))

            csr_map = self.yaml_load(block['file'], parent_file=parent_file)

            self.files.append(block['file'])
            blocks[index]['csr'] = csr_map
            try:
                sub_blocks = csr_map['blocks']
            except:
                sub_blocks = 0

            self.load_sub_blocks(sub_blocks, parent_file=block['file'])

            try:
                include_files = csr_map['include']
            except:
                include_files = 0

            self.load_include_files(include_files, block, parent_file=block['file'])


    def load_include_files(self, include_files, block, parent_file):
        if include_files == 0:
            return 0 
        for index, include in enumerate(include_files):
            include_map = self.yaml_load(include['file'], parent_file=parent_file)
            block['csr']['registers'].append(include_map)
            self.files.append(include['file'])
        
    def rtl_csr_pkg(self, design, cpu, block):
        
        module = block['name']
        filename = '%s_csr_pkg' % module
        self.rtl_header(design=design, cpu=cpu, filename=filename, module=module)
        print 'package %s;' % filename
        print 'endpackage;\n'

    def rtl_avalon_bus_pkg(self):
        design   = self.map['design']
        blocks   = design['blocks']
        cpu      = design['cpu']

        module   = 'avalon_bus'
        filename = 'avalon_bus_pkg'

        self.rtl_header(design=design, cpu=cpu, filename=filename, module=module)

	print 'package avalon_bus_pkg;\n'
	print '  typedef enum {OKAY, RESERVED, SLAVE_ERROR, DECODE_ERROR} response_te;\n'

        print '  interface avalon_bus #(parameter AWIDTH=%d, DWIDTH=%d, BE_WIDTH=DWIDTH/8) (input clk, rst);' % (cpu['awidth'], cpu['dwidth'])
        print '    logic   [AWIDTH-1:0] addr;'
        print '    logic [BE_WIDTH-1:0] byte_enable;'
        print '    logic   [DWIDTH-1:0] wdata;'
        print '    logic   [DWIDTH-1:0] rdata;'
        print '    logic                rdata_valid;'
        print '    logic                wr;'
        print '    logic                rd;'
        print '    logic                lock;'
        print '    logic                wait_response;'
        print '    response_te          response;\n'

        print '    // Check for valid parameter values during elaboration'
        print '    generate'
        print '      if ( (DWIDTH!=8) || (DWIDTH!=16) || (DWIDTH!=32) || (DWIDTH!=64) || (DWIDTH!=128) )'   
        print '        $fatal(1, "Parameter DWIDTH has an unsupported value of %0d", DWIDTH);'
        print '      if ( DWIDTH/8 != BE_WIDTH )'
        print '        $fatal(1, "BE_WIDTH has an unsupported value of %0d", BE_WIDTH);'
        print '    endgenerate\n'

        print '    modport master ('
        print '      output addr,'
        print '      output wr,'
        print '      output rd,'
        print '      output wdata,'
        print '      input  rdata,'
        print '      input  rdata_valid,'
        print '      output byte_enable,'
        print '      input  response,'
        print '      output lock,'
        print '      input  wait_request,'
        print '    );\n' 

        print '    modport slave ('
        print '      input  addr,'
        print '      input  wr,'
        print '      input  rd,'
        print '      input  wdata,'
        print '      output rdata,'
        print '      output rdata_valid,'
        print '      input  byte_enable,'
        print '      output response,'
        print '      input  lock,'
        print '      output wait_request'
        print '    );\n' 

        print '  endinterface;' 
        print 'endpackage;\n' 
        
    def rtl_gen(self):
        design = self.map['design']
        cpu    = design['cpu']
        blocks = design['blocks']
        self.rtl_avalon_bus_pkg()
        self.rtl_blocks(design=design, cpu=cpu, blocks=blocks)

    def rtl_blocks(self, design, cpu, blocks):
        for block in blocks:
            module = block['name']
            filename = '%s_csr.sv' % module
            self.rtl_csr_pkg(design=design, cpu=cpu, block=block)
            self.rtl_header(design=design, cpu=cpu, filename=filename, module=module)
            self.rtl_portmap(cpu=cpu, block=block)
            self.rtl_signal_declarations(cpu=cpu, block=block)
            self.rtl_signal_assignments(cpu=cpu, block=block)
            self.rtl_readback(cpu=cpu, block=block)
            self.rtl_endmodule()
            self.rtl_footer()

            # Generate code for sub-blocks (if present)
            try:
                self.rtl_blocks(design=design, cpu=cpu, blocks=block['csr']['blocks'])
            except:
                pass

    def rtl_header(self, design, cpu, filename, module):

	now = time.localtime()
	date = "%s/%02d/%02d" %(str(now.tm_year), now.tm_mon, now.tm_mday)
	year = str(now.tm_year)

        header = design['header']
        header = header.split('\n')

        for line in header:
            line = line.replace('<YEAR>', year)
            line = line.replace('<FILENAME>', filename)
            line = line.replace('<MODULE>', module)
            line = line.replace('<CPU>', cpu['name'])
            line = line.replace('<CPU_CLOCK>', cpu['interface']['clock'])
            print line

    def field_vector(self, bit_pos):
        b = bit_pos.split(':')
        width = int(b[0]) - int(b[len(b)-1]) + 1
        width_str = ' ' * 7
        if width > 1:
            width_str = '[%d:%d]' % (width-1, 0)
            width_str = '%7s' % width_str
        return width_str
        
    def rtl_portmap(self, cpu, block):

	print 'module %s_csr \n' % block['name']
        print '  import avalon_bus_pkg::*, %s_csr_pkg::*;\n' % block['name']
        print '  ('
        print '    // %s bus interface ---------------' % cpu['name']
        print '    interface bus,\n'
        print '    // CSR Signals --------------------------------------'
        signals = []
        for reg in block['csr']['registers']:
            for field in reg['fields']:
                attributes = field['attributes']
                width = self.field_vector(field['bit_pos'])
                if 'RO' in attributes:
                    signals.append('    input  logic %s %s'           % (width, field['name']))
                if 'RW' in attributes:
                    signals.append('    output logic %s %s'           % (width, field['name']))
                if 'WP' in attributes:
                    signals.append('    output logic         %s_wp'   % field['name'])
                if 'WPA' in attributes:
                    signals.append('    output logic         %s_wp'   % field['name'])
                    signals.append('    input  logic         %s_wpa'  % field['name'])
                if 'RP' in attributes:
                    signals.append('    output logic         %s_rp'   % field['name'])
                if 'RPA' in attributes:
                    signals.append('    output logic         %s_rp'   % field['name'])
                    signals.append('    input  logic         %s_rpa'  % field['name'])
                if 'W1C' in attributes:
                    signals.append('    input  logic %s %s'           % (width, field['name']))
                if 'INCR'  in attributes or \
                   'INCRS' in attributes or \
                   'DECR'  in attributes or \
                   'DECRS' in attributes:
                    signals.append('    input  logic         %s'      % field['name'])
                    if 'INTERNAL' not in attributes:
                        signals.append('    ouput  logic %s %s_ctr'       % (width, field['name']))
        print ',\n'.join(signals)
        print '  );'

    def rtl_signal_declarations(self, cpu, block):
        print '\n'
        print '  // ---------------------------------------------------------------------------'
        print '  // Signal Declarations'
        print '  // ---------------------------------------------------------------------------'
        signals = []
        signals.append('  logic  [%d:0] reserved;' % cpu['dwidth'])
        for reg in block['csr']['registers']:
            bit_pos = '%s:0' % cpu['dwidth']
            width = self.field_vector(bit_pos)
            signals.append('  logic %s %s_reg;' % (width, reg['name']))
            for field in reg['fields']:
                width = self.field_vector(field['bit_pos'])
                attributes = field['attributes']
                if 'W1C' in attributes:
                    signals.append('  logic %s %s_w1c;' % (width, field['name']))
                if ('INCR'  in attributes or \
                   'INCRS' in attributes or \
                   'DECR'  in attributes or \
                   'DECRS' in attributes) and 'INTERNAL' in attributes:
                   
                    signals.append('  logic %s %s_ctr;' % (width, field['name']))
        signals.sort()
        print '\n'.join(signals)

    def rtl_signal_assignments(self, cpu, block):
        print '\n'
        print '  // ---------------------------------------------------------------------------'
        print '  // Signal Assignments'
        print '  // ---------------------------------------------------------------------------'
        print "  assign reserved = '0; // use as a place-holder for undefined register bits.\n"
        assign = []
        
        # Find the longest register name
        reg_names = []
        for reg in block['csr']['registers']:
            reg_names.append(reg['name'])
        max_len = len(max(reg_names, key=len)) + 4

        # Assign fields to their corresponding registers
        for reg in block['csr']['registers']:
            # set the default of each register bit to 'reserved'
            register = ['reserved' for i in range(cpu['dwidth'])]
            fields = []
            for field in reg['fields']:
                attributes = field['attributes']
                bits = map(int, field['bit_pos'].split(':'))
                for i in range(bits[0], bits[len(bits)-1]-1, -1):
                    register[i] = field['name']
                    if 'W1C' in attributes:    
                        register[i] = field['name'] + '_w1c'
                    if 'INCR'  in attributes or \
                       'INCRS' in attributes or \
                       'DECR'  in attributes or \
                       'DECRS' in attributes:
                        register[i] = field['name'] + '_ctr'

            field_save = ''
            field_width = 0
            field_info_str = ''
            for i, field in reversed(list(enumerate(register))):
                if field != field_save:
                    if field_width > 0:
                        field_info_str += '%s[%d:0]' % (field_save, field_width)
                        fields.append(field_info_str)
                        field_info_str = ''
                    elif i < (cpu['dwidth'] - 1):
                        field_info_str += '%s[0]' % field_save
                        fields.append(field_info_str)
                    field_info_str = ''
                    field_save = field
                    field_width = 0
                else:
                    field_width += 1
            if field_width > 0:
                field_info_str += '%s[%d:0]' % (field_save, field_width)
            else:
                field_info_str += '%s[0]' % field_save
            fields.append(field_info_str)
            field_regs = ', '.join(fields)
            reg_name = '%s_reg' % reg['name']
            reg_name = reg_name.ljust(max_len)
            assign.append("  assign %s = {%s};" % (reg_name, field_regs))

        assign.sort()
        print '\n'.join(assign)
       
    def rtl_readback(self, cpu, block):
        print '\n'
        print '  // ------------------------'
        print '  // Read-back Path'
        print '  // ------------------------\n'

        print '  always_comb begin'
        print '    response = avalon_bus_pkg::OKAY;'
        print '    case ( bus.addr )\n'

        # Assign fields to their corresponding registers
        base = 0 # for now
        base_addr  = base + block['base_addr']
        for reg in block['csr']['registers']:
            print "{0:8}'h{1:0{2}x}: bus.rdata = {3}_reg".format(cpu['awidth'], reg['address'], cpu['awidth']/4, reg['name'])

        print ''
        print '      default: begin'
        print "        bus.rdata = 32'hDEADBEEF;"
        print '        response  = avalon_bus_pkg::DECODE_ERROR;'
        print '      end\n'

        print '    endcase'
        print '  end'


    def rtl_endmodule(self):
        print '\nendmodule;'

    def rtl_footer(self):

        now = time.localtime()
        date = "%s/%02d/%02d" %(str(now.tm_year), now.tm_mon, now.tm_mday)

        print "\n"
	print "// -------------------------------------------------------------------------------------------------"
	print "// Release History"
	print "//   VERSION DATE       AUTHOR           DESCRIPTION"
	print "// --------- ---------- ---------------- -----------------------------------------------------------"
	print "//   1.0     %s csr script       Control Status Register Generation." % date
	print "//                                       Do not modify. Changes may be overwritten."
	print "// -------------------------------------------------------------------------------------------------\n"
  

def print_txt_csr(reg, base_addr, awidth, dwidth):
    margin = 12
    reg_addr = base_addr + reg['address']
    addr_disp_len = awidth/4 + 2
    data_disp_len = dwidth/4 + 2

    addr = "{0:#0{1}x}".format(reg_addr, addr_disp_len)

    print ''
    print '{:>11}  {} - {}'.format(addr, reg['name'], reg['desc'])

    lines = []

    # Line #1
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

    # Print Header for Register
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

    # print the header
    for line in lines:
        print ' '*margin,
        print ''.join(line)
      
    for field in reg['fields']:
        bit_pos    = '[%s]' % field['bit_pos']
        por        = int(field['por'])
        por        = "{0:#0{1}x}".format(por, data_disp_len)
        attributes = ','.join(field['attributes'])

        data = []
        data.append(bit_pos)
        data.append(field['name'])
        data.append(por)
        data.append(attributes)

        print ' '*margin,

        # Right justify first column (bit-width)
        line = '{:>8}{}'.format(bit_pos,' ') 

        for i in range(1, len(data)):
            line = line + '{:{}s}{}'.format(data[i], col_width[i], ' ')

        # Deal with the description which may use several lines
        line_margin = margin + len(line) + 1
        desc = field['desc'].split('\n')
        line = line + desc[0]
        print line
        if len(desc) > 1:
            for d in range(1,len(desc)):
                line = ' ' * line_margin + desc[d]
                print line
    print '\n'

  
def print_txt_blocks(blocks, base=0, path=''):
    for block in blocks:
        base_addr  = base + block['base_addr']
        file = path + block['file']
        block_path, block_file = os.path.split(file)

        print '    BLOCK: %s - %s (%s)' % ( block['csr']['name'], block['csr']['desc'], file)
        print '    ' + '─' * 80
        print '    Base Address:  %s' % str(hex(base_addr))

        awidth = block['csr']['awidth']
        dwidth = block['csr']['dwidth']
        print '    Address Width: %s' % awidth
        print '    Data Width:    %s' % dwidth

        for reg in block['csr']['registers']:
            print_txt_csr(reg, base_addr, awidth, dwidth)

        try:
            for b in block['csr']['blocks']:
                print_txt_blocks(block['csr']['blocks'], base=base_addr, path=block_path+'/')
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

    print_txt_blocks(blocks) 

def print_rtl(csr):

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

  csr_map = CsrMap(args.yaml)

  if args.rtl:
      csr_map.rtl_gen()

  if args.txt:
      print_txt(csr_map)

  pp = pprint.PrettyPrinter(indent=2)
# pp.pprint(csr_map.map)


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
  
# print "┌ ─ ─ ┬ ─ ─ ┬ ─ ─ ┬ ─ ─ ┐"
# print "│     │     │     │     │"
# print "└ ─ ─ ┴ ─ ─ ┴ ─ ─ ┴ ─ ─ ┘"
# print "├ ─ ─ ┼                 ┤"
# print "│     │     │     │     │"
# print "└ ─ ─ ┴ ─ ─ ┴ ─ ─ ┴ ─ ─ ┘"
