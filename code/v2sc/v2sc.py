#-------------------------------------------------------------------------------
# codegen.py
#
# Code Generator from AST to Verilog HDL source code
#
# Copyright (C) 2013, Shinya Takamaeda-Yamazaki
# License: Apache 2.0
#-------------------------------------------------------------------------------
from __future__ import absolute_import
from __future__ import print_function
import sys
import os
import math
import re
import functools
from jinja2 import Environment, FileSystemLoader
from optparse import OptionParser

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pyverilog.utils.version
from pyverilog.vparser.parser import VerilogCodeParser
#from pyverilog.ast_code_generator.codegen import ASTCodeGenerator

from pyverilog.vparser.ast import *
from pyverilog.utils.op2mark import op2mark
from pyverilog.utils.op2mark import op2order

DEFAULT_TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__)) + '/template/'

#-------------------------------------------------------------------------------
try:
    import textwrap
    indent = textwrap.indent
except:
    def indent(text, prefix, predicate=None):
        if predicate is None: predicate = lambda x: x and not x.isspace()
        ret = []
        for line in text.split('\n'):
            if predicate(line):
                ret.append(prefix)
            ret.append(line)
            ret.append('\n')
        return ''.join(ret[:-1])

def indent_multiline_assign(text):
    ret = []
    texts = text.split('\n')
    if len(texts) <= 1:
        return text
    try:
        p = texts[0].index('=')
    except:
        return text
    ret.append(texts[0])
    ret.append('\n')
    ret.append(indent('\n'.join(texts[1:]), ' ' * (p + 2)))
    return ''.join(ret)


#-------------------------------------------------------------------------------
class ConvertVisitor(object):
    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.visit_default)
        return visitor(node)
    def visit_default(self, node):
        ret = []
        for c in node.children():
            ret.append(self.visit(c))
        return ''.join(ret)

def getfilename(node, suffix=''):
    return node.__class__.__name__.lower() + suffix + '.txt'

def escape(s):
    if s.startswith('\\'):
        return s + ' '
    return s

def del_paren(s):
    if s.startswith('(') and s.endswith(')'):
        return s[1:-1]
    return s

def del_space(s):
    return s.replace(' ', '')

