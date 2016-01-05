module TOP#
  (
   parameter STEP = 10
   ) (
    CLK,
    RST_X
);
  input CLK;
  input RSTX;
  input [2:0] width0;
  input [31:2] width1;
  input [63:0] width2;
  input [127:0] width3;
  output [2:0] width0;
  output [31:2] width1;
  output [63:0] width2;
  output [127:0] width3;
  inout [2:0] width0;
  inout [31:2] width1;
  inout [63:0] width2;
  inout [127:0] width3;
  reg [3:0] cnt;
  wire [2:1] sig;
  integer i;
  wire [15:0] wire_array [31:0];
  reg [31:0] mem [127:0];

  parameter P_WIDTH = 128;

  initial begin
    cnt = 0;

    while ( cnt >= 0 ) begin: scope
        cnt = cnt - 1;
        disable scope;
    end
  end

  function [3:0] zero_cnt;
    input [15:0] data;
    integer index;
    begin
        zero_cnt = 0;
        for (index = 0; index <= 15; index = index + 1)
            if (data[index] == 0)
                zero_cnt = zero_cnt + 1;

        case ( zero_cnt )
            2'b0, 2'b1: zero_cnt = 0;
            2'b1: zero_cnt = 1;
            default: zero_cnt = 2;
        endcase
    end
  endfunction

  always @(posedge CLK or negedge RSTX) begin
    if(!RST_X) begin
      for ( i = 0; i <= 1; i = i + 1 ) begin
        cnt <= 0;
      end
    end else begin
      cnt <= cnt + 1;
    end
  end

  always @( cnt ) begin
    if ( cnt == 0 )
        a.b.sig = mem[0][1:0];
    else
        a.b.sig = zero_cnt( 16'd0 );
  end
endmodule
