list(APPEND dupin_cxx "module.cpp" "dupin.h" "dupin.cpp")

pybind11_add_module(_dupin ${dupin_cxx})

set_target_properties(_dupin PROPERTIES
    CXX_STANDARD 17
    CMAKE_CXX_STANDARD_REQUIRED True
)

target_include_directories(_dupin PRIVATE
    ${EIGEN3_INCLUDE_DIR}
    ${TBB_INCLUDE_DIRS}
)

target_link_libraries(_dupin PRIVATE TBB::tbb)
target_compile_definitions(_dupin PRIVATE VERSION_INFO=${PROJECT_VERSION})
target_compile_options(_dupin PRIVATE -O2 -march=native)
# Installs C++ extension into the root of the Python package
install(TARGETS _dupin LIBRARY DESTINATION dupin)
