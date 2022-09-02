//This was taken from https://gist.github.com/breuderink/bf2cecb2540aa0c4bb2c551ac112aa4d 

// Generate expander graph. See https://mathoverflow.net/q/124714.
// cc expander.c -o expander && ./expander | \
// 	neato -Tpng -o expander.png -Goverlap=false -Gsplines=true

// From https://rosettacode.org/wiki/Modular_inverse#C
int mod_inv(int a, int b) {
	int b0 = b, t, q;
	int x0 = 0, x1 = 1;
	if (b == 1) return 1;
	while (a > 1) {
		q = a / b;
		t = b, b = a % b, a = t;
		t = x0, x0 = x1 - q * x0, x1 = t;
	}
	if (x1 < 0) x1 += b0;
	return x1;
}

#include <stdio.h>

#define N 11
int main() {
	puts("digraph G {\n");

	for (int i = 0; i < N; ++i) {
		printf("N%d -> N%d; ", i, i == 0 ? N - 1 : i-1);
		printf("N%d -> N%d; ", i, i == N - 1 ? 0 : i+1);
		printf("N%d -> N%d; \n", i, i == 0 ? 0 : mod_inv(i, N));
	}

	puts("}\n");
}