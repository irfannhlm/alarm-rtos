import pyRTOS
import sys

# Define Task 1
def task1(self):
    while True:
        print("Hello from task 1")
        yield [pyRTOS.timeout(1000)]  # Wait for 1 second

# Define Task 2
def task2(self):
    while True:
        print("Hello from task 2")
        yield [pyRTOS.timeout(1000)]  # Wait for 1 second

# Define the main function to handle the interrupt
def main():
    # Create tasks
    t1 = pyRTOS.Task(task1, name="Task 1", priority=1)
    t2 = pyRTOS.Task(task2, name="Task 2", priority=1)

    # Add tasks to the RTOS
    pyRTOS.add_task(t1)
    pyRTOS.add_task(t2)

    # Start the RTOS
    pyRTOS.start()

    # Monitor for interrupt input
    while True:
        if sys.stdin.read(1) == "interrupt":
            print("Tasks are interrupted")
            pyRTOS.remove_task(t1)
            pyRTOS.remove_task(t2)
            break

# Run the main function
main()

