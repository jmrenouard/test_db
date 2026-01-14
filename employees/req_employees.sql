-- Query 1: Simple count (Fast)
SELECT COUNT(*) FROM employees;

-- Query 2: Filter by first_name (Full Table Scan - no index)
SELECT * FROM employees WHERE first_name = 'Georgi';

-- Query 3: Join employees with departments (Efficient join)
SELECT e.first_name, e.last_name, d.dept_name 
FROM employees e 
JOIN dept_emp de ON e.emp_no = de.emp_no 
JOIN departments d ON de.dept_no = d.dept_no 
LIMIT 20;

-- Query 4: Filter by salary (Full Table Scan - no index on salary)
SELECT * FROM salaries WHERE salary > 120000;

-- Query 5: Group by gender
SELECT gender, COUNT(*) FROM employees GROUP BY gender;

-- Query 6: Subquery example
SELECT * FROM employees 
WHERE emp_no IN (SELECT emp_no FROM dept_manager);

-- Query 7: Average salary per department (Aggregates + Joins)
SELECT d.dept_name, AVG(s.salary) as avg_salary
FROM departments d
JOIN dept_emp de ON d.dept_no = de.dept_no
JOIN salaries s ON de.emp_no = s.emp_no
GROUP BY d.dept_name;

-- Query 8: Top 10 highest paid employees with their current titles
SELECT e.first_name, e.last_name, s.salary, t.title
FROM employees e
JOIN salaries s ON e.emp_no = s.emp_no
JOIN titles t ON e.emp_no = t.emp_no
WHERE s.to_date = '9999-01-01' AND t.to_date = '9999-01-01'
ORDER BY s.salary DESC
LIMIT 10;

-- Query 9: Department manager history for a specific department
SELECT e.first_name, e.last_name, dm.from_date, dm.to_date
FROM employees e
JOIN dept_manager dm ON e.emp_no = dm.emp_no
JOIN departments d ON dm.dept_no = d.dept_no
WHERE d.dept_name = 'Sales'
ORDER BY dm.from_date;
