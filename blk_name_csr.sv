// --------------------------------------------------------------------------------------------------
// Copyright (c) 2011  MTI Laboratory, Inc. All rights reserved.
//
//   This file includes unpublished proprietary source code of MTI Laboratory.  The copyright 
//   notice above does not evidence any actual or intended publication of such source code. You
//   shall not disclose such source code (or any related information) and shall use it only in 
//   accordance with the terms of the license or confidentiality agreements you have entered into 
//   with MTI Laboratory.  Distributed to licensed users or owners.
//
// --------------------------------------------------------------------------------------------------
// FILE NAME      : top_control_np0_csr.v
// CURRENT AUTHOR : csr script
// --------------------------------------------------------------------------------------------------
// KEYWORDS: top_control control status registers.
// --------------------------------------------------------------------------------------------------
// PURPOSE:  np0 top_control block control status registers.
// --------------------------------------------------------------------------------------------------
// Parameters
//   NAME              DEFAULT      DESCRIPTION
//   ----------------- ------------ -----------------------------------------------------------------
//   NP_AWIDTH         16           CPU address-bus bit-width
//   NP_DWIDTH         32           CPU data-bus bit-width
// --------------------------------------------------------------------------------------------------
// Reuse Issues:
//   Reset Strategy:      Synchronous
//   Clock Domains:       np_clk
//   Critical Timing:     None
//   Test Features:       None
//   Asynchronous I/F:    None
//   Synthesizable:       Yes
// --------------------------------------------------------------------------------------------------

