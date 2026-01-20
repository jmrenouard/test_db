-- scripts/dir_transactions_sysbench.lua
-- This script executes SQL transactions from all .sql files in a specified directory.
-- Usage: sysbench scripts/dir_transactions_sysbench.lua --sql-dir=/path/to/sql/dir [options] run

-- Define custom command line options
sysbench.cmdline.options = {
    ["sql-dir"] = {"Directory containing transaction SQL files", ""}
}

local transactions = {}
local transaction_count = 0

-- Function to load SQL files from a directory
function load_transactions()
    local sql_dir = sysbench.opt.sql_dir
    
    if not sql_dir or sql_dir == "" then
        error("You must specify the SQL directory using --sql-dir")
    end

    -- Ensure directory ends with /
    if string.sub(sql_dir, -1) ~= "/" then
        sql_dir = sql_dir .. "/"
    end

    -- Use find to get all .sql files in the directory
    local p = io.popen("find " .. sql_dir .. " -maxdepth 1 -name '*.sql'")
    if not p then
        error("Could not access directory: " .. sql_dir)
    end

    for file_path in p:lines() do
        -- Skip setup.sql if present in the directory
        if not string.match(file_path, "setup.sql$") and not string.match(file_path, "teardown.sql$") then
            local f = io.open(file_path, "r")
            if f then
            local content = f:read("*all")
            f:close()

            local statements = {}
            -- Split content by ; and trim whitespace
            for stmt in string.gmatch(content, "([^;]+);") do
                -- Remove comments and leading/trailing whitespace
                local lines = {}
                for line in string.gmatch(stmt, "([^\n]+)") do
                    if not string.match(line, "^%s*%-%-") then
                        table.insert(lines, line)
                    end
                end
                local clean_stmt = table.concat(lines, " ")
                clean_stmt = string.gsub(clean_stmt, "^%s*(.-)%s*$", "%1")
                
                if clean_stmt ~= "" then
                    table.insert(statements, clean_stmt)
                end
            end

            if #statements > 0 then
                table.insert(transactions, statements)
            end
            end
        end
    end
    p:close()

    transaction_count = #transactions
    if transaction_count == 0 then
        error("No .sql files found in " .. sql_dir)
    end
    
    print(string.format("Loaded %d transactions from %s", transaction_count, sql_dir))
end

-- sysbench entry point for each thread
function thread_init()
    load_transactions()
    -- Initialize random seed for each thread
    math.randomseed(os.time() + sysbench.tid)
end

-- sysbench event loop
function event()
    -- Pick a random transaction
    local idx = math.random(transaction_count)
    local statements = transactions[idx]

    for _, stmt in ipairs(statements) do
        db_query(stmt)
    end
end
