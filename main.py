from dataclasses import dataclass
import math
from drafter import *

set_website_title("construction-manager-site")
set_site_information(
    author="Mason Pust",
    description="Manage construction projects.",
    sources="Thanks to the Drafter docs and my study group.",
    planning=["CS1-0.pdf", "CS1-1.pdf"],
    links=["https://github.com/mhpust-cyber/construction-manager-site/blob/main/CS1-0.pdf", "https://github.com/mhpust-cyber/construction-manager-site/blob/main/CS1-1.pdf"],
)
hide_debug_information()
set_website_framed(False)

# ---------------------------------
# DATA CLASSES
# ---------------------------------

@dataclass
class Project:
    """A construction project.

    ADVANCED TECHNIQUE NOTE: Progress is NOT stored here. It is always
    calculated from the project's tasks by calculate_progress(), so the
    number can never get out of sync with the task list.
    """
    name: str
    location: str
    description: str
    budget: float


@dataclass
class Task:
    """A task that belongs to one project (linked by project name)."""
    name: str
    project_name: str
    description: str
    status: str


@dataclass
class Material:
    """A material purchase for one project (linked by project name)."""
    name: str
    project_name: str
    amount: float
    unit: str
    price: float


@dataclass
class State:
    """The website's saved data.

    ADVANCED TECHNIQUE NOTE: The type hints list[Project], list[Task], and
    list[Material] say what kind of object each list holds.

    Fields:
        projects, tasks, materials: lists of dataclass instances
        selected_project: name of the project the user last viewed or added
            to. It is used as the default choice in the "Add" forms.
        message: feedback (success or error) shown on the next page
    """
    projects: list[Project]
    tasks: list[Task]
    materials: list[Material]
    selected_project: str
    message: str


# ---------------------------------
# CONSTANTS
# ---------------------------------

TASK_STATUSES = [
    "Not Started",
    "In Progress",
    "Completed"
]

MATERIAL_UNITS = [
    "pounds",
    "tons",
    "ounces",
    "grams",
    "kilograms",
    "pieces",
    "feet",
    "inches",
    "yards",
    "meters",
    "square feet",
    "square yards",
    "cubic feet",
    "cubic yards",
    "gallons",
    "liters",
    "bags",
    "boxes",
    "loads"
]


# ---------------------------------
# HELPER FUNCTIONS
# ---------------------------------

def parse_number(text: str) -> float | None:
    """Convert text typed by the user into a number, or return None.

    ADVANCED TECHNIQUES USED HERE:

    1. try/except: Python tries to run float(text). If the user typed
       something that is not a number (like "abc" or an empty box), float()
       raises a ValueError. The except block catches that error so the
       program does not crash, and we return None instead.

    2. The return type hint "float | None" means "this function returns
       either a float or None".

    3. math.isfinite(): float() accepts the strings "nan" and "inf", which
       are not real prices or quantities. isfinite() returns False for them,
       so we reject them too.
    """
    try:
        value = float(text)
    except ValueError:
        return None

    if not math.isfinite(value):
        return None

    return value


def format_money(value: float) -> str:
    """Return a number as a money string such as "$1,234.50".

    ADVANCED TECHNIQUE: f-string format specifier. Inside an f-string,
    {value:,.2f} means: format value as a float (f) with 2 digits after
    the decimal point (.2) and commas as thousands separators (,).
    This avoids ugly floating point output like $30.299999999999997.
    """
    return f"${value:,.2f}"


def take_message(state: State) -> str:
    """Return the current message and clear it so it only shows once.

    Each page calls this when it is built, so an error or success message
    appears on the page the user actually sees, and does not stay around
    afterward.
    """
    message = state.message
    state.message = ""
    return message


def find_project(state: State, project_name: str) -> Project | None:
    """Return the Project with the given name, or None if it does not exist.

    ADVANCED TECHNIQUE: "Project | None" in the return type hint means
    the function returns either a Project or None.
    """
    for project in state.projects:
        if project.name == project_name:
            return project

    return None


