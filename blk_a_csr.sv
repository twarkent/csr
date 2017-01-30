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
// FILE NAME      : blk_a_csr.sv
// CURRENT AUTHOR : csr.py script
// --------------------------------------------------------------------------------------------------
// KEYWORDS: blk_a control status registers.
// --------------------------------------------------------------------------------------------------
// PURPOSE:  nios blk_a control status registers.
// --------------------------------------------------------------------------------------------------
// Reuse Issues:
//   Reset Strategy:      Asynchronous
//   Clock Domains:       clk
//   Critical Timing:     None
//   Test Features:       None
//   Asynchronous I/F:    None
//   Synthesizable:       Yes
// --------------------------------------------------------------------------------------------------

module blk_a_csr 

  import avalon_bus_pkg::*, blk_a_csr_pkg::*;   // only a single import statement allowed ??

  (
    // nios bus interface ---------------
    interface bus,

    // CSR Signals --------------------------------------

    // Read-Only Register
    input  logic   [3:0] reg_a_field_0,
    input  logic   [7:0] reg_a_field_1,
    input  logic   [1:0] reg_a_field_2,

    // Read/Write Register
    output logic  [15:0] reg_b_field_0,
    output logic  [15:0] reg_b_field_1,

    // Write-Only Register
    output logic  [15:0] reg_c_field_0,
    output logic  [15:0] reg_c_field_1,

    // RW Register with Write-Pulse
    output logic   [7:0] reg_d_field_0,
    output logic         reg_d_field_0_wp,

    // RW Register with Write-Pulse-Acknowledge
    output logic   [7:0] reg_e_field_0,
    output logic         reg_e_field_0_wp,
    input  logic         reg_e_field_0_wpa,

    // RW Register with Read-Pulse (Could also be a RO reg)
    output logic   [7:0] reg_f_field_0,
    output logic   [7:0] reg_f_field_0_rp,

    // RW Register with Read-Pulse-Acknowledge (Could also be a RO reg)
    output logic   [7:0] reg_g_field_0,
    output logic   [7:0] reg_g_field_0_rp,
    input  logic   [7:0] reg_g_field_0_rpa,

    // W1C
    input  logic  [31:0] reg_h_field_0,
    output logic  [31:0] reg_h_field_0_w1c,

    // W1S (Only set bits when writing a '1'. All other remain unchanged)
    input  logic  [31:0] reg_i_field_0,
    output logic  [31:0] reg_i_field_0_w1s,

    // Clear-on-read
    input  logic  [31:0] reg_j_field_0,
    output logic         reg_j_field_0_cor;
    
    // Increment-on-read
    output logic  [31:0] reg_k_field_0,

    // Increment-on-read saturate
    output logic  [31:0] reg_l_field_0,

    // Decrement-on-read
    output logic  [31:0] reg_m_field_0,

    // Decrement-on-read saturate
    output logic  [31:0] reg_n_field_0,

    // SUB(n) Register wider than DWIDTH
    output logic [127:0] reg_o_field_0,

    // External FIFO read-access
    output logic         field_p_rd,
    input  logic  [31:0] field_p_rdata,
    input  logic         field_p_empty,

    // External FIFO write-access
    output logic         field_q_wr,
    output logic  [31:0] field_q_wdata,
    input  logic         field_q_full,

    // External FIFO read/write-access
    output logic         field_r_rd,
    output logic         field_r_wr,
    input  logic         field_r_full,
    input  logic         field_r_empty,
    input  logic  [31:0] field_r_rdata,
    output logic  [31:0] field_r_wdata,
    
    // External RAM read-access
    output logic   [7:0] field_s_addr,
    input  logic  [31:0] field_s_rdata,

    // External RAM write-access
    output logic         field_t_wr,
    output logic   [7:0] field_t_addr,
    output logic  [31:0] field_t_wdata,

    // External RAM read/write-access
    output logic         field_u_wr,
    output logic   [7:0] field_u_addr,
    input  logic  [31:0] field_u_rdata,
    output logic  [31:0] field_u_wdata,

    // Read-Modify-Write
    output logic   [7:0] field_v,
    output logic         field_v_lock,

  );


  // ---------------------------------------------------------------------------
  // Signal Declarations
  // ---------------------------------------------------------------------------
  logic  [63:0] reserved;          // DWIDTH wide

  logic  [63:0] reg_a;
  logic  [63:0] reg_b;
  logic  [63:0] reg_d;
  logic  [63:0] reg_e;
  logic  [63:0] reg_f;
  logic  [63:0] reg_g;
  logic  [63:0] reg_h;
  logic  [63:0] reg_i;
  logic  [63:0] reg_j;
  logic  [63:0] reg_k;
  logic  [63:0] reg_l;
  logic  [63:0] reg_m;
  logic  [63:0] reg_n;

  logic  [63:0] reg_o_sub_0;
  logic  [63:0] reg_o_sub_1;


  // ---------------------------------------------------------------------------
  // Signal Assignments
  // ---------------------------------------------------------------------------
  assign reserved = '0; // use as a place-holder for undefined register bits.

  assign reg_a = {reserved[63:18], reg_a_field_2, reg_a_field_1, reserved[7:4], reg_0_field_0};
  assign reg_b = {reserved[63:32], reg_b_field_1, reg_b_field_0};
  assign reg_d = {reserved[63:8],  reg_d_field_0};
  assign reg_e = {reserved[63:8],  reg_e_field_0};
  assign reg_f = {reserved[63:8],  reg_f_field_0};
  assign reg_g = {reserved[63:8],  reg_g_field_0};
  assign reg_h = {reserved[63:32], reg_h_field_0_w1c};
  assign reg_i = {reserved[63:32], reg_i_field_0_w1s};
  assign reg_j = {reserved[63:32], reg_j_field_0};
  assign reg_k = {reserved[63:32], reg_k_field_0};
  assign reg_l = {reserved[63:32], reg_l_field_0};
  assign reg_m = {reserved[63:32], reg_m_field_0};
  assign reg_n = {reserved[63:32], reg_n_field_0};

  assign reg_o_sub_0 = reg_o_field_0[63:0];
  assign reg_o_sub_1 = reg_o_field_0[127:64];


  // ------------------------
  // Write Path
  // ------------------------

  // reg_b: RW
  always_ff @(posedge bus.clk, posedge bus.rst) begin
    if ( bus.rst ) begin
      reg_b_field_0 <= REG_B_FIELD_0_POR; 
      reg_b_field_1 <= REG_B_FIELD_1_POR; 
    end else if (bus.wr && (bus.addr == REG_B_ADDR)) begin
      reg_b_field_0 <= bus.wdata[REG_B_FIELD_0_BIT_POS];
      reg_b_field_1 <= bus.wdata[REG_B_FIELD_1_BIT_POS];
    end
  end

  // reg_c: WO
  always_ff @(posedge bus.clk, posedge bus.rst) begin
    if ( bus.rst ) begin
      reg_c_field_0 <= REG_C_FIELD_0_POR; 
      reg_c_field_1 <= REG_C_FIELD_1_POR; 
    end else if (bus.wr && (bus.addr == REG_C_ADDR)) begin
      reg_c_field_0 <= bus.wdata[REG_C_FIELD_0_BIT_POS];
      reg_c_field_1 <= bus.wdata[REG_C_FIELD_1_BIT_POS];
    end
  end

  // reg_d: RW, WP 
  always_ff @(posedge bus.clk, posedge bus.rst) begin
    if ( bus.rst ) begin
      reg_d_field_0    <= REG_D_FIELD_0_POR; 
      reg_d_field_0_wp <= '0;
    end else if (bus.wr && (bus.addr == REG_D_ADDR)) begin
      reg_d_field_0 <= bus.wdata[REG_D_FIELD_0_BIT_POS];
      reg_d_field_0_wp <= '1;
    end else
      reg_d_field_0_wp <= '0;
  end

  // reg_e: RW, WPA
  always_ff @(posedge bus.clk, posedge bus.rst) begin
    if ( bus.rst ) begin
      reg_e_field_0    <= REG_E_FIELD_0_POR; 
      reg_e_field_0_wp <= '0;
    end else if (bus.wr && (bus.addr == REG_E_ADDR)) begin
      reg_e_field_0 <= bus.wdata[REG_E_FIELD_0_BIT_POS];
      reg_e_field_0_wp <= '1;
    end else if ( reg_e_field_0_wpa )
      reg_e_field_0_wp <= '0;
  end

  // reg_f: RW, RP 
  always_ff @(posedge bus.clk, posedge bus.rst) begin
    if ( bus.rst ) begin
      reg_f_field_0    <= REG_F_FIELD_0_POR; 
      reg_f_field_0_rp <= '0;
    end else if (bus.wr && (bus.addr == REG_F_ADDR)) begin
      reg_f_field_0 <= bus.wdata[REG_F_FIELD_0_BIT_POS];
      reg_f_field_0_rp <= '1;
    end else
      reg_f_field_0_rp <= '0;
  end

  // reg_g: RW, RPA
  always_ff @(posedge bus.clk, posedge bus.rst) begin
    if ( bus.rst ) begin
      reg_g_field_0    <= REG_G_FIELD_0_POR; 
      reg_g_field_0_rp <= '0;
    end else if (bus.wr && (bus.addr == REG_G_ADDR)) begin
      reg_g_field_0 <= bus.wdata[REG_G_FIELD_0_BIT_POS];
      reg_g_field_0_rp <= '1;
    end else if ( reg_g_field_0_rpa )
      reg_g_field_0_rp <= '0;
  end

  // reg_h: RW, W1C
  always_ff @(posedge bus.clk, posedge bus.rst) begin
    if ( bus.rst ) begin
      reg_h_field_0_w1c <= REG_H_FIELD_0_POR; 
    end else if ( |reg_h_field_0 )
      reg_h_field_0_w1c <= reg_h_field_0_w1c | reg_h_field_0,
    end else if (bus.wr && (bus.addr == REG_H_ADDR)) begin
      reg_h_field_0_w1c <= reg_h_field_0_w1c & ~bus.wdata[REG_H_FIELD_0_BIT_POS];
  end

  // reg_i: RW, W1C
  always_ff @(posedge bus.clk, posedge bus.rst) begin
    if ( bus.rst ) begin
      reg_i_field_0_w1s <= REG_H_FIELD_0_POR; 
    end else if ( |reg_i_field_0 )
      reg_i_field_0_w1s <= reg_i_field_0_w1s | reg_i_field_0,
    end else if (bus.wr && (bus.addr == REG_H_ADDR)) begin
      reg_i_field_0_w1s <= reg_i_field_0_w1s | bus.wdata[REG_I_FIELD_0_BIT_POS];
  end

  // reg_j: COR
  always_ff @(posedge bus.clk, posedge bus.rst) begin
    if ( bus.rst ) begin
      reg_j_field_0_cor <= '0;
    end else if (bus.rd && (bus.addr == REG_H_ADDR)) begin
      reg_j_field_0_cor <= '1;
    else
      reg_j_field_0_cor <= '0;
  end

  // reg_k: IOR
  always_ff @(posedge bus.clk, posedge bus.rst) begin
    if ( bus.rst ) begin
      reg_k_field_0 <= REG_K_FIELD_0_POR;
    end else if (bus.wr && (bus.addr == REG_K_ADDR)) begin
      reg_k_field_0 <= bus.wdata[REG_K_FIELD_0_BIT_POS];
    end else if (bus.rd && (bus.addr == REG_K_ADDR)) begin
      reg_k_field_0 <= reg_k_field_0 + 1'b1;
  end

  // reg_l: IOR
  always_ff @(posedge bus.clk, posedge bus.rst) begin
    if ( bus.rst ) begin
      reg_l_field_0 <= REG_L_FIELD_0_POR;
    end else if (bus.wr && (bus.addr == REG_L_ADDR)) begin
      reg_l_field_0 <= bus.wdata[REG_L_FIELD_0_BIT_POS];
    end else if (bus.rd && (bus.addr == REG_K_ADDR) && ~&reg_l_field_0) begin
      reg_l_field_0 <= reg_l_field_0 + 1'b1;
  end

  // reg_m: DOR
  always_ff @(posedge bus.clk, posedge bus.rst) begin
    if ( bus.rst ) begin
      reg_m_field_0 <= REG_M_FIELD_0_POR;
    end else if (bus.wr && (bus.addr == REG_M_ADDR)) begin
      reg_m_field_0 <= bus.wdata[REG_M_FIELD_0_BIT_POS];
    end else if (bus.rd && (bus.addr == REG_M_ADDR)) begin
      reg_m_field_0 <= reg_m_field_0 - 1'b1;
  end

  // reg_n: IOR
  always_ff @(posedge bus.clk, posedge bus.rst) begin
    if ( bus.rst ) begin
      reg_n_field_0 <= REG_N_FIELD_0_POR;
    end else if (bus.wr && (bus.addr == REG_N_ADDR)) begin
      reg_n_field_0 <= bus.wdata[REG_N_FIELD_0_BIT_POS];
    end else if (bus.rd && (bus.addr == REG_N_ADDR) && |reg_n_field_0) begin
      reg_n_field_0 <= reg_n_field_0 - 1'b1;
  end

  // reg_o: RW, SUB
  always_ff @(posedge bus.clk, posedge bus.rst) begin
    if ( bus.rst )
      reg_o_field_0 <= REG_O_FIELD_0_POR;
    else if (bus.wr && (bus.addr == REG_O_FIELD_0_SUB_0_ADDR))
      reg_o_field_0[63:0]   <= bus.wdata[REG_O_FIELD_0_SUB_0_BIT_POS];
    else if (bus.wr && (bus.addr == REG_O_FIELD_0_SUB_1_ADDR))
      reg_o_field_0[127:64] <= bus.wdata[REG_O_FIELD_0_SUB_1_BIT_POS];
  end

  // ------------------------
  // Read-back Path
  // ------------------------

  always_comb begin

    bus.response      = avalon_bus_pkg::OKAY;
    bus.lock          = '0;
    bus.wait_response = '0;

    case (bus.addr)

      REG_A_ADDR:       bus.rdata = reg_a;
      REG_B_ADDR:       bus.rdata = reg_b;
      REG_D_ADDR:       bus.rdata = reg_d;
      REG_E_ADDR:       bus.rdata = reg_e;
      REG_F_ADDR:       bus.rdata = reg_f;
      REG_G_ADDR:       bus.rdata = reg_g;
      REG_H_ADDR:       bus.rdata = reg_h;
      REG_I_ADDR:       bus.rdata = reg_i;
      REG_J_ADDR:       bus.rdata = reg_j;
      REG_K_ADDR:       bus.rdata = reg_k;
      REG_L_ADDR:       bus.rdata = reg_l;
      REG_M_ADDR:       bus.rdata = reg_m;
      REG_N_ADDR:       bus.rdata = reg_n;
      REG_O_SUB_0_ADDR: bus.rdata = reg_o_sub_0;
      REG_O_SUB_1_ADDR: bus.rdata = reg_o_sub_1;

      default: begin
        bus.rdata    = 32'hDEADBEEF;
        bus.response = avalon_bus_pkg::DECODE_ERROR;
      end

    endcase
  end

endmodule;


// -------------------------------------------------------------------------------------------------
// Release History
//   VERSION DATE       AUTHOR           DESCRIPTION
// --------- ---------- ---------------- -----------------------------------------------------------
//   1.0     2017/01/28 csr script       Control Status Register Generation.
//                                       Do not modify. Changes may be overwritten.
// -------------------------------------------------------------------------------------------------

