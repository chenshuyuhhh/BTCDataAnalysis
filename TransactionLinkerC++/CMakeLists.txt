cmake_minimum_required(VERSION 3.10)
project(TransactionLinker)


set(CMAKE_CXX_STANDARD 14)
#set(CMAKE_CXX_FLAGS "-O0 -g")
find_package(Threads)
add_executable(TransactionLinker main.cpp TransactionLinker.cpp TransactionLinker.h)
target_link_libraries(TransactionLinker ${CMAKE_THREAD_LIBS_INIT})