module blk_name_csr 

  import avalon_bus_pkg::*, blk_name_csr_pkg::*;

  (
    // bus interface ----------------
    interface avalon_bus_pkg::bus,

    // CSR Signals -------------------------------
    output     [REG_X_FIELD_A_WIDTH-1:0] reg_v_field_a,

    input      [REG_W_FIELD_A_WIDTH-1:0] reg_w_field_a,

    output     [REG_X_FIELD_A_WIDTH-1:0] reg_x_field_a,
    output     [REG_X_FIELD_B_WIDTH-1:0] reg_x_field_b,
    output                               reg_x_field_b_wp,
    output     [REG_X_FIELD_C_WIDTH-1:0] reg_x_field_c,
    output                               reg_x_field_c_wp,
    input                                reg_x_field_c_wpa,

    output     [REG_Y_FIELD_A_WIDTH-1:0] reg_y_field_a,
    output                               reg_y_field_a_rp,
    input                                reg_y_field_a_rpa,
    output     [REG_Y_FIELD_B_WIDTH-1:0] reg_y_field_b,
    output                               reg_y_field_b_rp,
    output                               reg_y_field_b_wp,
    output     [REG_Y_FIELD_C_WIDTH-1:0] reg_y_field_c,
    output                               reg_y_field_c_rp,
    output                               reg_y_field_c_wp,
    input                                reg_y_field_c_wpa,

    input                                reg_z_field_a,
    output [REG_Z_FIELD_A_CTR_WIDTH-1:0] reg_z_field_a_ctr,
    input                                reg_z_field_b,
    output [REG_Z_FIELD_B_CTR_WIDTH-1:0] reg_z_field_b_ctr,
    input                                reg_z_field_c,
    output [REG_Z_FIELD_C_CTR_WIDTH-1:0] reg_z_field_c_ctr,
    input                                reg_z_field_d,
    output [REG_Z_FIELD_D_CTR_WIDTH-1:0] reg_z_field_d_ctr
  );


  // ---------------------------------------------------------------------------
  // Signal Declarations
  // ---------------------------------------------------------------------------
  logic [31:0] undefined;                  // Used for field spacing
  logic [31;0] rdata;
  logic [31:0] reg_v;
  logic [31:0] reg_w;
  logic [31:0] reg_x;
  logic [31:0] reg_y;
  logic [31:0] reg_z;

  logic [REG_W_FIELD_A_WIDTH-1:0] reg_w_field_a_w1c;

  avalon_bus_pkg::response_te response;


  // ---------------------------------------------------------------------------
  // Signal Assignments
  // ---------------------------------------------------------------------------
  assign undefined = '0;  // use as a place-holder for undefined register bits.

  assign reg_x = {reg_x_field_c, undefined[7:0], reg_x_field_b, reg_x_field_a};
  assign reg_y = {reg_y_field_c, reg_y_field_b, undefined[3:0], reg_y_field_a};
  assign reg_z = {reg_z_field_c, reg_z_field_b_ctr, reg_z_field_a_ctr};


  // ---------------------------------------------------------------------------
  // Read-back Path
  // ---------------------------------------------------------------------------
  always_comb begin
    response = OKAY;
    case ( bus.addr )

      blk_name_csr_pkg::REG_X_ADDR: rdata = reg_x;     
      blk_name_csr_pkg::REG_Y_ADDR: rdata = reg_y;     
      blk_name_csr_pkg::REG_Z_ADDR: rdata = reg_z;     

      default: begin
        rdata    = blk_name_csr_pkg::ADDR_DECODE_ERROR;
        response = avalon_bus_pkg::DECODE_ERROR;
      end
    endcase
  end

  always_ff @(posedge bus.clk, posedge bus.rst)
    if (bus.rst) begin
      bus.rdata    <= '0;
      bus.response <= OKAY;
    end else begin
      bus.rdata    <= rdata;
      bus.response <= response;
    end


  // ----------------------------------------
  // Register: reg_x
  // ----------------------------------------

  // Field: field_a (RW or WO) -- WO is not included in read-back mux
  always_ff @(posedge bus.clk, posedge bus.rst)
    if (bus.rst)
      reg_x_field_a <= '0
    else if ( bus.wr && (bus.addr==REG_X_ADDR) )
      reg_x_field_a <= bus.wdata[REG_X_FIELD_A_MSB:REG_X_FIELD_A_LSB];

  // Field: field_b (RW, WP)
  always_ff @ (posedge bus.clk, posedge bus.rst )
    if (bus.rst) begin
      reg_x_field_b    <= '0
      reg_x_field_b_wp <= '0; 
    end else begin
     reg_x_field_a_wp <= '0;
      if ( bus.wr && (bus.addr==REG_X_ADDR) ) begin
        reg_x_field_b_wp <= '1;
        reg_x_field_b    <= bus.wdata[REG_X_FIELD_A_MSB:REG_X_FIELD_A_LSB];
      end
    end

  // Field: field_c (RW, WPA)
  always_ff @ (posedge bus.clk, posedge bus.rst )
    if (bus.rst) begin
      reg_x_field_c    <= '0
      reg_x_field_c_wp <= '0; 
    end else begin
      reg_x_field_c_wp <= '0;
      if ( bus.wr && (bus.addr==REG_X_ADDR) ) begin
        reg_x_field_c_wp <= '1;
        reg_x_field_c    <= bus.wdata[REG_X_FIELD_A_MSB:REG_X_FIELD_A_LSB];
      end else if (reg_x_field_c_wpa)
        reg_x_field_c <= '0;
    end


  // ----------------------------------------
  // Register: reg_y
  // ----------------------------------------

  // Field: reg_y_field_a (RW, RPA)
  always_ff @(posedge bus.clk, posedge bus.rst )
    if (bus.rst) begin
      reg_y_field_a    <= '0
      reg_y_field_a_rp <= '0; 
    end else begin
      reg_y_field_a_rp <= '0;
      if (bus.addr==REG_Y_ADDR) begin
        if (bus.wr) reg_y_field_a    <= bus.wdata[REG_Y_FIELD_A_MSB:REG_Y_FIELD_A_LSB];
        if (bus.rd) reg_y_field_a_rp <= '1;
      end else if (reg_y_field_a_rpa)
        reg_y_field_a <= '0;
    end

  // Field: reg_y_field_b (RW, RP, WP)
  always_ff @(posedge bus.clk, posedge bus.rst )
    if (bus.rst) begin
      reg_y_field_b    <= '0
      reg_y_field_b_rp <= '0; 
      reg_y_field_b_wp <= '0; 
    end else begin
      reg_y_field_a_rp <= '0;
      reg_y_field_a_wp <= '0;
      if (bus.addr==REG_Y_ADDR) begin
        if (bus.wr) begin
          reg_y_field_b    <= bus.wdata[REG_Y_FIELD_B_MSB:REG_Y_FIELD_B_LSB];
          reg_y_field_b_wp <= '1;
        end else if (bus.rd) begin
          reg_y_field_b_rp <= '1;
        end
      end
    end

  // Field: reg_y_field_c (RW, RP, WPA)
  always_ff @ (posedge bus.clk, posedge bus.rst )
    if (bus.rst) begin
      reg_y_field_c    <= '0
      reg_y_field_c_rp <= '0; 
      reg_y_field_c_wp <= '0; 
    end else begin
      reg_y_field_c_rp <= '0;
      reg_y_field_c_wp <= '0;
      if (addr==REG_X_ADDR) begin
        if (wr) begin
          reg_y_field_c    <= wdata[REG_X_FIELD_A_MSB:REG_X_FIELD_A_LSB];
          reg_y_field_c_wp <= '1;
        end else if (rd) begin
          reg_y_field_c_rp <= '1;
        end
      end else if (reg_y_field_c_wpa) begin
        reg_y_field_c <= '0;
      end
    end

  // ----------------------------------------
  // Register: reg_z
  // ----------------------------------------

  // Field: reg_z_field_a (INC, COW)
  always_ff @ (posedge bus.clk, posedge bus.rst)
    if (bus.rst) begin
      reg_z_field_a_ctr <= '0
    end else begin
      if (reg_z_field_a)
        reg_z_field_a_ctr <= reg_z_field_a_ctr + 1'b1;
      else if ( bus.wr && (bus.addr==REG_Z_ADDR) )
        reg_z_field_a_ctr <= '0;
    end

  // Field: field_b (INCS, COR)
  always_ff @ (posedge bus.clk, posedge bus.rst)
    if (bus.rst) begin
      reg_z_field_b_ctr <= '0
    end else begin
      if (reg_z_field_b && ~(&reg_z_field_b_ctr))
          reg_z_field_b_ctr <= reg_z_field_b_ctr + 1'b1;
      else if ( bus.rd && (bus.addr==REG_Z_ADDR) )
        reg_z_field_b_ctr <= '0;
    end

  // Field: reg_z_field_c (DECS, SOW)
  always_ff @ (posedge bus.clk, posedge bus.rst)
    if (bus.rst) begin
      reg_z_field_c_ctr <= '0
    end else begin
      if (reg_z_field_c && |reg_z_field_c_ctr)
        reg_z_field_c_ctr <= reg_z_field_c_ctr - 1'b1;
      else if ( bus.wr && (bus.addr==REG_Z_ADDR) )
        reg_z_field_c_ctr <= '1;
    end

  // Field: reg_z_field_d (RW, DECS)
  always_ff @ (posedge bus.clk, posedge bus.rst)
    if (bus.rst) begin
      reg_z_field_d_ctr <= '0
    end else begin
      if (reg_z_field_d && |reg_z_field_d_ctr)
          reg_z_field_d_ctr <= reg_z_field_d_ctr - 1'b1;
      else if ( bus.wr && (bus.addr==REG_Z_ADDR) )
        reg_z_field_d_ctr <= bus.wdata[REG_Z_FIELD_D_MSB:REG_Z_FIELD_D_LSB];
    end
    
  // Field: reg_w_field_a (W1C)
  always_ff @(posedge bus.clk, posedge bus.rst)
    if (bus.rst)
      reg_w_field_a_w1c <= '0;
    else if ( bus.wr && (bus.addr==REG_W_ADDR) )
      reg_w_field_a_w1c <= reg_w_field_a_w1c & ~bus.wdata[REG_W_FIELD_A_MSB:REG_W_FIELD_A_LSB];
    else 
      reg_w_field_a_w1c <= reg_w_field_a_w1c | reg_w_field_a;

  // Field: reg_v_field_a (SUB)
  always_ff @(posedge bus.clk, posedge bus.rst)
    if (bus.rst)
      reg_v_field_a <= '0;
    else begin
      if ( bus.wr && (bus.addr==REG_V_SUB0_ADDR) )
        reg_v_field_a[reg_v_sub0_msb:reg_v_sub0_lsb] <= bus.wdata[reg_v_sub0_bus_msb:reg_v_sub0_bus_lsb];
      else if ( bus.wr && (bus.addr==REG_V_SUB1_ADDR) )
        reg_v_field_a[reg_v_sub1_msb:reg_v_sub1_lsb] <= bus.wdata[reg_v_sub1_bus_msb:reg_v_sub1_bus_lsb];
      else if ( bus.wr && (bus.addr==REG_V_SUB2_ADDR) )
        reg_v_field_a[reg_v_sub2_msb:reg_v_sub2_lsb] <= bus.wdata[reg_v_sub2_bus_msb:reg_v_sub2_bus_lsb];
    end


endmodule

// --------------------------------------------------------------------------------------------------
// Release History
//   VERSION DATE        AUTHOR            DESCRIPTION
// --------- ----------- ----------------- ----------------------------------------------------------
//   1.0     2011/11/15  csr script        Do not modify. Changes may be overwritten.
// --------------------------------------------------------------------------------------------------

