import pytest
import numpy as np
from flowpath_wrapper import call_flowpath
from main import flowpath

@pytest.mark.parametrize(
    "fdr, start_i, start_j",
    [
        # Test case 1: Simple flow
        (np.array([
            [1, 1, 1],
            [4, 4, 4],
            [8, 8, 8]
        ], dtype=np.uint8), 0, 0),

        # Test case 2: Flow hitting a sink
        (np.array([
            [1, 1, 1],
            [4, 0, 4],  # Sink at (1,1)
            [8, 8, 8]
        ], dtype=np.uint8), 0, 0),

        # Test case 3: Out-of-bounds check
        (np.array([
            [1, 1, 1, 1],
            [4, 4, 4, 4],
            [8, 8, 8, 8]
        ], dtype=np.uint8), 2, 3),

        # Test case 4: Complex terrain
        (np.array([
            [1, 2, 4, 8],
            [16, 32, 64, 128],
            [1, 2, 4, 8]
        ], dtype=np.uint8), 1, 1),
    ]
)
def test_flowpath(fdr, start_i, start_j):
    """Test if Python and C versions of flowpath return the same results."""
    # Run Python version
    python_ii, python_jj = flowpath(fdr, start_i, start_j)

    # Run C version (wrapped in Python)
    c_ii, c_jj = call_flowpath(fdr, start_i, start_j)

    # Ensure both return arrays of the same length
    assert len(python_ii) == len(c_ii), "Mismatch in path length"
    assert len(python_jj) == len(c_jj), "Mismatch in path length"

    # Ensure all elements match
    np.testing.assert_array_equal(python_ii, c_ii, err_msg="Row indices mismatch")
    np.testing.assert_array_equal(python_jj, c_jj, err_msg="Column indices mismatch")