def calculate_progress(state: State, project_name: str) -> float:
    """Return the percentage (0 to 100) of a project's tasks that are Completed."""
    total_tasks = 0
    completed_tasks = 0

    for task in state.tasks:
        if task.project_name == project_name:
            total_tasks += 1

            if task.status == "Completed":
                completed_tasks += 1

    if total_tasks == 0:
        return 0.0

    return completed_tasks / total_tasks * 100


def calculate_material_cost(state: State, project_name: str) -> float:
    """Return the total cost (amount * price) of all materials for a project."""
    total_cost = 0.0

    for material in state.materials:
        if material.project_name == project_name:
            total_cost += material.amount * material.price

    return total_cost


def default_project_choice(state: State, project_options: list[str]) -> str:
    """Pick which project should be pre-selected in an "Add" form.

    Uses the project the user last viewed (state.selected_project) if it
    still exists; otherwise falls back to the first project.
    """
    if state.selected_project in project_options:
        return state.selected_project

    return project_options[0]


# ---------------------------------
# HOME PAGE
# ---------------------------------

@route
def index(state: State) -> Page:
    return home(state)


@route
def home(state: State) -> Page:
    return Page(state, [
        Header("Construction Project Manager"),
        take_message(state),
        "Organize construction projects, track progress, and manage material costs.",

        Header("Main Menu", 2),

        Button("Projects", "projects"),
        Button("Tasks", "tasks"),
        Button("Materials", "materials"),
        Button("Budget Summary", "budget_summary")
    ])


# ---------------------------------
# PROJECT ROUTES
# ---------------------------------

@route
def projects(state: State) -> Page:
    content = [
        Header("Construction Projects"),
        take_message(state),
        Button("Add a Project", "add_project"),
        HorizontalRule()
    ]

    if len(state.projects) == 0:
        content.append("No projects have been added yet.")

    for project in state.projects:
        progress = calculate_progress(state, project.name)

        content.append(Header(project.name, 2))
        content.append("Location: " + project.location)
        content.append("Budget: " + format_money(project.budget))
        content.append("Completion: " + str(round(progress, 1)) + "%")

        content.append(
            Button(
                "View Project Details",
                "project_details",
                [Argument("project_name", project.name)]
            )
        )

        content.append(HorizontalRule())

    content.append(Button("Home", "home"))

    return Page(state, content)


@route
def add_project(state: State) -> Page:
    return Page(state, [
        Header("Add a New Project"),
        take_message(state),

        "Project Name:",
        TextBox("project_name", ""),

        "Project Location:",
        TextBox("project_location", ""),

        "Project Description:",
        TextArea("project_description", ""),

        "Project Budget:",
        TextBox("project_budget", "0"),

        Button("Save Project", "save_project"),
        Button("Cancel", "projects")
    ])


@route
def save_project(
    state: State,
    project_name: str,
    project_location: str,
    project_description: str,
    project_budget: str
) -> Page:
    # project_budget arrives as text from the TextBox, so we convert it
    # ourselves with parse_number() (which uses try/except).
    budget = parse_number(project_budget)

    if project_name.strip() == "":
        state.message = "Please enter a project name."
        return add_project(state)

    if find_project(state, project_name.strip()) is not None:
        state.message = "A project with that name already exists."
        return add_project(state)

    if project_location.strip() == "":
        state.message = "Please enter a project location."
        return add_project(state)

    if budget is None:
        state.message = "The project budget must be a number."
        return add_project(state)

    if budget < 0:
        state.message = "The project budget cannot be negative."
        return add_project(state)

    new_project = Project(
        project_name.strip(),
        project_location.strip(),
        project_description,
        budget
    )

    state.projects.append(new_project)
    state.selected_project = new_project.name
    state.message = "Project successfully added!"

    return projects(state)


