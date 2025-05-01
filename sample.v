module sample(
    input       CLK,
    input       RSTX,
    input       REQ,
    output      ACK,
    input [7:0] DAT
);

`include "task.v"
`include "task2.v"

    initial begin
        sample1();
        sample2();
    end

    /*AUTO_LISP(defun getparam1 (strg)
     (string-match "_\\([^_]+\\)_[^_]+$" strg)
     (match-string 1 strg))
     */
    /*AUTO_LISP(defun getparam2 (strg)
     (string-match "_\\([^_]+\\)$" strg)
     (match-string 1 strg))
     */

    /* SUB AUTO_TEMPLATE (
     .ACK( w_aaa_@"(getparam1 vl-cell-name)"_@"(downcase vl-name)"[]),
     .CLK( w_bbb_@"(getparam2 vl-cell-name)"_@"(downcase vl-name)"[]),
     );*/

    SUB sub_111_222
        (/*AUTOINST*/
         // Outputs
         .ACK                           ( w_aaa_111_ack),        // Templated
         // Inputs
         .CLK                           ( w_bbb_222_clk),        // Templated
         .RSTX                          (RSTX),
         .REQ                           (REQ),
         .DAT                           (DAT[7:0]));

endmodule

// Local Variables:
// verilog-library-flags:("sub.v")
// End:
