# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.10

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list


# Suppress display of executed commands.
$(VERBOSE).SILENT:


# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/daslab/TransactionLinkerC++

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/daslab/TransactionLinkerC++

# Include any dependencies generated for this target.
include CMakeFiles/TransactionLinker.dir/depend.make

# Include the progress variables for this target.
include CMakeFiles/TransactionLinker.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/TransactionLinker.dir/flags.make

CMakeFiles/TransactionLinker.dir/main.cpp.o: CMakeFiles/TransactionLinker.dir/flags.make
CMakeFiles/TransactionLinker.dir/main.cpp.o: main.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/daslab/TransactionLinkerC++/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object CMakeFiles/TransactionLinker.dir/main.cpp.o"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/TransactionLinker.dir/main.cpp.o -c /home/daslab/TransactionLinkerC++/main.cpp

CMakeFiles/TransactionLinker.dir/main.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/TransactionLinker.dir/main.cpp.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/daslab/TransactionLinkerC++/main.cpp > CMakeFiles/TransactionLinker.dir/main.cpp.i

CMakeFiles/TransactionLinker.dir/main.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/TransactionLinker.dir/main.cpp.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/daslab/TransactionLinkerC++/main.cpp -o CMakeFiles/TransactionLinker.dir/main.cpp.s

CMakeFiles/TransactionLinker.dir/main.cpp.o.requires:

.PHONY : CMakeFiles/TransactionLinker.dir/main.cpp.o.requires

CMakeFiles/TransactionLinker.dir/main.cpp.o.provides: CMakeFiles/TransactionLinker.dir/main.cpp.o.requires
	$(MAKE) -f CMakeFiles/TransactionLinker.dir/build.make CMakeFiles/TransactionLinker.dir/main.cpp.o.provides.build
.PHONY : CMakeFiles/TransactionLinker.dir/main.cpp.o.provides

CMakeFiles/TransactionLinker.dir/main.cpp.o.provides.build: CMakeFiles/TransactionLinker.dir/main.cpp.o


CMakeFiles/TransactionLinker.dir/TransactionLinker.cpp.o: CMakeFiles/TransactionLinker.dir/flags.make
CMakeFiles/TransactionLinker.dir/TransactionLinker.cpp.o: TransactionLinker.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/daslab/TransactionLinkerC++/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Building CXX object CMakeFiles/TransactionLinker.dir/TransactionLinker.cpp.o"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/TransactionLinker.dir/TransactionLinker.cpp.o -c /home/daslab/TransactionLinkerC++/TransactionLinker.cpp

CMakeFiles/TransactionLinker.dir/TransactionLinker.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/TransactionLinker.dir/TransactionLinker.cpp.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/daslab/TransactionLinkerC++/TransactionLinker.cpp > CMakeFiles/TransactionLinker.dir/TransactionLinker.cpp.i

CMakeFiles/TransactionLinker.dir/TransactionLinker.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/TransactionLinker.dir/TransactionLinker.cpp.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/daslab/TransactionLinkerC++/TransactionLinker.cpp -o CMakeFiles/TransactionLinker.dir/TransactionLinker.cpp.s

CMakeFiles/TransactionLinker.dir/TransactionLinker.cpp.o.requires:

.PHONY : CMakeFiles/TransactionLinker.dir/TransactionLinker.cpp.o.requires

CMakeFiles/TransactionLinker.dir/TransactionLinker.cpp.o.provides: CMakeFiles/TransactionLinker.dir/TransactionLinker.cpp.o.requires
	$(MAKE) -f CMakeFiles/TransactionLinker.dir/build.make CMakeFiles/TransactionLinker.dir/TransactionLinker.cpp.o.provides.build
.PHONY : CMakeFiles/TransactionLinker.dir/TransactionLinker.cpp.o.provides

CMakeFiles/TransactionLinker.dir/TransactionLinker.cpp.o.provides.build: CMakeFiles/TransactionLinker.dir/TransactionLinker.cpp.o


# Object files for target TransactionLinker
TransactionLinker_OBJECTS = \
"CMakeFiles/TransactionLinker.dir/main.cpp.o" \
"CMakeFiles/TransactionLinker.dir/TransactionLinker.cpp.o"

# External object files for target TransactionLinker
TransactionLinker_EXTERNAL_OBJECTS =

TransactionLinker: CMakeFiles/TransactionLinker.dir/main.cpp.o
TransactionLinker: CMakeFiles/TransactionLinker.dir/TransactionLinker.cpp.o
TransactionLinker: CMakeFiles/TransactionLinker.dir/build.make
TransactionLinker: CMakeFiles/TransactionLinker.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/home/daslab/TransactionLinkerC++/CMakeFiles --progress-num=$(CMAKE_PROGRESS_3) "Linking CXX executable TransactionLinker"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/TransactionLinker.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/TransactionLinker.dir/build: TransactionLinker

.PHONY : CMakeFiles/TransactionLinker.dir/build

CMakeFiles/TransactionLinker.dir/requires: CMakeFiles/TransactionLinker.dir/main.cpp.o.requires
CMakeFiles/TransactionLinker.dir/requires: CMakeFiles/TransactionLinker.dir/TransactionLinker.cpp.o.requires

.PHONY : CMakeFiles/TransactionLinker.dir/requires

CMakeFiles/TransactionLinker.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/TransactionLinker.dir/cmake_clean.cmake
.PHONY : CMakeFiles/TransactionLinker.dir/clean

CMakeFiles/TransactionLinker.dir/depend:
	cd /home/daslab/TransactionLinkerC++ && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/daslab/TransactionLinkerC++ /home/daslab/TransactionLinkerC++ /home/daslab/TransactionLinkerC++ /home/daslab/TransactionLinkerC++ /home/daslab/TransactionLinkerC++/CMakeFiles/TransactionLinker.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/TransactionLinker.dir/depend
