# BEGINNER NOTE: This builds the C API library so tools in C can use this dialect.
add_mlir_public_c_api_library(StandaloneCAPI
  Dialects.cpp
  LINK_LIBS PUBLIC
  MLIRStandalone
)