@route
def project_details(state: State, project_name: str) -> Page:
    found_project = find_project(state, project_name)

    if found_project is None:
        return Page(state, [
            Header("Project Not Found"),
            Button("View Projects", "projects"),
            Button("Home", "home")
        ])

    # Remember which project the user is looking at so the "Add a Task"
    # and "Add Materials" forms can pre-select it.
    state.selected_project = project_name

    progress = calculate_progress(state, project_name)
    material_cost = calculate_material_cost(state, project_name)
    budget_remaining = found_project.budget - material_cost

    content = [
        Header("Project Details"),
        take_message(state),
        Header(found_project.name, 2),
        "Location: " + found_project.location,
        "Description: " + found_project.description,
        "Project Budget: " + format_money(found_project.budget),
        "Completion: " + str(round(progress, 1)) + "%",
        "Material Costs: " + format_money(material_cost),
        "Budget Remaining: " + format_money(budget_remaining),
        HorizontalRule(),
        Header("Project Tasks", 2)
    ]

    found_task = False

    for task in state.tasks:
        if task.project_name == project_name:
            found_task = True
            content.append(task.name + " - " + task.status)

    if not found_task:
        content.append("No tasks have been added to this project.")

    content.append(HorizontalRule())
    content.append(Button("Add a Task", "add_task"))
    content.append(Button("Add Materials", "add_material"))
    content.append(Button("View Projects", "projects"))
    content.append(Button("Home", "home"))

    return Page(state, content)


# ---------------------------------
# TASK ROUTES
# ---------------------------------

@route
def tasks(state: State) -> Page:
    content = [
        Header("Project Tasks"),
        take_message(state),
        Button("Add a Task", "add_task"),
        HorizontalRule()
    ]

    if len(state.tasks) == 0:
        content.append("No tasks have been added yet.")

    for task_number in range(len(state.tasks)):
        task = state.tasks[task_number]

        content.append(Header(task.name, 2))
        content.append("Project: " + task.project_name)
        content.append("Description: " + task.description)
        content.append("Status: " + task.status)

        content.append("Change Status:")

        for status in TASK_STATUSES:
            content.append(
                Button(
                    status,
                    "update_task_status",
                    [
                        Argument("task_number", task_number),
                        Argument("new_status", status)
                    ]
                )
            )

        content.append(HorizontalRule())

    content.append(Button("Home", "home"))

    return Page(state, content)


@route
def add_task(state: State) -> Page:
    project_options = []

    for project in state.projects:
        project_options.append(project.name)

    if len(project_options) == 0:
        return Page(state, [
            Header("Add a Task"),
            "You must create a project first.",
            Button("Add a Project", "add_project"),
            Button("Home", "home")
        ])

    return Page(state, [
        Header("Add a New Task"),
        take_message(state),

        "Task Name:",
        TextBox("task_name", ""),

        "Choose a Project:",
        SelectBox(
            "project_name",
            project_options,
            default_project_choice(state, project_options)
        ),

        "Task Description:",
        TextArea("task_description", ""),

        "Task Status:",
        SelectBox("task_status", TASK_STATUSES, "Not Started"),

        Button("Save Task", "save_task"),
        Button("Cancel", "tasks")
    ])


@route
def save_task(
    state: State,
    task_name: str,
    project_name: str,
    task_description: str,
    task_status: str
) -> Page:

    if task_name.strip() == "":
        state.message = "Please enter a task name."
        return add_task(state)

    if task_status not in TASK_STATUSES:
        state.message = "Please select a valid task status."
        return add_task(state)

    new_task = Task(
        task_name.strip(),
        project_name,
        task_description,
        task_status
    )

    state.tasks.append(new_task)
    state.selected_project = project_name
    state.message = "Task successfully added!"

    return tasks(state)


@route
def update_task_status(
    state: State,
    task_number: int,
    new_status: str
) -> Page:

    if task_number < 0 or task_number >= len(state.tasks):
        state.message = "That task could not be found."
        return tasks(state)

    if new_status not in TASK_STATUSES:
        state.message = "Please select a valid status."
        return tasks(state)

    state.tasks[task_number].status = new_status
    state.message = "Task status successfully updated!"

    return tasks(state)


