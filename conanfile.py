import os
import sys
from conans import ConanFile, CMake
from conans.tools import chdir, patch, environment_append, os_info, SystemPackageTool, ChocolateyTool

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

required_conan_version = ">=1.28.0"


class AngleConan(ConanFile):
    name = "angle"
    version = "2.1.0"
    license = "BSD 3-Clause License"
    author = "Google"
    url = "https://chromium.googlesource.com/angle/angle"
    description = "ANGLE is an open source, BSD-licensed graphics engine abstraction layer developed by Google."
    topics = ("graphics", "opengl", "opengl es")
    settings = "build_type", "arch", "os"  # , "compiler"
    options = {
        "python_executable": "ANY",  # system default python installation is used, if None
    }
    default_options = {
        "python_executable": "None",
    }
    generators = "cmake"
    exports_sources = ['patches/*']
    
    @property
    def _python_executable(self):
        """
        obtain full path to the python interpreter executable
        :return: path to the python interpreter executable, either set by option, or system default
        """
        exe = self.options.python_executable if self.options.python_executable else sys.executable
        return str(exe).replace('\\', '/')
        
    def source(self):
        self.run("git clone -b chromium/4389 https://github.com/google/angle --depth=1 angle")
        self.run("git clone https://chromium.googlesource.com/chromium/tools/depot_tools --depth=1 depot_tools")
        
        # bootstrap
        if os_info.is_windows:
            self.output.info("Bootstrap for windows")
            with chdir("depot_tools/bootstrap"):
                with environment_append({"DEPOT_TOOLS_UPDATE": "0", "PYTHONDONTWRITEBYTECODE": "1"}):
                    self.run(".\win_tools.bat")
            with chdir("depot_tools"):
                self.run(".\git.bat config --system core.longpaths true")
        
        # apply patches
        if os_info.is_windows:
            patch(patch_file="patches/bootstrap.patch")
        
        # fetch dependencies
        python_executable = self._python_executable
        envs = {
            "DEPOT_TOOLS_UPDATE": "0",
            "DEPOT_TOOLS_WIN_TOOLCHAIN": "0",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PATH": [ os.path.join(os.getcwd(), "depot_tools") ]
        }
        self.output.info("PATH=%s" % os.environ.get("PATH"))
        with environment_append(envs):
            with chdir("angle"):
                # bootstrap
                self.run("\"%s\" scripts/bootstrap.py" % python_executable)
                self.run("gclient sync")
                if os_info.is_linux:
                    self.output.warn("[IMPORTANT!] You have to execute \"./build/install-build-deps.sh\" manually for first time building ANGLE")
                    self.output.warn("[IMPORTANT!] Note: Rebuild with --keep-source to skip the installation of dependencies next time")
                    #self.run("./build/install-build-deps.sh")
        
                # patch windows sdk version
                if os_info.is_windows:
                    with chdir(".."):
                        patch(patch_file="patches/setup_toolchain.patch")
        
    def build(self):
        # build
        envs = {
            "DEPOT_TOOLS_UPDATE": "0",
            "DEPOT_TOOLS_WIN_TOOLCHAIN": "0",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PATH": [ os.path.join(os.getcwd(), "depot_tools") ]
        }
        with environment_append(envs):
            with chdir("angle"):
                # detect target_cpu
                if self.settings.arch == "x86_64" or self.settings.arch == "x64" or self.settings.arch == "amd64":
                    target_cpu = "x64"
                elif self.settings.arch == "x86":  
                    target_cpu = "x86"
                else:
                    raise RuntimeError("Unknown arch %s", self.settings.arch)
                
                # detect is_debug
                is_debug = "true" if (self.settings.build_type == "Debug") else "false"
                
                # run ninja
                self.output.info("Configure source (is_debug=%s, target_cpu=%s)" % (is_debug, target_cpu))
                if os_info.is_windows:
                    self.run("gn gen out --args=\"is_clang=true is_debug=%s target_cpu=\\\"\"%s\\\"\" \"" % (is_debug, target_cpu))
                else:
                    self.run("gn gen out --args='is_clang=true is_debug=%s target_cpu=\"%s\"'" % (is_debug, target_cpu))
                self.output.info("Start building")
                self.run("autoninja -C out")
        
    def package(self):
        self.copy("*.dll", dst="bin", src="angle/out")
        self.copy("*.so*", dst="lib", src="angle/out")
        self.copy("*.dylib", dst="lib", src="angle/out")
        self.copy("*.a", dst="lib", src="angle/out")
        self.copy("*.lib", dst="lib", src="angle/out")
        self.copy("*.h", dst="include", src="angle/include")
        self.copy("*.inc", dst="include", src="angle/include")
        
    def package_info(self):
        if os_info.is_windows:
            self.cpp_info.libs = ["libEGL.dll.lib", "libGLESv2.dll.lib"]
        else:
            self.cpp_info.libs = ["EGL", "GLESv2"]
        