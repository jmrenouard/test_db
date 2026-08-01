#!/usr/bin/env python3
"""
scripts/inject_fake_employees.py
================================================================================
Python Data Faker Employee Injection Tool
================================================================================
Purpose:
  Generates and injects synthetic employee data into the `employees` database
  using the Python Faker library (or a built-in fallback generator).

Usage:
  python3 scripts/inject_fake_employees.py --count 50
  python3 scripts/inject_fake_employees.py --count 100 --dry-run
  python3 scripts/inject_fake_employees.py --count 20 --output-sql /tmp/fake.sql
================================================================================
"""

import os
import sys
import random
import argparse
import subprocess
from datetime import datetime, timedelta

# Try importing Faker, provide robust fallback if missing
try:
    from faker import Faker
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False


class FallbackFaker:
    """Minimal fake data generator when 'faker' package is not installed."""
    FIRST_NAMES_M = [
        "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
        "Thomas", "Charles", "Christopher", "Daniel", "Matthew", "Anthony", "Mark",
        "Donald", "Steven", "Paul", "Andrew", "Joshua", "Kenneth", "Kevin", "Brian"
    ]
    FIRST_NAMES_F = [
        "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan",
        "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Sandra", "Margaret",
        "Ashley", "Kimberly", "Emily", "Donna", "Michelle", "Carol", "Amanda", "Melissa"
    ]
    LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
        "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson"
    ]

    def first_name_male(self):
        return random.choice(self.FIRST_NAMES_M)[:14]

    def first_name_female(self):
        return random.choice(self.FIRST_NAMES_F)[:14]

    def last_name(self):
        return random.choice(self.LAST_NAMES)[:16]


DEPARTMENTS = ["d001", "d002", "d003", "d004", "d005", "d006", "d007", "d008", "d009"]
TITLES = [
    "Senior Engineer", "Staff", "Engineer", "Senior Staff",
    "Assistant Engineer", "Technique Leader", "Manager"
]


def generate_fake_employees(count, start_emp_no, seed=None):
    """Generates lists of tuples for employees, dept_emp, titles, and salaries."""
    if seed is not None:
        random.seed(seed)

    if FAKER_AVAILABLE:
        fake = Faker()
        if seed is not None:
            Faker.seed(seed)
    else:
        fake = FallbackFaker()

    employees = []
    dept_emps = []
    titles = []
    salaries = []

    current_emp_no = start_emp_no
    base_date = datetime(2020, 1, 1)

    for i in range(count):
        gender = random.choice(['M', 'F'])
        if FAKER_AVAILABLE:
            first_name = (fake.first_name_male() if gender == 'M' else fake.first_name_female())[:14]
            last_name = fake.last_name()[:16]
        else:
            first_name = (fake.first_name_male() if gender == 'M' else fake.first_name_female())[:14]
            last_name = fake.last_name()[:16]

        # Escape single quotes in names if any
        first_name = first_name.replace("'", "''")
        last_name = last_name.replace("'", "''")

        # Birth date between 1965 and 2000
        birth_year = random.randint(1965, 2000)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        birth_date = f"{birth_year:04d}-{birth_month:02d}-{birth_day:02d}"

        # Hire date between 2010 and 2024
        hire_year = random.randint(2010, 2024)
        hire_month = random.randint(1, 12)
        hire_day = random.randint(1, 28)
        hire_date = f"{hire_year:04d}-{hire_month:02d}-{hire_day:02d}"

        dept_no = random.choice(DEPARTMENTS)
        title = random.choice(TITLES)
        salary = random.randint(45000, 135000)

        employees.append((current_emp_no, birth_date, first_name, last_name, gender, hire_date))
        dept_emps.append((current_emp_no, dept_no, hire_date, '9999-01-01'))
        titles.append((current_emp_no, title, hire_date, '9999-01-01'))
        salaries.append((current_emp_no, salary, hire_date, '9999-01-01'))

        current_emp_no += 1

    return employees, dept_emps, titles, salaries