# ---------------------------------
# MATERIAL ROUTES
# ---------------------------------

@route
def materials(state: State) -> Page:
    content = [
        Header("Construction Materials"),
        take_message(state),
        Button("Add a Material", "add_material"),
        HorizontalRule()
    ]

    if len(state.materials) == 0:
        content.append("No materials have been added yet.")

    for material in state.materials:
        total_cost = material.amount * material.price

        content.append(Header(material.name, 2))
        content.append("Project: " + material.project_name)
        content.append(
            "Quantity: " + str(material.amount) + " " + material.unit
        )
        content.append("Price Per Unit: " + format_money(material.price))
        content.append("Total Cost: " + format_money(total_cost))
        content.append(HorizontalRule())

    content.append(Button("Home", "home"))

    return Page(state, content)


@route
def add_material(state: State) -> Page:
    project_options = []

    for project in state.projects:
        project_options.append(project.name)

    if len(project_options) == 0:
        return Page(state, [
            Header("Add a Material"),
            "You must create a project first.",
            Button("Add a Project", "add_project"),
            Button("Home", "home")
        ])

    return Page(state, [
        Header("Add a New Material"),
        take_message(state),

        "Material Name:",
        TextBox("material_name", ""),

        "Choose a Project:",
        SelectBox(
            "project_name",
            project_options,
            default_project_choice(state, project_options)
        ),

        "Quantity (numbers only):",
        TextBox("amount", "1"),

        "Select Material Unit:",
        SelectBox("unit", MATERIAL_UNITS, "pounds"),

        "Price Per Unit:",
        TextBox("price", "0"),

        Button("Save Material", "save_material"),
        Button("Cancel", "materials")
    ])


@route
def save_material(
    state: State,
    material_name: str,
    project_name: str,
    amount: str,
    unit: str,
    price: str
) -> Page:
    # amount and price arrive as text from TextBoxes, so we convert them
    # ourselves with parse_number() (which uses try/except).
    amount_number = parse_number(amount)
    price_number = parse_number(price)

    if material_name.strip() == "":
        state.message = "Please enter a material name."
        return add_material(state)

    if amount_number is None:
        state.message = "Quantity must be a number."
        return add_material(state)

    if amount_number <= 0:
        state.message = "Quantity must be greater than zero."
        return add_material(state)

    if price_number is None:
        state.message = "Price must be a number."
        return add_material(state)

    if price_number < 0:
        state.message = "Price cannot be negative."
        return add_material(state)

    if unit not in MATERIAL_UNITS:
        state.message = "Please select a valid material unit."
        return add_material(state)

    new_material = Material(
        material_name.strip(),
        project_name,
        amount_number,
        unit,
        price_number
    )

    state.materials.append(new_material)
    state.selected_project = project_name
    state.message = "Material successfully added!"

    return materials(state)


# ---------------------------------
# BUDGET SUMMARY
# ---------------------------------

@route
def budget_summary(state: State) -> Page:
    content = [
        Header("Project Budget Summary"),
        take_message(state)
    ]

    if len(state.projects) == 0:
        content.append("Create a project to view its budget summary.")

    for project in state.projects:
        material_cost = calculate_material_cost(state, project.name)
        remaining_budget = project.budget - material_cost

        content.append(HorizontalRule())
        content.append(Header(project.name, 2))
        content.append("Location: " + project.location)
        content.append("Original Budget: " + format_money(project.budget))
        content.append("Material Costs: " + format_money(material_cost))
        content.append("Remaining Budget: " + format_money(remaining_budget))

        if remaining_budget < 0:
            content.append("Warning: This project is over budget!")
        else:
            content.append("This project is within its material budget.")

    content.append(HorizontalRule())
    content.append(Button("Home", "home"))

    return Page(state, content)


# ---------------------------------
# START THE WEBSITE
# ---------------------------------

start_server(
    State(
        [],
        [],
        [],
        "",
        "Welcome to your Construction Project Manager!"
    )
)
