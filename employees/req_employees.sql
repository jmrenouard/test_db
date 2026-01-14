-- 1. Simple OLTP lookup by employee number
SELECT * FROM employees WHERE emp_no = 10001;
-- 2. Filter employees hired after a specific date
SELECT * FROM employees WHERE hire_date > '1995-01-01' LIMIT 10;
-- 3. Search for employees by last name prefix
SELECT * FROM employees WHERE last_name LIKE 'Fac%' LIMIT 5;
-- 4. Count total number of employees
SELECT COUNT(*) FROM employees;
-- 5. List employees with a specific gender and birth year
SELECT * FROM employees WHERE gender = 'F' AND birth_date BETWEEN '1960-01-01' AND '1960-12-31' LIMIT 10;
-- 6. Update an employee's first name (OLTP transaction simulation)
UPDATE employees SET first_name = 'Jane' WHERE emp_no = 10002;
-- 7. Retrieve the current salary of a specific employee
SELECT salary FROM salaries WHERE emp_no = 10001 ORDER BY to_date DESC LIMIT 1;
-- 8. List all departments ordered by name
SELECT * FROM departments ORDER BY dept_name;
-- 9. Find employees who are currently managers
SELECT emp_no FROM dept_manager WHERE to_date = '9999-01-01';
-- 10. Simple count of employees per gender
SELECT gender, COUNT(*) FROM employees GROUP BY gender;
-- 11. Join employees with their current department names
SELECT e.first_name, e.last_name, d.dept_name FROM employees e JOIN dept_emp de ON e.emp_no = de.emp_no JOIN departments d ON de.dept_no = d.dept_no WHERE de.to_date = '9999-01-01' LIMIT 10;
-- 12. List all managers with their employee details
SELECT e.first_name, e.last_name, d.dept_name FROM employees e JOIN dept_manager dm ON e.emp_no = dm.emp_no JOIN departments d ON dm.dept_no = d.dept_no;
-- 13. Find the average salary across the entire company
SELECT AVG(salary) FROM salaries;
-- 14. Join titles and employees to see the history of a specific person
SELECT e.first_name, t.title, t.from_date FROM employees e JOIN titles t ON e.emp_no = t.emp_no WHERE e.emp_no = 10005;
-- 15. List the top 5 highest historical salaries
SELECT * FROM salaries ORDER BY salary DESC LIMIT 5;
-- 16. Triple join to find employees, their department, and their title
SELECT e.first_name, d.dept_name, t.title FROM employees e JOIN dept_emp de ON e.emp_no = de.emp_no JOIN departments d ON de.dept_no = d.dept_no JOIN titles t ON e.emp_no = t.emp_no WHERE de.to_date = '9999-01-01' AND t.to_date = '9999-01-01' LIMIT 10;
-- 17. Use a subquery to find employees earning more than the company average
SELECT emp_no, salary FROM salaries WHERE salary > (SELECT AVG(salary) FROM salaries) AND to_date = '9999-01-01' LIMIT 10;
-- 18. Count employees in each department
SELECT d.dept_name, COUNT(de.emp_no) FROM departments d JOIN dept_emp de ON d.dept_no = de.dept_no GROUP BY d.dept_name;
-- 19. Find the maximum salary for each department
SELECT d.dept_name, MAX(s.salary) FROM departments d JOIN dept_emp de ON d.dept_no = de.dept_no JOIN salaries s ON de.emp_no = s.emp_no GROUP BY d.dept_name;
-- 20. List departments with more than 10 managers in history
SELECT dept_no, COUNT(*) FROM dept_manager GROUP BY dept_no HAVING COUNT(*) > 10;
-- 21. CTE to calculate average salary per gender
WITH GenderAvg AS (SELECT gender, AVG(salary) as avg_sal FROM employees e JOIN salaries s ON e.emp_no = s.emp_no GROUP BY gender) SELECT * FROM GenderAvg;
-- 22. Window function: Rank employees by salary within their department
SELECT e.emp_no, de.dept_no, s.salary, RANK() OVER (PARTITION BY de.dept_no ORDER BY s.salary DESC) as sal_rank FROM employees e JOIN dept_emp de ON e.emp_no = de.emp_no JOIN salaries s ON e.emp_no = s.emp_no WHERE de.to_date = '9999-01-01' AND s.to_date = '9999-01-01' LIMIT 20;
-- 23. Window function: Calculate the running total of salaries
SELECT emp_no, salary, SUM(salary) OVER (ORDER BY emp_no) as running_total FROM salaries WHERE to_date = '9999-01-01' LIMIT 20;
-- 24. CTE to find employees with multiple titles over time
WITH MultiTitle AS (SELECT emp_no, COUNT(DISTINCT title) as title_count FROM titles GROUP BY emp_no HAVING title_count > 1) SELECT e.first_name, e.last_name, mt.title_count FROM employees e JOIN MultiTitle mt ON e.emp_no = mt.emp_no LIMIT 10;
-- 25. Window function: Get the previous salary for each employee (LAG)
SELECT emp_no, salary, from_date, LAG(salary) OVER (PARTITION BY emp_no ORDER BY from_date) as prev_salary FROM salaries LIMIT 20;
-- 26. Analytics: Percentile rank of salary within the company
SELECT emp_no, salary, PERCENT_RANK() OVER (ORDER BY salary) as pct_rank FROM salaries WHERE to_date = '9999-01-01' LIMIT 20;
-- 27. Join with aggregation: Departments with the youngest average employee age
SELECT d.dept_name, AVG(YEAR(CURDATE()) - YEAR(e.birth_date)) as avg_age FROM departments d JOIN dept_emp de ON d.dept_no = de.dept_no JOIN employees e ON de.emp_no = e.emp_no GROUP BY d.dept_name ORDER BY avg_age ASC;
-- 28. CTE: Find the highest-paid employee in each title category
WITH TitleMax AS (SELECT t.title, MAX(s.salary) as max_sal FROM titles t JOIN salaries s ON t.emp_no = s.emp_no WHERE t.to_date = '9999-01-01' AND s.to_date = '9999-01-01' GROUP BY t.title) SELECT * FROM TitleMax;
-- 29. Window function: Row number for each employee's salary records
SELECT emp_no, salary, ROW_NUMBER() OVER (PARTITION BY emp_no ORDER BY from_date DESC) as row_num FROM salaries LIMIT 20;
-- 30. Analytics: Salary difference between current and first salary for each employee
WITH FirstLast AS (SELECT emp_no, FIRST_VALUE(salary) OVER (PARTITION BY emp_no ORDER BY from_date) as first_sal, LAST_VALUE(salary) OVER (PARTITION BY emp_no ORDER BY from_date RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as last_sal FROM salaries) SELECT DISTINCT emp_no, last_sal - first_sal as salary_growth FROM FirstLast LIMIT 10;
-- 31. OLTP: Insert a new temporary department (Transaction check)
INSERT INTO departments (dept_no, dept_name) VALUES ('d999', 'Temporary Service');
-- 32. Join: Find employees who have never been managers
SELECT e.first_name, e.last_name FROM employees e LEFT JOIN dept_manager dm ON e.emp_no = dm.emp_no WHERE dm.emp_no IS NULL LIMIT 10;
-- 33. Aggregation: Group by year of hiring
SELECT YEAR(hire_date) as hire_year, COUNT(*) FROM employees GROUP BY hire_year;
-- 34. Window function: Lead salary (Next salary record)
SELECT emp_no, salary, from_date, LEAD(salary) OVER (PARTITION BY emp_no ORDER BY from_date) as next_salary FROM salaries LIMIT 10;
-- 35. CTE: Recursive-like structure for employee seniority brackets
WITH Seniority AS (SELECT emp_no, CASE WHEN hire_date < '1985-01-01' THEN 'Veteran' WHEN hire_date < '1995-01-01' THEN 'Senior' ELSE 'Junior' END as bracket FROM employees) SELECT bracket, COUNT(*) FROM Seniority GROUP BY bracket;
-- 36. Complex Join: Employees, their current manager and their department
SELECT e.first_name as employee, m.first_name as manager, d.dept_name FROM employees e JOIN dept_emp de ON e.emp_no = de.emp_no JOIN departments d ON de.dept_no = d.dept_no JOIN dept_manager dm ON d.dept_no = dm.dept_no JOIN employees m ON dm.emp_no = m.emp_no WHERE de.to_date = '9999-01-01' AND dm.to_date = '9999-01-01';
-- 37. Analytics: Standard deviation of salaries per department
SELECT d.dept_name, STDDEV(s.salary) as sal_stddev FROM departments d JOIN dept_emp de ON d.dept_no = de.dept_no JOIN salaries s ON de.emp_no = s.emp_no GROUP BY d.dept_name;
-- 38. Window function: Dense Rank of employees by seniority (hire_date)
SELECT emp_no, hire_date, DENSE_RANK() OVER (ORDER BY hire_date) as seniority_rank FROM employees LIMIT 20;
-- 39. Subquery: Departments where at least one employee earns > 150000
SELECT dept_name FROM departments WHERE dept_no IN (SELECT dept_no FROM dept_emp de JOIN salaries s ON de.emp_no = s.emp_no WHERE s.salary > 140000);
-- 40. Aggregation: Find the month with the most hirings historically
SELECT MONTH(hire_date) as hire_month, COUNT(*) as count FROM employees GROUP BY hire_month ORDER BY count DESC LIMIT 1;
-- 41. CTE with multiple steps: Identify high flyers (salary growth > 50%)
WITH InitialSal AS (SELECT emp_no, salary as start_sal FROM salaries WHERE from_date = (SELECT MIN(from_date) FROM salaries s2 WHERE s2.emp_no = salaries.emp_no)), CurrentSal AS (SELECT emp_no, salary as curr_sal FROM salaries WHERE to_date = '9999-01-01') SELECT i.emp_no, i.start_sal, c.curr_sal FROM InitialSal i JOIN CurrentSal c ON i.emp_no = c.emp_no WHERE c.curr_sal > i.start_sal * 1.5;
-- 42. Window function: NTile(4) to split employees into 4 salary quartiles
SELECT emp_no, salary, NTILE(4) OVER (ORDER BY salary) as quartile FROM salaries WHERE to_date = '9999-01-01';
-- 43. Join: Employees who switched departments at least once
SELECT e.emp_no, e.first_name, COUNT(de.dept_no) FROM employees e JOIN dept_emp de ON e.emp_no = de.emp_no GROUP BY e.emp_no HAVING COUNT(de.dept_no) > 1 LIMIT 10;
-- 44. Analytics: Ratio of average salary in department vs company average
SELECT d.dept_name, AVG(s.salary) / (SELECT AVG(salary) FROM salaries) as sal_ratio FROM departments d JOIN dept_emp de ON d.dept_no = de.dept_no JOIN salaries s ON de.emp_no = s.emp_no GROUP BY d.dept_name;
-- 45. Window function: Cume_Dist of hiring dates
SELECT emp_no, hire_date, CUME_DIST() OVER (ORDER BY hire_date) as dist FROM employees LIMIT 20;
-- 46. OLTP: Delete the temporary department added earlier
DELETE FROM departments WHERE dept_no = 'd999';
-- 47. Aggregation: Median-like salary (using ranking as MySQL has no MEDIAN)
SELECT salary FROM (SELECT salary, ROW_NUMBER() OVER (ORDER BY salary) as row_id, COUNT(*) OVER () as total_count FROM salaries WHERE to_date = '9999-01-01') as t WHERE row_id = FLOOR(total_count/2);
-- 48. Join: List employees who are managed by someone younger than them
SELECT e.first_name, e.birth_date as emp_birth, m.first_name as mgr_name, m.birth_date as mgr_birth FROM employees e JOIN dept_emp de ON e.emp_no = de.emp_no JOIN dept_manager dm ON de.dept_no = dm.dept_no JOIN employees m ON dm.emp_no = m.emp_no WHERE e.birth_date < m.birth_date AND de.to_date = '9999-01-01' AND dm.to_date = '9999-01-01';
-- 49. CTE: Find the 'Gap' years where no one was hired
WITH Years AS (SELECT DISTINCT YEAR(hire_date) as y FROM employees) SELECT t1.y + 1 FROM Years t1 WHERE NOT EXISTS (SELECT 1 FROM Years t2 WHERE t2.y = t1.y + 1) AND t1.y < (SELECT MAX(y) FROM Years);
-- 50. Analytics: Top 1% earners in each department
WITH Ranked AS (SELECT emp_no, dept_no, salary, PERCENT_RANK() OVER (PARTITION BY dept_no ORDER BY salary DESC) as p_rank FROM salaries s JOIN dept_emp de ON s.emp_no = de.emp_no WHERE s.to_date = '9999-01-01' AND de.to_date = '9999-01-01') SELECT * FROM Ranked WHERE p_rank <= 0.01;
-- 51. Window Function: Moving average of salaries (prev 2 records)
SELECT emp_no, salary, AVG(salary) OVER (PARTITION BY emp_no ORDER BY from_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as moving_avg FROM salaries;
-- 52. Join: Employees with their very first title and their very first salary
SELECT e.emp_no, t.title, s.salary FROM employees e JOIN titles t ON e.emp_no = t.emp_no JOIN salaries s ON e.emp_no = s.emp_no WHERE t.from_date = e.hire_date AND s.from_date = e.hire_date LIMIT 10;
-- 53. Aggregation: Total salary budget per year
SELECT YEAR(from_date) as year, SUM(salary) FROM salaries GROUP BY year;
-- 54. Analytics: Department mobility - employees who worked in > 2 departments
SELECT emp_no FROM dept_emp GROUP BY emp_no HAVING COUNT(DISTINCT dept_no) > 2;
-- 55. CTE: Daily hiring rate average
WITH DailyHires AS (SELECT hire_date, COUNT(*) as count FROM employees GROUP BY hire_date) SELECT AVG(count) FROM DailyHires;
-- 56. Window Function: Find if current salary is the all-time max for that employee
SELECT emp_no, salary, MAX(salary) OVER (PARTITION BY emp_no) as max_sal, CASE WHEN salary = MAX(salary) OVER (PARTITION BY emp_no) THEN 'YES' ELSE 'NO' END as is_max FROM salaries WHERE to_date = '9999-01-01';
-- 57. Join: List all employees who were hired in the same month as their birth month
SELECT emp_no, first_name, birth_date, hire_date FROM employees WHERE MONTH(birth_date) = MONTH(hire_date) LIMIT 10;
-- 58. Aggregation: Most common last name in the company
SELECT last_name, COUNT(*) as count FROM employees GROUP BY last_name ORDER BY count DESC LIMIT 1;
-- 59. Window Function: Last hire in each department (ROW_NUMBER)
SELECT * FROM (SELECT e.emp_no, de.dept_no, e.hire_date, ROW_NUMBER() OVER (PARTITION BY de.dept_no ORDER BY e.hire_date DESC) as last_hired FROM employees e JOIN dept_emp de ON e.emp_no = de.emp_no) t WHERE last_hired = 1;
-- 60. Complex Analytics: Gender salary gap per department
SELECT d.dept_name, AVG(CASE WHEN e.gender = 'M' THEN s.salary END) as male_avg, AVG(CASE WHEN e.gender = 'F' THEN s.salary END) as female_avg FROM departments d JOIN dept_emp de ON d.dept_no = de.dept_no JOIN employees e ON de.emp_no = e.emp_no JOIN salaries s ON e.emp_no = s.emp_no WHERE de.to_date = '9999-01-01' AND s.to_date = '9999-01-01' GROUP BY d.dept_name;
