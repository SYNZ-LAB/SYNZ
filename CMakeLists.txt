cmake_minimum_required(VERSION 3.14)
project(SYNZ_Core)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)
# 1. Declare where to get it (Official repo)
FetchContent_Declare(
    llama_cpp
    GIT_REPOSITORY https://github.com/ggerganov/llama.cpp
    GIT_TAG        master
)
# 2. Options (Crucial for performance!)
# We enable CUDA (NVIDIA) or Metal (Mac) if available.
option(GGML_CUDA "Build with CUDA support" OFF) 
# 3. Download and make available
FetchContent_MakeAvailable(llama_cpp)

# Define our app name and source files
add_executable(synz_core src/main.cpp)
# Link the llama library so we can use #include "llama.h"
target_link_libraries(synz_core PRIVATE llama)