class ASTCodeGenerator(ConvertVisitor):
    def __init__(self, indentsize=4, clock_name='CLK', reset_name='RSTX'):
        self.env = Environment(loader=FileSystemLoader(DEFAULT_TEMPLATE_DIR))
        self.indent = functools.partial(indent, prefix=' '*indentsize)
        self.clock_name = clock_name
        self.reset_name = reset_name

    def visit_process(self, node):
        method = 'visit_' + node.__class__.__name__ + '_process'
        visitor = getattr(self, method, self.visit_none)
        return visitor(node)

    def visit_declaration(self, node):
        method = 'visit_' + node.__class__.__name__ + '_declaration'
        visitor = getattr(self, method, self.visit_none)
        return visitor(node)

    def visit_argument(self, node):
        method = 'visit_' + node.__class__.__name__ + '_argument'
        visitor = getattr(self, method, self.visit_none)
        return visitor(node)

    def visit_parameter(self, node):
        method = 'visit_' + node.__class__.__name__ + '_parameter'
        visitor = getattr(self, method, self.visit_none)
        return visitor(node)

    def visit_none(self, node):
        return ''

    def visit_Source(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'description' : self.visit(node.description),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Description(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'definitions' : [ self.visit(definition) for definition in node.definitions ],
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_ModuleDef(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        portlist = self.indent(self.visit(node.portlist)) if node.portlist is not None else ''
        paramlist = [ self.visit(node.paramlist) ] if node.paramlist is not None else ()
        parameters = [ self.visit_parameter(item) for item in node.items ] if node.items else ()
        parameters += paramlist
        template_dict = {
            'modulename' : escape(node.name),
            'portlist' :  portlist,
            'parameters' : parameters,
            'declarationlist' : [ self.visit_declaration(item) for item in node.items ] if node.items else (),
            'processlist' : [ self.visit_process(item) for item in node.items ] if node.items else (),
            'items' : [ self.indent(self.visit(item)) for item in node.items ] if node.items else (),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Paramlist(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        params = [ self.visit_parameter(param).replace(';','') for param in node.params ]
        template_dict = {
            'params' : params,
            'len_params' : len(params),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Paramlist_parameter(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        params = [ self.visit_parameter(param).replace(';','') for param in node.params ]
        template_dict = {
            'params' : params,
            'len_params' : len(params),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Portlist(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        ports = [ self.visit(port) for port in node.ports ]
        template_dict = {
            'ports' : ports,
            'len_ports' : len(ports),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Port(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'name' : escape(node.name),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Width(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        msb = del_space(del_paren(self.visit(node.msb)))
        lsb = del_space(del_paren(self.visit(node.lsb)))
        template_dict = {
            'width': eval( msb + '-' + lsb + '+1' ),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Length(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        msb = del_space(del_paren(self.visit(node.msb)))
        lsb = del_space(del_paren(self.visit(node.lsb)))
        template_dict = {
            'width': eval( msb + '-' + lsb + '+1' ),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Identifier(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'name' : escape(node.name),
            'scope' : '' if node.scope is None else self.visit(node.scope).replace('.', '::'),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Value(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'value' : node.value,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Constant(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'value' : node.value,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_IntConst(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'value' : node.value,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_FloatConst(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'value' : node.value,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_StringConst(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'value' : node.value,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Variable(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        if node.width is None:
            width = '1'
            big = False
        else:
            width = self.visit(node.width)
            big = True if int(width) >= 64 else False
        template_dict = {
            'name' : escape(node.name),
            'width' : width,
            'signed' : node.signed,
            'big' : big,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Input(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        if node.width is None:
            width = '1'
            big = False
        else:
            width = self.visit(node.width)
            big = True if int(width) >= 64 else False
        template_dict = {
            'name' : escape(node.name),
            'width' : width,
            'signed' : node.signed,
            'big' : big,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Input_argument(self, node):
        filename = getfilename(node, '_argument')
        template = self.env.get_template(filename)
        if node.width is None:
            width = '1'
            big = False
        else:
            width = self.visit(node.width)
            big = True if int(width) >= 64 else False
        template_dict = {
            'name' : escape(node.name),
            'width' : width,
            'signed' : node.signed,
            'big' : big,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Output(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        if node.width is None:
            width = '1'
            big = False
        else:
            width = self.visit(node.width)
            big = True if int(width) >= 64 else False
        template_dict = {
            'name' : escape(node.name),
            'width' : width,
            'signed' : node.signed,
            'big' : big,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Output_argument(self, node):
        filename = getfilename(node, '_argument')
        template = self.env.get_template(filename)
        if node.width is None:
            width = '1'
            big = False
        else:
            width = self.visit(node.width)
            big = True if int(width) >= 64 else False
        template_dict = {
            'name' : escape(node.name),
            'width' : width,
            'signed' : node.signed,
            'big' : big,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Inout(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        if node.width is None:
            width = '1'
            big = False
        else:
            width = self.visit(node.width)
            big = True if int(width) >= 64 else False
        template_dict = {
            'name' : escape(node.name),
            'width' : width,
            'signed' : node.signed,
            'big' : big,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Inout_argument(self, node):
        filename = getfilename(node, '_argument')
        template = self.env.get_template(filename)
        if node.width is None:
            width = '1'
            big = False
        else:
            width = self.visit(node.width)
            big = True if int(width) >= 64 else False
        template_dict = {
            'name' : escape(node.name),
            'width' : width,
            'signed' : node.signed,
            'big' : big,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Tri(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        if node.width is None:
            width = '1'
            big = False
        else:
            width = self.visit(node.width)
            big = True if int(width) >= 64 else False
        template_dict = {
            'name' : escape(node.name),
            'width' : width,
            'signed' : node.signed,
            'big' : big,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Wire(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        if node.width is None:
            width = '1'
            big = False
        else:
            width = self.visit(node.width)
            big = True if int(width) >= 64 else False
        template_dict = {
            'name' : escape(node.name),
            'width' : width,
            'signed' : node.signed,
            'big' : big,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Reg(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        if node.width is None:
            width = '1'
            big = False
        else:
            width = self.visit(node.width)
            big = True if int(width) >= 64 else False
        template_dict = {
            'name' : escape(node.name),
            'width' : width,
            'signed' : node.signed,
            'big' : big,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_WireArray(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        if node.width is None:
            width = '1'
            big = False
        else:
            width = self.visit(node.width)
            big = True if int(width) >= 64 else False
        template_dict = {
            'name' : escape(node.name),
            'width' : width,
            'length' : self.visit(node.length),
            'signed' : node.signed,
            'big' : big,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_RegArray(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        if node.width is None:
            width = '1'
            big = False
        else:
            width = self.visit(node.width)
            big = True if int(width) >= 64 else False
        template_dict = {
            'name' : escape(node.name),
            'width' : width,
            'length' : self.visit(node.length),
            'signed' : node.signed,
            'big' : big,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Integer(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'name' : escape(node.name),
            'signed' : node.signed,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Real(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'name' : escape(node.name),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Genvar(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'name' : escape(node.name),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Ioport(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'first' : self.visit(node.first),
            'second' : '' if node.second is None else self.visit(node.second),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Parameter(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        value = self.visit(node.value)
        if node.width is None:
            width = '1'
            big = False
        else:
            width = '' if (value.startswith('"') and value.endswith('"')) else self.visit(node.width)
            big = True if int(width) >= 64 else False
        template_dict = {
            'name' : escape(node.name),
            'width' : width,
            'value' : value,
            'signed' : node.signed,
            'big' : big,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Localparam(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        value = self.visit(node.value)
        template_dict = {
            'name' : escape(node.name),
            'width' : '' if node.width is None or (value.startswith('"') and value.endswith('"')) else self.visit(node.width),
            'value' : value,
            'signed' : node.signed,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Decl(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'items' : [ self.visit(item) for item in node.list if item.__class__.__name__ != 'Parameter'],
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Decl_argument(self, node):
        filename = getfilename(node, '_argument')
        template = self.env.get_template(filename)
        items = [ self.visit_argument(item) for item in node.list if item.__class__.__name__ == 'Input' or item.__class__.__name__ == 'Output' or item.__class__.__name__ == 'Inout' ]
        template_dict = {
            'items' : items,
            'len_items' : len(items),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Decl_parameter(self, node):
        filename = getfilename(node, '_parameter')
        template = self.env.get_template(filename)
        items = [ self.visit(item) for item in node.list if item.__class__.__name__ == 'Parameter' ]
        template_dict = {
            'items' : items,
            'len_items' : len(items),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Concat(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        items = [ del_paren(self.visit(item)) for item in node.list ]
        template_dict = {
            'items' : items,
            'len_items' : len(items),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_LConcat(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        items = [ del_paren(self.visit(item)) for item in node.list ]
        template_dict = {
            'items' : items,
            'len_items' : len(items),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Repeat(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'value' : del_paren(self.visit(node.value)),
            'times' : del_paren(self.visit(node.times)),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Partselect(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'var' : self.visit(node.var),
            'msb' : del_space(del_paren(self.visit(node.msb))),
            'lsb' : del_space(del_paren(self.visit(node.lsb))),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Pointer(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'var' : self.visit(node.var),
            'ptr' : del_paren(self.visit(node.ptr)),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Lvalue(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'var' : del_paren(self.visit(node.var)),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Rvalue(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'var' : del_paren(self.visit(node.var)),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Operator(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        order = op2order(node.__class__.__name__)
        lorder = op2order(node.left.__class__.__name__)
        rorder = op2order(node.right.__class__.__name__)
        left = self.visit(node.left)
        right = self.visit(node.right)
        if ((not isinstance(node.left, (Sll, Srl, Sra,
                                        LessThan, GreaterThan, LessEq, GreaterEq,
                                        Eq, NotEq, Eql, NotEql))) and
            (lorder is not None and lorder <= order)):
            left = del_paren(left)
        if ((not isinstance(node.right, (Sll, Srl, Sra,
                                         LessThan, GreaterThan, LessEq, GreaterEq,
                                         Eq, NotEq, Eql, NotEql))) and
            (rorder is not None and order > rorder)):
            right = del_paren(right)
        template_dict = {
            'left' : left,
            'right' : right,
            'op' : op2mark(node.__class__.__name__),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_UnaryOperator(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        right = self.visit(node.right)
        template_dict = {
            'right' : right,
            'op' : op2mark(node.__class__.__name__),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Uplus(self, node):
        return self.visit_UnaryOperator(node)

    def visit_Uminus(self, node):
        return self.visit_UnaryOperator(node)

    def visit_Ulnot(self, node):
        return self.visit_UnaryOperator(node)

    def visit_Unot(self, node):
        return self.visit_UnaryOperator(node)

    def visit_Uand(self, node):
        return self.visit_UnaryOperator(node)

    def visit_Unand(self, node):
        return self.visit_UnaryOperator(node)

    def visit_Uor(self, node):
        return self.visit_UnaryOperator(node)

    def visit_Unor(self, node):
        return self.visit_UnaryOperator(node)

    def visit_Uxor(self, node):
        return self.visit_UnaryOperator(node)

    def visit_Uxnor(self, node):
        return self.visit_UnaryOperator(node)

    def visit_Power(self, node):
        return self.visit_Operator(node)

    def visit_Times(self, node):
        return self.visit_Operator(node)

    def visit_Divide(self, node):
        return self.visit_Operator(node)

    def visit_Mod(self, node):
        return self.visit_Operator(node)

    def visit_Plus(self, node):
        return self.visit_Operator(node)

    def visit_Minus(self, node):
        return self.visit_Operator(node)

    def visit_Sll(self, node):
        return self.visit_Operator(node)

    def visit_Srl(self, node):
        return self.visit_Operator(node)

    def visit_Sra(self, node):
        return self.visit_Operator(node)

    def visit_LessThan(self, node):
        return self.visit_Operator(node)

    def visit_GreaterThan(self, node):
        return self.visit_Operator(node)

    def visit_LessEq(self, node):
        return self.visit_Operator(node)

    def visit_GreaterEq(self, node):
        return self.visit_Operator(node)

    def visit_Eq(self, node):
        return self.visit_Operator(node)

    def visit_NotEq(self, node):
        return self.visit_Operator(node)

    def visit_Eql(self, node):
        return self.visit_Operator(node)

    def visit_NotEql(self, node):
        return self.visit_Operator(node)

    def visit_And(self, node):
        return self.visit_Operator(node)

    def visit_Xor(self, node):
        return self.visit_Operator(node)

    def visit_Xnor(self, node):
        return self.visit_Operator(node)

    def visit_Or(self, node):
        return self.visit_Operator(node)

    def visit_Land(self, node):
        return self.visit_Operator(node)

    def visit_Lor(self, node):
        return self.visit_Operator(node)

    def visit_Cond(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        true_value = del_paren(self.visit(node.true_value))
        false_value = del_paren(self.visit(node.false_value))
        if isinstance(node.false_value, Cond):
            false_value = ''.join( ['\n', false_value] )
        template_dict = {
            'cond' : del_paren(self.visit(node.cond)),
            'true_value' : true_value,
            'false_value' : false_value,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Assign(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'left' : self.visit(node.left),
            'right' : self.visit(node.right),
            }
        rslt = template.render(template_dict)
        rslt = indent_multiline_assign(rslt)
        return rslt

    def visit_Always(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'lineno' : str(node.lineno),
            'statement' : self.visit(node.statement),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Always_process(self, node):
        filename = getfilename(node, '_process')
        template = self.env.get_template(filename)
        clock_sens = ''
        reset_sens = ''
        for sens in node.sens_list.list:
            if sens.sig.name == self.clock_name:
                clock_sens = self.visit(sens)
            if sens.sig.name == self.reset_name:
                reset_sens = self.visit(sens)
                reset_sens = reset_sens.replace('.pos()', ', true')
                reset_sens = reset_sens.replace('.neg()', ', false')
        template_dict = {
            'lineno' : str(node.lineno),
            'clock_sens' : clock_sens,
            'reset_sens' : reset_sens,
            'sens_list' : self.visit(node.sens_list),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Always_declaration(self, node):
        filename = getfilename(node, '_declaration')
        template = self.env.get_template(filename)
        template_dict = {
            'lineno' : str(node.lineno),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_SensList(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        items = [ self.visit(item) for item in node.list if item.sig.name != self.clock_name and item.sig.name != self.reset_name]
        template_dict = {
            'items' : items,
            'len_items' : len(items),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Sens(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'sig' : '*' if node.type == 'all' else self.visit(node.sig),
            'type' : node.type[0:3] if node.type == 'posedge' or node.type == 'negedge' else ''
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Substitution(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'left' : self.visit(node.left),
            'right' : self.visit(node.right),
            'ldelay' : '' if node.ldelay is None else self.visit(node.ldelay),
            'rdelay' : '' if node.rdelay is None else self.visit(node.rdelay),
            }
        rslt = template.render(template_dict)
        rslt = indent_multiline_assign(rslt)
        return rslt

    def visit_BlockingSubstitution(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'left' : self.visit(node.left),
            'right' : self.visit(node.right),
            'ldelay' : '' if node.ldelay is None else self.visit(node.ldelay),
            'rdelay' : '' if node.rdelay is None else self.visit(node.rdelay),
            }
        rslt = template.render(template_dict)
        rslt = indent_multiline_assign(rslt)
        return rslt

    def visit_NonblockingSubstitution(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'left' : self.visit(node.left),
            'right' : self.visit(node.right),
            'ldelay' : '' if node.ldelay is None else self.visit(node.ldelay),
            'rdelay' : '' if node.rdelay is None else self.visit(node.rdelay),
            }
        rslt = template.render(template_dict)
        rslt = indent_multiline_assign(rslt)
        return rslt

    def visit_IfStatement(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        true_statement = '' if node.true_statement is None else self.visit(node.true_statement)
        false_statement = '' if node.false_statement is None else self.visit(node.false_statement)
        template_dict = {
            'cond' : del_paren(self.visit(node.cond)),
            'true_statement' : true_statement,
            'false_statement' : false_statement,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_ForStatement(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'pre' : '' if node.pre is None else self.visit(node.pre),
            'cond' : '' if node.cond is None else del_paren(self.visit(node.cond)),
            'post' : '' if node.post is None else self.visit(node.post).replace(';', ''),
            'statement' : '' if node.statement is None else self.visit(node.statement),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_WhileStatement(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'cond' : '' if node.cond is None else del_paren(self.visit(node.cond)),
            'statement' : '' if node.statement is None else self.visit(node.statement),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_CaseStatement(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'comp' : del_paren(self.visit(node.comp)),
            'caselist' : [ self.indent(self.visit(case)) for case in node.caselist ],
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_CasexStatement(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'comp' : del_paren(self.visit(node.comp)),
            'caselist' : [ self.indent(self.visit(case)) for case in node.caselist ],
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Case(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        condlist = [ 'default' ] if node.cond is None else [ del_paren(self.visit(c)) for c in node.cond ]
        template_dict = {
            'condlist' : condlist,
            'statement' : self.visit(node.statement),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Block(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'scope' : '' if node.scope is None else escape(node.scope),
            'statements' : [ self.indent(self.visit(statement)) for statement in node.statements ],
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Initial(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'name' : 'initial_at_line_' + str(node.lineno),
            'statement' : self.visit(node.statement),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Initial_process(self, node):
        filename = getfilename(node, '_process')
        template = self.env.get_template(filename)
        template_dict = {
            'name' : 'initial_at_line_' + str(node.lineno),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Initial_declaration(self, node):
        filename = getfilename(node, '_declaration')
        template = self.env.get_template(filename)
        template_dict = {
            'name' : 'initial_at_line_' + str(node.lineno),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_EventStatement(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'senslist': del_paren(self.visit(node.senslist)),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_WaitStatement(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'cond': del_paren(self.visit(node.cond)),
            'statement' : self.visit(node.statement) if node.statement else '',
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_ForeverStatement(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'statement' : self.visit(node.statement),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_DelayStatement(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'delay' : self.visit(node.delay),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_InstanceList(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        parameterlist = [ self.indent(self.visit(param)) for param in node.parameterlist ]
        instances = [ self.visit(instance) for instance in node.instances ]
        template_dict = {
            'module' : escape(node.module),
            'parameterlist' : parameterlist,
            'len_parameterlist' : len(parameterlist),
            'instances' : instances,
            'len_instances' : len(instances),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Instance(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        array = '' if node.array is None else self.visit(node.array)
        portlist = [ self.indent(self.visit(port)) for port in node.portlist ]
        template_dict = {
            'name' : escape(node.name),
            'array' : array,
            'portlist' : portlist,
            'len_portlist' : len(portlist),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_ParamArg(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'paramname' : '' if node.paramname is None else escape(node.paramname),
            'argname' : '' if node.argname is None else del_paren(self.visit(node.argname)),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_PortArg(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'portname' : '' if node.portname is None else escape(node.portname),
            'argname' : '' if node.argname is None else del_paren(self.visit(node.argname)),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Function(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        arguments = [ self.visit_argument(s) for s in node.statement ]
        statements = [ self.visit(s) for s in node.statement ]
        statements = [ statement for statement in statements if not statement.startswith('sc_in<') and not statement.startswith('sc_out<') and not statement.startswith('sc_inout<') ]
        template_dict = {
            'name' : escape(node.name),
            'lineno' : str(node.lineno),
            'retwidth' : self.visit(node.retwidth),
            'arguments' : arguments,
            'statements' : statements,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Function_declaration(self, node):
        filename = getfilename(node, '_declaration')
        template = self.env.get_template(filename)
        arguments = [ self.visit_argument(s) for s in node.statement ]
        statements = [ self.indent(self.visit(s)) for s in node.statement ]
        template_dict = {
            'name' : escape(node.name),
            'lineno' : str(node.lineno),
            'retwidth' : self.visit(node.retwidth),
            'arguments' : arguments,
            'statements' : statements,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_FunctionCall(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        args = [ self.visit(arg) for arg in node.args ]
        template_dict = {
            'name' : self.visit(node.name),
            'lineno' : str(node.lineno),
            'args' : args,
            'len_args' : len(args),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Task(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        statement = [ self.indent(self.visit(s)) for s in node.statement ]
        template_dict = {
            'name' : escape(node.name),
            'statement' : statement,
            }
        rslt = template.render(template_dict)
        return rslt

    #def visit_TaskCall(self, node):
    #    filename = getfilename(node)
    #    template = self.env.get_template(filename)
    #    args = [ self.visit(arg) for arg in node.args ]
    #    template_dict = {
    #        'name' : self.visit(node.name),
    #        'args' : args,
    #        'len_args' : len(args),
    #        }
    #    rslt = template.render(template_dict)
    #    return rslt

    def visit_GenerateStatement(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'items' : [ self.visit(item) for item in node.items ]
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_SystemCall(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        args = [ self.visit(arg) for arg in node.args ]
        template_dict = {
            'syscall' : escape(node.syscall),
            'args' : args,
            'len_args' : len(args),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_IdentifierScopeLabel(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'name' : escape(node.name),
            'loop' : '' if node.loop is None else self.visit(node.loop),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_IdentifierScope(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        scopes = [ self.visit(scope) for scope in node.labellist ]
        template_dict = {
            'scopes' : scopes,
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Pragma(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'entry' : self.visit(node.entry),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_PragmaEntry(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'name' : escape(node.name),
            'value' : '' if node.value is None else self.visit(node.value),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_Disable(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'name' : escape(node.dest),
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_ParallelBlock(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'scope' : '' if node.scope is None else escape(node.scope),
            'statements' : [ self.indent(self.visit(statement)) for statement in node.statements ],
            }
        rslt = template.render(template_dict)
        return rslt

    def visit_SingleStatement(self, node):
        filename = getfilename(node)
        template = self.env.get_template(filename)
        template_dict = {
            'statement' : self.visit(node.statement),
            }
        rslt = template.render(template_dict)
        return rslt

def main():
    INFO = "Code converter from AST"
    VERSION = pyverilog.utils.version.VERSION
    USAGE = "Usage: python example_codegen.py file ..."

    def showVersion():
        print(INFO)
        print(VERSION)
        print(USAGE)
        sys.exit()

    optparser = OptionParser()
    optparser.add_option("-v","--version",action="store_true",dest="showversion",
                         default=False,help="Show the version")
    optparser.add_option("-I","--include",dest="include",action="append",
                         default=[],help="Include path")
    optparser.add_option("-D",dest="define",action="append",
                         default=[],help="Macro Definition")
    (options, args) = optparser.parse_args()

    filelist = args
    if options.showversion:
        showVersion()

    for f in filelist:
        if not os.path.exists(f): raise IOError("file not found: " + f)

    if len(filelist) == 0:
        showVersion()

    codeparser = VerilogCodeParser(filelist,
                                   preprocess_include=options.include,
                                   preprocess_define=options.define)

    ast = codeparser.parse()
    directives = codeparser.get_directives()

    ast.show();

    codegen = ASTCodeGenerator()
    rslt = codegen.visit(ast)
    print(rslt)

if __name__ == '__main__':
    main()
