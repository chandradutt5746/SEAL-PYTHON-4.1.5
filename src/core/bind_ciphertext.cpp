#include "bind_ciphertext.h"
#include <seal/ciphertext.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <fstream>
#include <sstream>

namespace py = pybind11;
using namespace seal;

void bind_ciphertext(py::module &m) {
    py::class_<Ciphertext>(m, "Ciphertext")
        .def(py::init<>(), "Create an empty ciphertext")
        .def(py::init<const SEALContext&>(), py::arg("context"), "Create a ciphertext with the given context")
        .def(py::init([](const SEALContext& context, py::array_t<uint64_t> data, size_t poly_count, size_t coeff_mod_count, size_t poly_mod_degree, double scale) {
            // Initialize a ciphertext directly from a NumPy array for high performance
            auto buf = data.request();
            if (buf.ndim != 1) {
                throw std::runtime_error("Data must be a 1D array");
            }
            
            const size_t expected_size = poly_count * coeff_mod_count * poly_mod_degree;
            if (buf.size != static_cast<py::ssize_t>(expected_size)) {
                throw std::runtime_error("Data size doesn't match ciphertext dimensions");
            }
            
            // Create a ciphertext with the given parameters
            Ciphertext ct(context);
            ct.resize(poly_count);
            ct.scale() = scale;
            
            // Copy data from NumPy array
            const uint64_t* src = static_cast<const uint64_t*>(buf.ptr);
            const size_t elements_per_poly = coeff_mod_count * poly_mod_degree;
            
            for (size_t i = 0; i < poly_count; i++) {
                // We're accessing the source array directly here, so we need to be careful with pointer arithmetic
                // No need for casting since the raw pointer arithmetic works with size_t
                std::memcpy(ct.data(i), src + i * elements_per_poly, elements_per_poly * sizeof(uint64_t));
            }
            
            return ct;
        }), py::arg("context"), py::arg("data"), py::arg("poly_count"), py::arg("coeff_mod_count"), 
            py::arg("poly_mod_degree"), py::arg("scale"), "Create a ciphertext directly from a NumPy array (high performance)")
        .def("parms_id", [](const Ciphertext &ct) {
            auto id = ct.parms_id();
            return py::bytes(reinterpret_cast<const char*>(id.data()), id.size());
        })
        .def("scale", py::overload_cast<>(&Ciphertext::scale, py::const_))
        .def("set_scale", [](Ciphertext &ct, double scale) { ct.scale() = scale; })
        .def("size", &Ciphertext::size)
        .def("size_capacity", &Ciphertext::size_capacity)
        .def("poly_modulus_degree", &Ciphertext::poly_modulus_degree)
        .def("coeff_modulus_size", &Ciphertext::coeff_modulus_size)
        .def("is_ntt_form", py::overload_cast<>(&Ciphertext::is_ntt_form, py::const_))
        .def("is_transparent", py::overload_cast<>(&Ciphertext::is_transparent, py::const_))
        .def("correction_factor", py::overload_cast<>(&Ciphertext::correction_factor, py::const_))
        .def("set_correction_factor", [](Ciphertext &ct, std::uint64_t cf) { ct.correction_factor() = cf; })
        .def("reserve", py::overload_cast<std::size_t>(&Ciphertext::reserve), 
             py::arg("size"), "Allocates enough memory to accommodate the specified number of polynomials.")
             
        .def("reserve_with_context", [](Ciphertext &ct, const SEALContext &ctx, std::size_t size) {
            ct.reserve(ctx, size);
        }, py::arg("context"), py::arg("size"), "Allocates enough memory to accommodate the specified number of polynomials "
           "based on the given context.")
           
        .def_static("create_preallocated", [](const SEALContext &context, size_t count) {
            // Pre-allocate a batch of ciphertexts with the same parameters - more efficient than creating individually
            std::vector<Ciphertext> result;
            result.reserve(count);
            
            for (size_t i = 0; i < count; i++) {
                result.emplace_back(context);
            }
            
            return result;
        }, py::arg("context"), py::arg("count"), "Create a batch of pre-allocated ciphertexts for better performance.")
        .def("release", &Ciphertext::release)
        .def("save", [](const Ciphertext &self, const std::string &path) {
            std::ofstream out(path, std::ios::binary);
            if (!out) throw std::runtime_error("Failed to open file for writing");
            self.save(out);
            out.close();
        })
        .def("load", [](Ciphertext &self, const SEALContext &context, const std::string &path) {
            std::ifstream in(path, std::ios::binary);
            if (!in) throw std::runtime_error("Failed to open file for reading");
            self.load(context, in);
            in.close();
        })
        // Better approach: split into multiple methods with docstrings
        .def("data_size", [](const Ciphertext &ct) {
            return ct.size();
        }, "Returns the number of polynomials in this ciphertext.")
        
        .def("data_at", [](Ciphertext &ct, size_t index) {
            if (index >= ct.size()) {
                throw std::out_of_range("Ciphertext index out of range");
            }
            return py::memoryview::from_buffer(
                ct.data(index),
                {static_cast<py::ssize_t>(ct.coeff_modulus_size() * ct.poly_modulus_degree())},
                {static_cast<py::ssize_t>(sizeof(uint64_t))}
            );
        }, py::arg("index"), py::keep_alive<0, 1>(), 
           "Returns a memoryview to the polynomial at the given index in this ciphertext.")
           
        .def("to_array", [](const Ciphertext &ct) {
            // Convert ciphertext to NumPy array for much better performance
            auto size = ct.size();
            auto coeff_count = ct.coeff_modulus_size() * ct.poly_modulus_degree();
            auto total_size = size * coeff_count;
            
            // Create NumPy array directly to avoid copying
            // Explicitly convert total_size to pybind11::ssize_t to avoid sign conversion warning
            py::array_t<uint64_t> result(static_cast<py::ssize_t>(total_size));
            auto r = result.mutable_unchecked<1>();
            
            // Use py::ssize_t for idx to avoid sign conversion warning when indexing NumPy array
            py::ssize_t idx = 0;
            for (size_t i = 0; i < size; i++) {
                const uint64_t* ptr = ct.data(i);
                for (size_t j = 0; j < coeff_count; j++) {
                    r[idx++] = ptr[j];
                }
            }
            
            return result;
        }, "Converts the ciphertext to a NumPy array of uint64 values for faster access in Python.")
        
        .def("to_array_view", [](const Ciphertext &ct) {
            // Create a NumPy array that shares the underlying memory - even faster but needs careful use
            auto size = ct.size();
            auto coeff_count = ct.coeff_modulus_size() * ct.poly_modulus_degree();
            
            if (size == 0) {
                return py::array_t<uint64_t>(0);
            }
            
            // Only works if memory is contiguous, which it should be in SEAL
            return py::array_t<uint64_t>(
                {static_cast<py::ssize_t>(size), static_cast<py::ssize_t>(coeff_count)},
                {static_cast<py::ssize_t>(coeff_count * sizeof(uint64_t)), static_cast<py::ssize_t>(sizeof(uint64_t))},
                ct.data(0),
                py::cast(ct)  // Keep the ciphertext alive as long as the array exists
            );
        }, py::keep_alive<0, 1>(), "Returns a view of the ciphertext as a NumPy array without copying data.")
        // Add serialization helpers instead of pickle
        .def("__getstate__", [](const Ciphertext &c) {
            std::stringstream ss;
            c.save(ss);
            return py::bytes(ss.str());
        })
        .def("__setstate__", [](Ciphertext &c, py::bytes b) {
            std::string str = b;
            std::stringstream ss(str);
            // We can't fully deserialize here without context
            // User must call load() explicitly with context
            c = Ciphertext();
        })
        .def("resize", [](Ciphertext &ct, std::size_t size) { ct.resize(size); })
        
        // Performance optimizations for batch operations
        .def_static("batch_save", [](const std::vector<std::reference_wrapper<const Ciphertext>> &ciphertexts, const std::string &path) {
            // Save multiple ciphertexts to a single file - more efficient than saving individually
            std::ofstream out(path, std::ios::binary);
            if (!out) throw std::runtime_error("Failed to open file for writing");
            
            // Write number of ciphertexts
            uint64_t count = ciphertexts.size();
            out.write(reinterpret_cast<const char*>(&count), sizeof(count));
            
            // Write each ciphertext
            for (const auto &ct_ref : ciphertexts) {
                ct_ref.get().save(out);
            }
            
            out.close();
            return count;
        }, py::arg("ciphertexts"), py::arg("path"), "Save multiple ciphertexts to a single file efficiently.")
        
        .def_static("batch_load", [](const SEALContext &context, const std::string &path) {
            // Load multiple ciphertexts from a single file
            std::ifstream in(path, std::ios::binary);
            if (!in) throw std::runtime_error("Failed to open file for reading");
            
            // Read number of ciphertexts
            uint64_t count;
            in.read(reinterpret_cast<char*>(&count), sizeof(count));
            
            // Read each ciphertext
            std::vector<Ciphertext> result;
            result.reserve(count);
            
            for (uint64_t i = 0; i < count; i++) {
                Ciphertext ct;
                ct.load(context, in);
                result.push_back(std::move(ct));
            }
            
            in.close();
            return result;
        }, py::arg("context"), py::arg("path"), "Load multiple ciphertexts from a single file efficiently.");
}