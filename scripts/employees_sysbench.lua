-- Basic sysbench lua script for employees database

function event()
   local emp_no = math.random(1, 400000)
   -- Point select
   db_query("SELECT * FROM employees WHERE emp_no = " .. emp_no)
   
   -- Range select
   db_query("SELECT count(*) FROM salaries WHERE emp_no = " .. emp_no)
end
