import sys
import ctypes
import numpy as np

lib = ctypes.CDLL("libflowpath.so")

# Define the argument and return types for the flowpath function.
# The fdr pointer is an array of unsigned char (np.uint8).
lib.flowpath.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),  # fdr pointer
    ctypes.c_int,                    # nrows
    ctypes.c_int,                    # ncols
    ctypes.c_int,                    # i (starting row)
    ctypes.c_int,                    # j (starting col)
    ctypes.POINTER(ctypes.POINTER(ctypes.c_int)),  # ii_out
    ctypes.POINTER(ctypes.POINTER(ctypes.c_int)),  # jj_out
    ctypes.POINTER(ctypes.c_int)     # npoints
]
lib.flowpath.restype = None

def call_flowpath(fdr: np.ndarray, i: int, j: int):
    # Ensure the numpy array is of type uint8 and contiguous
    if fdr.dtype != np.uint8:
        raise ValueError("fdr must be of type np.uint8")
    if not fdr.flags['C_CONTIGUOUS']:
        fdr = np.ascontiguousarray(fdr, dtype=np.uint8)
    
    nrows, ncols = fdr.shape
    fdr_ptr = fdr.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
    
    # Prepare pointers for the outputs
    ii_ptr = ctypes.POINTER(ctypes.c_int)()
    jj_ptr = ctypes.POINTER(ctypes.c_int)()
    npoints = ctypes.c_int()
    
    # Call the C function
    lib.flowpath(fdr_ptr, nrows, ncols, i, j,
                 ctypes.byref(ii_ptr), ctypes.byref(jj_ptr), ctypes.byref(npoints))
    
    n = npoints.value
    # Convert the returned C arrays to NumPy arrays and copy the data
    ii_array = np.ctypeslib.as_array(ii_ptr, shape=(n,)).copy()
    jj_array = np.ctypeslib.as_array(jj_ptr, shape=(n,)).copy()
    
    # Free the memory allocated in the C function using the C standard library free()
    libc = ctypes.CDLL("libc.dylib")
    libc.free.argtypes = [ctypes.c_void_p]
    libc.free(ii_ptr)
    libc.free(jj_ptr)
    
    return ii_array, jj_array

# Example usage:
if __name__ == "__main__":
    # Create an example grid (5x5)
    fdr = np.array([
        [1,   1,   1,   1,   1],
        [1, 255,   1, 255,   1],
        [1,   1,   1,   1,   1],
        [1, 255,   1, 255,   1],
        [1,   1,   1,   1,   1],
    ], dtype=np.uint8)
    
    ii, jj = call_flowpath(fdr, 0, 0)
    print("Flow path:")
    for r, c in zip(ii, jj):
        print(f"({r}, {c})")
