cmake_minimum_required(VERSION 2.8)
add_executable(systemc systemc.cpp)

include_directories(/usr/local/systemc/include)
LINK_DIRECTORIES(/usr/local/systemc/lib-cygwin)
