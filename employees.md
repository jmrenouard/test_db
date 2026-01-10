# **📊 SQL Queries for the Employees Database**

[**📊 SQL Queries for the Employees Database	1**](?tab=t.0#heading=)

[🗂️ Relational Schema Structure	1](?tab=t.0#heading=)

[🚀 Table of 60 SQL Queries	2](?tab=t.0#heading=)

This document lists 60 SQL queries optimized for MySQL 8.0, covering complex data analysis, reporting, and manipulation scenarios.

## **🗂️ Relational Schema Structure**

Here is a visual representation of the relationships between the tables in the employees database.

``mermaid
erDiagram
    EMPLOYEES ||--o{ SALARIES : "has"
    EMPLOYEES ||--o{ TITLES : "has"
    EMPLOYEES ||--o{ DEPT_EMP : "works in"
    EMPLOYEES ||--o{ DEPT_MANAGER : "manages"
    DEPARTMENTS ||--o{ DEPT_EMP : "contains"
    DEPARTMENTS ||--o{ DEPT_MANAGER : "is managed by"

    EMPLOYEES {
        int emp_no PK
        date birth_date
        string first_name
        string last_name
        enum gender
        date hire_date
    }

    DEPARTMENTS {
        char(4) dept_no PK
        string dept_name
    }

    SALARIES {
        int emp_no PK
        int salary
        date from_date PK
        date to_date
    }

    TITLES {
        int emp_no PK
        string title PK
        date from_date PK
        date to_date
    }

``

## **🚀 Table of 60 SQL Queries**

| # | Tables Used | Query Type | Description & SQL Code |
| :---- | :---- | :---- | :---- |
| **1** | employees, salaries | **Simple Join** | **List of employees with their current salary** SELECT e.first_name, e.last_name, s.salary FROM employees e JOIN salaries s ON e.emp_no = s.emp_no WHERE s.to_date = '9999-01-01'; |
| **2** | employees, dept_emp, departments | **Multiple Join** | **Employees and their current departments** SELECT e.first_name, e.last_name, d.dept_name FROM employees e JOIN dept_emp de ON e.emp_no = de.emp_no JOIN departments d ON de.dept_no = d.dept_no WHERE de.to_date = '9999-01-01'; |
| **3** | employees | **Aggregate (COUNT)** | **Total number of employees by gender** SELECT gender, COUNT(*) as count FROM employees GROUP BY gender; |
| **4** | salaries | **Aggregate (AVG)** | **Current overall average salary** SELECT AVG(salary) as avg_salary FROM salaries WHERE to_date = '9999-01-01'; |
| **5** | salaries, dept_emp, departments | **Aggregate + Join** | **Average salary by department** SELECT d.dept_name, AVG(s.salary) as avg_dept_salary FROM departments d JOIN dept_emp de ON d.dept_no = de.dept_no JOIN salaries s ON de.emp_no = s.emp_no WHERE s.to_date = '9999-01-01' AND de.to_date = '9999-01-01' GROUP BY d.dept_name; |
| **6** | employees | **Regex Search** | **Employees whose last name starts with 'A' or 'B'** SELECT * FROM employees WHERE last_name REGEXP '^[AB]'; |
| **7** | employees | **Regex Search** | **First names containing 'mar' case-insensitively** SELECT * FROM employees WHERE first_name REGEXP '(?i)mar'; |
| **8** | salaries | **Window Function (RANK)** | **Ranking of current salaries (Top 10)** SELECT emp_no, salary, RANK() OVER (ORDER BY salary DESC) as salary_rank FROM salaries WHERE to_date = '9999-01-01' LIMIT 10; |
| **9** | salaries, dept_emp | **Window Function (PARTITION)** | **Ranking of salaries by department** SELECT de.dept_no, s.emp_no, s.salary, RANK() OVER (PARTITION BY de.dept_no ORDER BY s.salary DESC) as dept_rank FROM salaries s JOIN dept_emp de ON s.emp_no = de.emp_no WHERE s.to_date = '9999-01-01' AND de.to_date = '9999-01-01'; |
| **10** | titles | **Aggregate (GROUP_CONCAT)** | **History of titles per employee (concatenated)** SELECT emp_no, GROUP_CONCAT(title ORDER BY from_date SEPARATOR ', ') as title_history FROM titles GROUP BY emp_no LIMIT 100; |
| **11** | employees | **Date Function** | **Employees hired more than 20 years ago** SELECT * FROM employees WHERE hire_date <= DATE_SUB(CURDATE(), INTERVAL 20 YEAR); |
| **12** | salaries | **Analytic (LAG)** | **Salary evolution (Comparison with previous)** SELECT emp_no, from_date, salary, LAG(salary, 1) OVER (PARTITION BY emp_no ORDER BY from_date) as prev_salary, (salary - LAG(salary, 1) OVER (PARTITION BY emp_no ORDER BY from_date)) as difference FROM salaries LIMIT 100; |
| **13** | salaries | **Analytic (LEAD)** | **Anticipation of the next salary change** SELECT emp_no, from_date, salary, LEAD(salary, 1) OVER (PARTITION BY emp_no ORDER BY from_date) as next_salary FROM salaries LIMIT 100; |
| **14** | dept_manager, employees | **Join + Subquery** | **Current managers who are women** SELECT e.first_name, e.last_name FROM employees e JOIN dept_manager dm ON e.emp_no = dm.emp_no WHERE dm.to_date = '9999-01-01' AND e.gender = 'F'; |
| **15** | salaries | **CTE (Common Table Expression)** | **Current average salary (calculated via CTE)** WITH CurrentSalaries AS (SELECT salary FROM salaries WHERE to_date = '9999-01-01') SELECT AVG(salary) FROM CurrentSalaries; |
| **16** | departments, dept_emp, salaries | **Complex CTE** | **Departments paying better than the overall average** WITH DeptAvg AS (SELECT de.dept_no, AVG(s.salary) as avg_sal FROM dept_emp de JOIN salaries s ON de.emp_no = s.emp_no WHERE s.to_date = '9999-01-01' GROUP BY de.dept_no), GlobalAvg AS (SELECT AVG(salary) as glob_sal FROM salaries WHERE to_date = '9999-01-01') SELECT d.dept_name, da.avg_sal FROM DeptAvg da JOIN departments d ON da.dept_no = d.dept_no JOIN GlobalAvg ga WHERE da.avg_sal > ga.glob_sal; |
| **17** | employees | **JSON Generation** | **Create a JSON object for each employee** SELECT JSON_OBJECT('id', emp_no, 'name', CONCAT(first_name, ' ', last_name), 'gender', gender) as emp_json FROM employees LIMIT 10; |
| **18** | titles | **JSON Aggregation** | **List of an employee's titles in a JSON array** SELECT emp_no, JSON_ARRAYAGG(title) as titles_json FROM titles GROUP BY emp_no LIMIT 10; |
| **19** | employees, dept_emp | **EXISTS Filter** | **Employees who have never changed department** SELECT e.first_name, e.last_name FROM employees e WHERE EXISTS (SELECT 1 FROM dept_emp de WHERE de.emp_no = e.emp_no GROUP BY de.emp_no HAVING COUNT(*) = 1) LIMIT 100; |
| **20** | salaries | **Window Function (DENSE_RANK)** | **Dense ranking of salaries (without gaps)** SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) as rank_dense FROM salaries WHERE to_date = '9999-01-01' LIMIT 20; |
| **21** | employees | **Regex Search** | **Last names ending in 'son' or 'sen'** SELECT last_name FROM employees WHERE last_name REGEXP 's[eo]n$' LIMIT 50; |
| **22** | dept_emp | **Temporal Aggregate** | **Number of hires per year** SELECT YEAR(from_date) as hire_year, COUNT(*) FROM dept_emp GROUP BY hire_year ORDER BY hire_year; |
| **23** | salaries | **Window Function (Running Total)** | **Cumulative sum of salaries paid per employee (historical)** SELECT emp_no, from_date, salary, SUM(salary) OVER (PARTITION BY emp_no ORDER BY from_date) as running_total_paid FROM salaries LIMIT 100; |
| **24** | employees, titles | **Self Join (Simulation)** | **Employees with the same title at the same time (Complex Logic)** SELECT t1.emp_no as Emp1, t2.emp_no as Emp2, t1.title FROM titles t1 JOIN titles t2 ON t1.title = t2.title AND t1.emp_no < t2.emp_no WHERE t1.to_date = '9999-01-01' AND t2.to_date = '9999-01-01' LIMIT 50; |
| **25** | salaries | **Window Frame** | **Moving average of salary over 3 periods** SELECT emp_no, from_date, salary, AVG(salary) OVER (PARTITION BY emp_no ORDER BY from_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as moving_avg FROM salaries LIMIT 100; |
| **26** | dept_manager | **Aggregate** | **Average tenure of a manager (days)** SELECT AVG(DATEDIFF(IF(to_date='9999-01-01', CURDATE(), to_date), from_date)) as avg_days_as_manager FROM dept_manager; |
| **27** | employees | **Analytic (NTILE)** | **Distribution of employees into 4 quartiles by age** SELECT emp_no, birth_date, NTILE(4) OVER (ORDER BY birth_date) as age_quartile FROM employees LIMIT 100; |
| **28** | salaries | **Standard Deviation Search** | **Suspicious salaries (> 3 standard deviations from the mean)** WITH Stats AS (SELECT AVG(salary) as avg_sal, STDDEV(salary) as std_dev FROM salaries WHERE to_date = '9999-01-01') SELECT s.emp_no, s.salary FROM salaries s, Stats st WHERE s.to_date = '9999-01-01' AND s.salary > (st.avg_sal + 3 * st.std_dev); |
| **29** | employees | **Complex Regex** | **First names with 2 consecutive vowels** SELECT first_name FROM employees WHERE first_name REGEXP '[aeiou]{2}' LIMIT 50; |
| **30** | dept_emp, departments | **Pivot (Case When)** | **Pivot: Number of employees per department (Columns)** SELECT SUM(CASE WHEN dept_no = 'd001' THEN 1 ELSE 0 END) as Marketing, SUM(CASE WHEN dept_no = 'd002' THEN 1 ELSE 0 END) as Finance FROM dept_emp WHERE to_date = '9999-01-01'; |
| **31** | titles | **Recursive CTE (Simulation)** | **Generate a series of dates (to fill gaps)** WITH RECURSIVE DateSeries AS (SELECT '2000-01-01' as d UNION ALL SELECT DATE_ADD(d, INTERVAL 1 YEAR) FROM DateSeries WHERE d < '2010-01-01') SELECT * FROM DateSeries; |
| **32** | employees | **String Manipulation** | **Initials of employees** SELECT CONCAT(LEFT(first_name, 1), '.', LEFT(last_name, 1), '.') as initials FROM employees LIMIT 50; |
| **33** | salaries, employees | **Window (First Value)** | **Hiring salary vs Current salary** SELECT emp_no, salary, FIRST_VALUE(salary) OVER (PARTITION BY emp_no ORDER BY from_date) as starting_salary FROM salaries WHERE to_date = '9999-01-01' LIMIT 50; |
| **34** | dept_emp | **Aggregate with ROLLUP** | **Total employees per department with subtotals** SELECT dept_no, COUNT(*) FROM dept_emp WHERE to_date = '9999-01-01' GROUP BY dept_no WITH ROLLUP; |
| **35** | employees | **JSON Extraction** | **Extract info from a generated JSON (Simulation)** SELECT JSON_EXTRACT(JSON_OBJECT('name', first_name), '$.name') as name_extracted FROM employees LIMIT 10; |
| **36** | salaries | **Analytic (Percent Rank)** | **Percent rank of salary** SELECT emp_no, salary, PERCENT_RANK() OVER (ORDER BY salary) as percentile FROM salaries WHERE to_date = '9999-01-01' LIMIT 100; |
| **37** | employees, dept_emp | **Anti-Join (Left Join NULL)** | **Employees without an active department assignment (Theoretical)** SELECT e.emp_no FROM employees e LEFT JOIN dept_emp de ON e.emp_no = de.emp_no AND de.to_date = '9999-01-01' WHERE de.dept_no IS NULL; |
| **38** | salaries | **Aggregate (MIN/MAX)** | **Min/max salary range per employee** SELECT emp_no, MAX(salary) - MIN(salary) as salary_growth_range FROM salaries GROUP BY emp_no LIMIT 100; |
| **39** | dept_manager | **CTE + Window** | **Successive managers by department** WITH Managers AS (SELECT dept_no, emp_no, from_date, to_date FROM dept_manager) SELECT dept_no, emp_no, LAG(emp_no) OVER (PARTITION BY dept_no ORDER BY from_date) as prev_manager FROM Managers; |
| **40** | employees | **Regex Boundary** | **Names starting and ending with the same letter** SELECT first_name FROM employees WHERE first_name REGEXP '^(.).*\1$' LIMIT 20; |
| **41** | salaries | **Mathematics** | **Salary modulo 1000 (Distribution of remainders)** SELECT salary % 1000 as remainder, COUNT(*) FROM salaries WHERE to_date = '9999-01-01' GROUP BY remainder ORDER BY remainder; |
| **42** | titles, dept_emp | **Complex Join** | **Current title vs Current department** SELECT t.title, d.dept_name, COUNT(*) FROM titles t JOIN dept_emp de ON t.emp_no = de.emp_no JOIN departments d ON de.dept_no = d.dept_no WHERE t.to_date = '9999-01-01' AND de.to_date = '9999-01-01' GROUP BY t.title, d.dept_name; |
| **43** | employees | **Aggregate (Date)** | **Employees born on the weekend** SELECT * FROM employees WHERE DAYOFWEEK(birth_date) IN (1, 7) LIMIT 50; |
| **44** | salaries | **Analytic (CUME_DIST)** | **Cumulative distribution of salaries** SELECT salary, CUME_DIST() OVER (ORDER BY salary) as cum_dist FROM salaries WHERE to_date = '9999-01-01' LIMIT 100; |
| **45** | dept_emp | **Window Count** | **Number of department changes per employee** SELECT emp_no, COUNT(*) OVER (PARTITION BY emp_no) as dept_changes FROM dept_emp LIMIT 100; |
| **46** | employees | **JSON Formatting** | **Pretty Print of an employee (Formatting)** SELECT JSON_PRETTY(JSON_OBJECT('id', emp_no, 'dates', JSON_OBJECT('birth', birth_date, 'hire', hire_date))) FROM employees LIMIT 1; |
| **47** | salaries | **Update (Safe Update)** | **Theoretical 10% increase (Select)** SELECT emp_no, salary, salary * 1.10 as potential_salary FROM salaries WHERE to_date = '9999-01-01'; |
| **48** | employees, dept_emp | **Union** | **Unified list of Managers and Employees (with type)** SELECT emp_no, 'Manager' as type FROM dept_manager WHERE to_date = '9999-01-01' UNION SELECT emp_no, 'Employee' FROM dept_emp WHERE to_date = '9999-01-01' LIMIT 100; |
| **49** | titles | **Regex Alternation** | **Titles containing Engineer or Staff** SELECT DISTINCT title FROM titles WHERE title REGEXP 'Engineer|Staff'; |
| **50** | salaries | **CTE + Join** | **Employees with the maximum salary in their department** WITH MaxDepSal AS (SELECT de.dept_no, MAX(s.salary) as max_sal FROM dept_emp de JOIN salaries s ON de.emp_no = s.emp_no WHERE s.to_date = '9999-01-01' GROUP BY de.dept_no) SELECT de.emp_no, de.dept_no, s.salary FROM dept_emp de JOIN salaries s ON de.emp_no = s.emp_no JOIN MaxDepSal mds ON de.dept_no = mds.dept_no AND s.salary = mds.max_sal WHERE s.to_date = '9999-01-01'; |
| **51** | employees | **Random Sort** | **Random sample of 5 employees** SELECT * FROM employees ORDER BY RAND() LIMIT 5; |
| **52** | salaries | **Bitwise Operator** | **Even salaries only** SELECT emp_no, salary FROM salaries WHERE (salary & 1) = 0 LIMIT 20; |
| **53** | dept_emp | **Group By Having** | **Employees who have worked in more than 2 departments** SELECT emp_no, COUNT(DISTINCT dept_no) as nb_depts FROM dept_emp GROUP BY emp_no HAVING nb_depts > 2; |
| **54** | employees | **Full Text (Simulation)** | **Approximate search (Soundex)** SELECT * FROM employees WHERE SOUNDEX(last_name) = SOUNDEX('Schwarzenegger'); |
| **55** | salaries | **Analytic (Row Number)** | **Duplicate removal (Selection simulation)** WITH Duplicates AS (SELECT *, ROW_NUMBER() OVER(PARTITION BY emp_no, from_date ORDER BY to_date DESC) as rn FROM salaries) SELECT * FROM Duplicates WHERE rn > 1; |
| **56** | departments | **JSON Array** | **List of departments in a JSON array** SELECT JSON_ARRAYAGG(dept_name) FROM departments; |
| **57** | employees | **Age Calculation** | **Current age of employees** SELECT emp_no, TIMESTAMPDIFF(YEAR, birth_date, CURDATE()) as age FROM employees LIMIT 50; |
| **58** | salaries | **Histogram (CASE)** | **Salary categorization (Low, Med, High)** SELECT CASE WHEN salary < 50000 THEN 'Low' WHEN salary BETWEEN 50000 AND 100000 THEN 'Medium' ELSE 'High' END as category, COUNT(*) FROM salaries WHERE to_date = '9999-01-01' GROUP BY category; |
| **59** | titles | **Regex Character Class** | **Titles without numbers** SELECT DISTINCT title FROM titles WHERE title NOT REGEXP '[0-9]'; |
| **60** | all tables | **Meta Data** | **Size of tables in MB (Admin Query)** SELECT table_name, round(((data_length + index_length) / 1024 / 1024), 2) as size_mb FROM information_schema.tables WHERE table_schema = 'employees'; |

*Note: The queries are designed for MariaDB environments. Some features may not be available in older versions or other database management systems.*