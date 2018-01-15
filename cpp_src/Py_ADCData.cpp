//
//  ADC_Readout.cpp
//  ADC_Data_Receiver
//
//  Created by Jonas Nilsson on 2017-10-17.
//  Copyright © 2017 European Spallation Source. All rights reserved.
//

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "AdcReadout.h"

namespace py = pybind11;

PYBIND11_MODULE(AdcReadout, m) {
  py::class_<TimeStamp>(m, "TimeStamp")
  .def(py::init<>())
  .def_readwrite("Seconds", &TimeStamp::Seconds)
  .def_readwrite("SecondsFraction", &TimeStamp::SecondsFraction);
  
  py::class_<SampleData>(m, "SampleData")
  .def(py::init<>())
  .def_readwrite("TimeStamps", &SampleData::TimeStamps)
  .def_readwrite("Samples", &SampleData::Samples);
  
  py::class_<AdcReadout>(m, "AdcReadout")
  .def(py::init<std::uint16_t, std::int32_t>())
  .def("startThreads", &AdcReadout::StartThreads)
  .def("stopThreads", &AdcReadout::StopThreads)
  .def("getSamples", &AdcReadout::getSamples);
}
