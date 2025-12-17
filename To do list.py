
# Class/ Format
class Task:
    def __init__(self, title, due_date):
        self.title = title
        self.due_date = due_date
        self.status = "Not Started"
        self.is_done = False

    def update_status(self, new_status):
        self.status = new_status
        if new_status == "Done":
            self.is_done = True
        else:
            self.is_done = False

    def display(self, index):
        print(f"{index}. {self.title} | Due: {self.due_date} | Status: {self.status}")


# FUNCTIONS/ Main menu/ Arrays

def show_menu():
    print("\n--- TO DO LiST MENU ---")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Update Task Status")
    print("4. Delete Task")
    print("5. Exit")


def add_task(task_list):
    title = input("Enter task title (0 to cancel): ")
    if title == "0":
        return

    due_date = input("Enter due date: ")
    task = Task(title, due_date)
    task_list.append(task)
    print("Task added!")


def view_tasks(task_list):
    if len(task_list) == 0:
        print("No tasks available.")
        return

    for i in range(len(task_list)):
        task_list[i].display(i + 1)


def update_task(task_list):
    view_tasks(task_list)
    if len(task_list) == 0:
        return

    number = int(input(f"Enter task number (1 to {len(task_list)}) or 0 to cancel: "))
    if number == 0:
        return

    if number < 1 or number > len(task_list):
        print("Invalid task number.")
        return

    index = number - 1

    if 0 <= index < len(task_list):
        print("1. Not Started")
        print("2. In Progress")
        print("3. Done")

        choice = int(input("Choose status: "))

        if choice == 1:
            task_list[index].update_status("Not Started")
        elif choice == 2:
            task_list[index].update_status("In Progress")
        elif choice == 3:
            task_list[index].update_status("Done")
        else:
            print("Invalid choice.")
    else:
        print("Invalid task number.")


def delete_task(task_list):
    view_tasks(task_list)
    if len(task_list) == 0:
        return

    number = int(input("Enter task number to delete (0 to cancel): "))
    if number == 0:
        return

    index = number - 1

    if 0 <= index < len(task_list):
        del task_list[index]
        print("Task deleted.")
    else:
        print("Invalid task number.")


# Main Loop

def main():
    task_list = []
    running = True

    while running:
        show_menu()
        choice = int(input("Enter choice: "))

        if choice == 1:
            add_task(task_list)
        elif choice == 2:
            view_tasks(task_list)
        elif choice == 3:
            update_task(task_list)
        elif choice == 4:
            delete_task(task_list)
        elif choice == 5:
            running = False
            print("Goodbye!")
        else:
            print("Invalid choice.")

main()
