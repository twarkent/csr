package avalon_bus_pkg;

  typedef enum {OKAY, RESERVED, SLAVE_ERROR, DECODE_ERROR} response_te; // te: typedef enum

  interface avalon_bus #(parameter AWIDTH=20, DWIDTH=32, BE_WIDTH=4) (input clk, rst);
    logic   [AWIDTH-1:0] addr;
    logic [BE_WIDTH-1:0] byte_enable;
    logic   [DWIDTH-1:0] wdata;
    logic   [DWIDTH-1:0] rdata;
    logic                rdata_valid;
    logic                wr;
    logic                rd;
    response_te          response;
    logic                lock;
    logic                wait_request;

    // Check for valid parameter values at elaboration
    generate
      if ( (DWIDTH!=8) || (DWIDTH!=16) || (DWIDTH!=32) || (DWIDTH!=64) || (DWIDTH!=128) )
        $fatal(1, "Parameter DWIDTH has an unsupported value of %0d", DWIDTH);
      if ( (BE_WIDTH!=0) && (DWIDTH/8!=BE_WIDTH) )
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
      input  wait_request
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

  endinterface

endpackage

