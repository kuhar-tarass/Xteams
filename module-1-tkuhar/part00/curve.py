import numpy as np
import matplotlib.pyplot as plt

def main():
	a = 5
	b = 5

	y, x = np.ogrid[-5:5:100j, -5:5:100j]
	plt.contour(x.ravel(),y.ravel(), pow(y, 2) - pow(x, 3) - x * a - b, [0])
	plt.grid()
	plt.savefig("1.png")

if __name__ == '__main__':
	main()