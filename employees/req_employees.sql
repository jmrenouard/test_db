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
