// bind_ckksencoder.cpp
#include <seal/ckks.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/complex.h>
#include <pybind11/numpy.h>

namespace py = pybind11;
using namespace seal;

void bind_ckksencoder(py::module &m) {
    py::class_<CKKSEncoder>(m, "CKKSEncoder")
        .def(py::init<const SEALContext &>(), py::arg("context"),
            "Creates a CKKSEncoder for the given SEALContext (must be CKKS scheme).")

        // Encode vector<double>
        .def("encode", [](const CKKSEncoder &encoder, const std::vector<double> &values, double scale, Plaintext &plain) {
            std::cout << "[DEBUG] encode called with values.size() = " << values.size() << std::endl;
            encoder.encode(values, scale, plain);
        }, py::arg("values"), py::arg("scale"), py::arg("plain"),
            "Encodes a vector of double into a Plaintext with the given scale.")

        // Encode vector<complex<double>>
        .def("encode", [](const CKKSEncoder &encoder, const std::vector<std::complex<double>> &values, double scale, Plaintext &plain) {
            std::cout << "[DEBUG] encode2 called with values.size() = " << values.size() << std::endl;
            encoder.encode(values, scale, plain);
        }, py::arg("values"), py::arg("scale"), py::arg("plain"),
            "Encodes a vector of complex<double> into a Plaintext with the given scale.")

        // Encode single double
        .def("encode", [](const CKKSEncoder &encoder, double value, double scale, Plaintext &plain) {
            std::cout << "[DEBUG] encode3 called with value = " << value << std::endl;
            encoder.encode(value, scale, plain);
        }, py::arg("value"), py::arg("scale"), py::arg("plain"),
            "Encodes a single double into a Plaintext with the given scale.")

        // Encode single int64_t (fills all slots)
        .def("encode", [](const CKKSEncoder &encoder, std::int64_t value, Plaintext &plain) {
            std::cout << "[DEBUG] encode4 called with value = " << value << std::endl;
            encoder.encode(value, plain);
        }, py::arg("value"), py::arg("plain"),
            "Encodes a single int64_t into a Plaintext (fills all slots).")

        // Decode to vector<double>
        .def("decode", [](const CKKSEncoder &encoder, const Plaintext &plain) {
            std::vector<double> result;
            encoder.decode(plain, result);
            std::cout << "[DEBUG] decode_double called, result.size() = " << result.size() << std::endl;
            return result;
        }, py::arg("plain"),
            "Decodes a Plaintext into a vector of double.")

        // Decode to vector<complex<double>>
        .def("decode_complex", [](const CKKSEncoder &encoder, const Plaintext &plain) {
            std::vector<std::complex<double>> result;
            encoder.decode(plain, result);
            std::cout << "[DEBUG] decode_complex called, result.size() = " << result.size() << std::endl;
            return result;
        }, py::arg("plain"),
            "Decodes a Plaintext into a vector of complex<double>.")

        // Slot count
        .def("slot_count", &CKKSEncoder::slot_count,
            "Returns the number of slots (poly_modulus_degree / 2).")

        // For CKKSEncoder
        .def("encode_new", [](const CKKSEncoder &encoder, const std::vector<double> &values, double scale) {
            std::cout << "[DEBUG] encode_new called with values.size() = " << values.size() << std::endl;
            Plaintext plain;
            encoder.encode(values, scale, plain);
            return plain;
        })

        // Add this overload for complex<double>
        // Safely add numpy array support
        .def("encode_new_numpy", [](const CKKSEncoder &encoder, py::array_t<double, py::array::c_style> values, double scale) {
            auto buf = values.request();
            if (buf.ndim != 1) {
                throw std::runtime_error("Number of dimensions must be 1");
            }
            
            const double* ptr = static_cast<const double*>(buf.ptr);
            std::vector<double> vec(ptr, ptr + buf.shape[0]);
            
            std::cout << "[DEBUG] encode_new_numpy called with values.size() = " << vec.size() << std::endl;
            Plaintext plain;
            encoder.encode(vec, scale, plain);
            return plain;
        }, py::arg("values"), py::arg("scale"));
}