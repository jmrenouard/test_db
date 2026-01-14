-- scripts/employees_sysbench.lua
-- This script reads queries from a SQL file and executes them sequentially.

local queries = {}
local query_count = 0

-- Load queries from the SQL file
function load_queries()
    local sql_file = "/tmp/req_employees.sql"
    local f = io.open(sql_file, "r")
    if not f then
        -- Fallback to alternative name if provided
        sql_file = "/tmp/rerq_employees.sql"
        f = io.open(sql_file, "r")
    end

    if not f then
        error("Could not find SQL query file at /tmp/req_employees.sql or /tmp/rerq_employees.sql")
    end

    local content = f:read("*all")
    f:close()

    -- Parse queries delimited by ;
    -- We use a simple pattern to split by semicolon
    for query in string.gmatch(content, "([^;]+);") do
        -- Remove comments (lines starting with --)
        local lines = {}
        for line in string.gmatch(query, "([^\n]+)") do
            if not string.match(line, "^%s*%-%-") then
                table.insert(lines, line)
            end
        end
        local clean_query = table.concat(lines, " ")
        -- Trim whitespace
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

-- sysbench entry point
function thread_init()
    load_queries()
    query_index = 0
end

-- sysbench event loop
function event()
    query_index = (query_index % query_count) + 1
    db_query(queries[query_index])
end
