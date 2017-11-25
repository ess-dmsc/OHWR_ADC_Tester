cmake_minimum_required(VERSION 3.8)
project(AdcReadout)
add_definitions(-std=c++11)
set(CMAKE_CXX_STANDARD 11)

set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake_modules)

if (CMAKE_VERSION VERSION_LESS 3.2)
  set(UPDATE_DISCONNECTED_IF_AVAILABLE "")
else()
  set(UPDATE_DISCONNECTED_IF_AVAILABLE "UPDATE_DISCONNECTED 1")
endif()
    
include(DownloadProject)
download_project(PROJ                pybind11
  GIT_REPOSITORY      https://github.com/pybind/pybind11.git
  GIT_TAG             master
  ${UPDATE_DISCONNECTED_IF_AVAILABLE})

add_subdirectory(${pybind11_SOURCE_DIR} ${pybind11_BINARY_DIR})

set(ADC_SRC Socket.cpp AdcReadout.cpp AdcParse.cpp)
set(ADC_INC AdcReadout.h CircularBuffer.h atomicops.h Detector.h readerwriterqueue.h Socket.h AdcParse.h AdcBufferElements.h)
pybind11_add_module(AdcReadout ${ADC_SRC} ${ADC_INC} Py_ADCData.cpp)
