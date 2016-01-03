// --------------------------------------------------------------------------------------------------
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

package blk_name_csr_pkg;

  localparam REG_X_ADDR         = 20'h0020;
  localparam REG_Y_ADDR         = 20'h0021;
  localparam REG_Z_ADDR         = 20'h0022;

  localparam REG_X_FIELD_A_MSB  = 7;
  localparam REG_X_FIELD_A_LSB  = 0;
  localparam REG_X_FIELD_B_MSB  = 15;
  localparam REG_X_FIELD_B_LSB  = 8;
  localparam REG_X_FIELD_C_MSB  = 15;
  localparam REG_X_FIELD_C_LSB  = 8;

  localparam ADDR_DECODE_ERROR  = 32'hDEADBEEF;

endpackage

