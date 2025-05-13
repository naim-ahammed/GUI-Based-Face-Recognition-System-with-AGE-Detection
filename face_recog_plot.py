import matplotlib.pyplot as plt

y_values = [59, 60, 60, 59, 68, 67, 65, 67, 66, 65]
x_values = list(range(1, 11))  


plt.figure(figsize=(10, 5))
plt.plot(x_values, y_values, marker='o', linestyle='-', color='b')


plt.title('Data Points Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('Values')
plt.grid(True)

plt.show()
