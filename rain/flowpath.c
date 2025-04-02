#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef unsigned char uchar;

#ifdef __cplusplus
extern "C" {
#endif

// Function prototype:
//  - fdr: pointer to grid data stored in row-major order
//  - nrows, ncols: dimensions of the grid
//  - i, j: starting coordinates
//  - ii_out, jj_out: pointers to dynamically allocated arrays containing the row and column indices of the flow path
//  - npoints: pointer to an integer storing the number of points in the path
void flowpath(const uchar *fdr, int nrows, int ncols, int i, int j, int **ii_out, int **jj_out, int *npoints) {
    // Direction mapping using a switch-case below
    //  Flow value to (di, dj)
    //  1: ( 0,  1)
    //  2: ( 1,  1)
    //  4: ( 1,  0)
    //  8: ( 1, -1)
    // 16: ( 0, -1)
    // 32: (-1, -1)
    // 64: (-1,  0)
    // 128:(-1,  1)

    // Allocate a visited array to detect cycles.
    bool *visited = (bool *)calloc(nrows * ncols, sizeof(bool));
    if (!visited) {
        fprintf(stderr, "Memory allocation failed for visited array.\n");
        exit(EXIT_FAILURE);
    }

    // Dynamic arrays for storing the path.
    int capacity = 100;
    int count = 0;
    int *ii = (int *)malloc(capacity * sizeof(int));
    int *jj = (int *)malloc(capacity * sizeof(int));
    if (!ii || !jj) {
        fprintf(stderr, "Memory allocation failed for path arrays.\n");
        free(visited);
        exit(EXIT_FAILURE);
    }

    while (1) {
        // Check out-of-bounds
        if (i < 0 || i >= nrows || j < 0 || j >= ncols) {
            // printf("Out-of-bounds\n");
            break;
        }
        
        // Compute index into visited array.
        int idx = i * ncols + j;
        if (visited[idx]) {
            // printf("I've been here before!\n");
            break;
        }
        visited[idx] = true;

        // Add the coordinate to the path
        if (count >= capacity) {
            capacity *= 2;
            ii = (int *)realloc(ii, capacity * sizeof(int));
            jj = (int *)realloc(jj, capacity * sizeof(int));
            if (!ii || !jj) {
                fprintf(stderr, "Reallocation failed for path arrays.\n");
                free(visited);
                exit(EXIT_FAILURE);
            }
        }
        ii[count] = i;
        jj[count] = j;
        count++;

        // Get the flow value from the grid.
        uchar cell = fdr[idx];
        if (cell == 0 || cell == 255) {
            // printf("Hit sink\n");
            break;
        }

        // Determine the direction offsets.
        int di = 0, dj = 0;
        switch(cell) {
            case 1:   di = 0;  dj = 1;  break;  // east
            case 2:   di = 1;  dj = 1;  break;  // southeast
            case 4:   di = 1;  dj = 0;  break;  // south
            case 8:   di = 1;  dj = -1; break;  // southwest
            case 16:  di = 0;  dj = -1; break;  // west
            case 32:  di = -1; dj = -1; break;  // northwest
            case 64:  di = -1; dj = 0;  break;  // north
            case 128: di = -1; dj = 1;  break;  // northeast
            default:
                fprintf(stderr, "Unexpected cell value: %d at (%d, %d)\n", cell, i, j);
                goto cleanup;
        }
        // Move to the next cell
        i += di;
        j += dj;
    }

cleanup:
    // Clean up the visited array
    free(visited);

    // Resize output arrays to the final number of points.
    ii = (int *)realloc(ii, count * sizeof(int));
    jj = (int *)realloc(jj, count * sizeof(int));
    
    // Set the output parameters
    *ii_out = ii;
    *jj_out = jj;
    *npoints = count;
}

#ifdef __cplusplus
}
#endif

#ifdef TEST_FLOWPATH
// A simple test driver for the flowpath function
#include <string.h>
int main() {
    // Example grid (5x5) stored in row-major order.
    // For simplicity, we use a grid with a single flow direction.
    // You can change the values to test different flow scenarios.
    uchar grid[25] = {
         1,   1,   1,   1,   4,
         1, 255,   1, 255,   4,
         1,   1,   4,   16,   16,
         1, 255,   1, 255,   1,
         1,   1,   1,   1,   1,
    };

    int *ii = NULL;
    int *jj = NULL;
    int npoints = 0;
    // Start at cell (0, 0)
    flowpath(grid, 5, 5, 0, 0, &ii, &jj, &npoints);

    printf("Flow path (%d points):\n", npoints);
    for (int k = 0; k < npoints; k++) {
        printf("(%d, %d)\n", ii[k], jj[k]);
    }

    // Free allocated path arrays
    free(ii);
    free(jj);
    return 0;
}
#endif
