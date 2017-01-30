// --------------------------------------------------------------------------------------------------'
// Copyright (c) 2017  CompanyName  All rights reserved.
//
//   This file includes unpublished proprietary source code of CompanyName.  The copyright
//   notice above does not evidence any actual or intended publication of such
//   source code. You shall not disclose such source code (or any related information)
//   and shall use it only in accordance with the terms of the license or confidentiality
//   agreements you have entered into with CompanyName. Distributed to licensed users or owners.
//
// --------------------------------------------------------------------------------------------------
// FILE NAME      : avalon_bus_pkg
// CURRENT AUTHOR : csr.py script
// --------------------------------------------------------------------------------------------------
// KEYWORDS: avalon_bus control status registers.
// --------------------------------------------------------------------------------------------------
// PURPOSE:  nios avalon_bus control status registers.
// --------------------------------------------------------------------------------------------------
// Reuse Issues:
//   Reset Strategy:      Asynchronous
//   Clock Domains:       clk
//   Critical Timing:     None
//   Test Features:       None
//   Asynchronous I/F:    None
//   Synthesizable:       Yes
// --------------------------------------------------------------------------------------------------

package avalon_bus_pkg;

  typedef enum {OKAY, RESERVED, SLAVE_ERROR, DECODE_ERROR} response_te;

  interface avalon_bus #(parameter AWIDTH=20, DWIDTH=64, BE_WIDTH=DWIDTH/8) (input clk, rst);
    logic   [AWIDTH-1:0] addr;
    logic [BE_WIDTH-1:0] byte_enable;
    logic   [DWIDTH-1:0] wdata;
    logic   [DWIDTH-1:0] rdata;
    logic                rdata_valid;
    logic                wr;
    logic                rd;
    logic                lock;
    logic                wait_response;
    response_te          response;

    // Check for valid parameter values during elaboration
    generate
      if ( (DWIDTH!=8) || (DWIDTH!=16) || (DWIDTH!=32) || (DWIDTH!=64) || (DWIDTH!=128) )
        $fatal(1, "Parameter DWIDTH has an unsupported value of %0d", DWIDTH);
      if ( DWIDTH/8 != BE_WIDTH )
        $fatal(1, "BE_WIDTH has an unsupported value of %0d", BE_WIDTH);
    endgenerate

    modport master (
      output addr,
      output wr,
      output rd,
      output wdata,
      input  rdata,
      input  rdata_valid,
      output byte_enable,
      input  response,
      output lock,
      input  wait_request,
    );

    modport slave (
      input  addr,
      input  wr,
      input  rd,
      input  wdata,
      output rdata,
      output rdata_valid,
      input  byte_enable,
      output response,
      input  lock,
      output wait_request
    );

  endinterface;
endpackage;
