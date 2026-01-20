-- scripts/employees_sysbench.lua
-- ============================================================================
-- Sequential Performance Tester for Employees Database
-- ============================================================================
-- Purpose:
--   Reads a set of SQL queries from a fixed temporary file and executes 
--   them sequentially in a loop for each thread.
--   Used for standard performance benchmarks against the 'employees' schema.
--
-- Expected File:
--   /tmp/req_employees.sql (or /tmp/rerq_employees.sql)
--
-- Logic:
--   1. thread_init(): Loads all queries from the SQL file into memory.
--   2. event(): Executes queries one by one using a circular index.
-- ============================================================================

local queries = {}
local query_count = 0

--- Loads queries from the predefined temporary SQL files.
-- Parsea the content by semicolon and removes SQL comments.
function load_queries()
    -- Primary location for generated queries
    local sql_file = "/tmp/req_employees.sql"
    local f = io.open(sql_file, "r")
    if not f then
        -- Fallback location
        sql_file = "/tmp/rerq_employees.sql"
        f = io.open(sql_file, "r")
    end

    if not f then
        error("Could not find SQL query file at /tmp/req_employees.sql or /tmp/rerq_employees.sql")
    end

    local content = f:read("*all")
    f:close()

    -- SQL PARSING: 
    -- Split by semicolon (;) to isolate individual queries.
    for query in string.gmatch(content, "([^;]+);") do
        -- CLEANING: Remove single-line comments starting with --
        local lines = {}
        for line in string.gmatch(query, "([^\n]+)") do
            if not string.match(line, "^%s*%-%-") then
                table.insert(lines, line)
            end
        end
        local clean_query = table.concat(lines, " ")
        -- Trim trailing/leading whitespace
        clean_query = string.gsub(clean_query, "^%s*(.-)%s*$", "%1")
        
        if clean_query ~= "" then
            table.insert(queries, clean_query)
        end
    end

    query_count = #queries
    if query_count == 0 then
        error("No queries found in " .. sql_file)
    end
end

--- sysbench entry point: initialization for each worker thread.
function thread_init()
    load_queries()
    -- Initialize the index for sequential execution
    query_index = 0
end

--- sysbench entry point: logic executed for each 'request'.
function event()
    -- SEQUENTIAL LOGIC: 
    -- Move to the next query in the list, wrapping around if the end is reached.
    query_index = (query_index % query_count) + 1
    db_query(queries[query_index])
end
