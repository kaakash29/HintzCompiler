# BEGINNER NOTE: This builds/runs C API tests that verify the dialect works through the C interface.
# Link the C API libraries directly so installed LLVM/MLIR distributions work
# even when they do not ship MLIR_INSTALL_AGGREGATE_OBJECTS.

add_llvm_executable(standalone-capi-test
  standalone-capi-test.c
)
llvm_update_compile_flags(standalone-capi-test)
set_target_properties(standalone-capi-test PROPERTIES LINKER_LANGUAGE CXX)
target_link_libraries(standalone-capi-test
  PRIVATE StandaloneCAPI MLIRCAPIIR MLIRCAPIRegisterEverything)