def build_sql_script(employees, dept_emps, titles, salaries, db_name="employees"):
    """Converts data tuples into executable SQL statements."""
    lines = [
        f"USE `{db_name}`;",
        "SET FOREIGN_KEY_CHECKS = 0;",
        "START TRANSACTION;"
    ]

    # Employees
    lines.append("\n-- Inject fake employees")
    emp_vals = [
        f"({emp_no}, '{birth_date}', '{first_name}', '{last_name}', '{gender}', '{hire_date}')"
        for emp_no, birth_date, first_name, last_name, gender, hire_date in employees
    ]
    lines.append(f"INSERT INTO employees (emp_no, birth_date, first_name, last_name, gender, hire_date) VALUES\n" + ",\n".join(emp_vals) + ";")

    # Dept_emp
    lines.append("\n-- Inject department assignments")
    de_vals = [
        f"({emp_no}, '{dept_no}', '{from_date}', '{to_date}')"
        for emp_no, dept_no, from_date, to_date in dept_emps
    ]
    lines.append(f"INSERT INTO dept_emp (emp_no, dept_no, from_date, to_date) VALUES\n" + ",\n".join(de_vals) + ";")

    # Titles
    lines.append("\n-- Inject titles")
    title_vals = [
        f"({emp_no}, '{title}', '{from_date}', '{to_date}')"
        for emp_no, title, from_date, to_date in titles
    ]
    lines.append(f"INSERT INTO titles (emp_no, title, from_date, to_date) VALUES\n" + ",\n".join(title_vals) + ";")

    # Salaries
    lines.append("\n-- Inject salaries")
    sal_vals = [
        f"({emp_no}, {salary}, '{from_date}', '{to_date}')"
        for emp_no, salary, from_date, to_date in salaries
    ]
    lines.append(f"INSERT INTO salaries (emp_no, salary, from_date, to_date) VALUES\n" + ",\n".join(sal_vals) + ";")

    lines.append("\nCOMMIT;")
    lines.append("SET FOREIGN_KEY_CHECKS = 1;")
    return "\n".join(lines)


def get_max_emp_no(container, db_name, use_container):
    """Fetches current MAX(emp_no) from DB to avoid primary key collisions."""
    query = f"SELECT COALESCE(MAX(emp_no), 500000) FROM {db_name}.employees;"
    try:
        if use_container and container:
            cmd = ["docker", "exec", "-i", container, "mariadb", "-u", "root", "-N", "-e", query]
        else:
            cmd = ["mariadb", "-u", "root", "-N", "-e", query]
        
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        val = res.stdout.strip()
        if val and val.isdigit():
            return int(val) + 1
    except Exception:
        pass
    return 500001


def main():
    parser = argparse.ArgumentParser(description="Inject synthetic employee data generated via Python Faker.")
    parser.add_argument("--count", type=int, default=10, help="Number of fake employees to create (default: 10).")
    parser.add_argument("--start-emp-no", type=int, default=None, help="Starting emp_no (default: auto-detected from DB).")
    parser.add_argument("--db-name", type=str, default="employees", help="Target database name (default: employees).")
    parser.add_argument("--container", type=str, default=os.environ.get("CONTAINER_NAME", "mariadb-11-8"), help="Target Docker container.")
    parser.add_argument("--use-container", type=str, default=os.environ.get("USE_CONTAINER", "true"), help="Use Docker container (true/false).")
    parser.add_argument("--dry-run", action="store_true", help="Output generated SQL to stdout without executing.")
    parser.add_argument("--output-sql", type=str, default=None, help="Write generated SQL script to specified file path.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for deterministic generation.")

    args = parser.parse_args()

    use_container = args.use_container.lower() not in ("false", "0", "no", "off", "disable")

    if not FAKER_AVAILABLE and not args.dry_run:
        print("[INFO] 'faker' python package not found; using built-in synthetic generator.", file=sys.stderr)

    start_emp_no = args.start_emp_no
    if start_emp_no is None:
        if not args.dry_run and args.output_sql is None:
            start_emp_no = get_max_emp_no(args.container, args.db_name, use_container)
        else:
            start_emp_no = 500001

    employees, dept_emps, titles, salaries = generate_fake_employees(args.count, start_emp_no, args.seed)
    sql_script = build_sql_script(employees, dept_emps, titles, salaries, db_name=args.db_name)

    if args.dry_run:
        print(sql_script)
        return

    if args.output_sql:
        with open(args.output_sql, "w", encoding="utf-8") as f:
            f.write(sql_script)
        print(f"✅ Generated SQL script written to {args.output_sql} ({args.count} employees).")
        return

    # Execute SQL script against MariaDB
    try:
        if use_container:
            cmd = ["docker", "exec", "-i", args.container, "mariadb", "-u", "root"]
        else:
            cmd = ["mariadb", "-u", "root"]

        proc = subprocess.run(cmd, input=sql_script, text=True, capture_output=True, check=True)
        print(f"✅ Successfully injected {args.count} synthetic employees (emp_no: {start_emp_no} .. {start_emp_no + args.count - 1}).")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to inject fake employees: {e.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"❌ Command execution error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
