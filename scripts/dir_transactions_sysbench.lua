-- scripts/dir_transactions_sysbench.lua
-- ============================================================================
-- Sysbench Transaction Simulation Script
-- ============================================================================
-- Purpose:
--   Executes SQL transactions from all .sql files found in a specified directory.
--   Each .sql file represents a single transaction (atomic unit of work).
--   Multiple statements within a file must be separated by semicolons.
--
-- Usage:
--   sysbench scripts/dir_transactions_sysbench.lua \
--     --sql-dir=/path/to/sql/dir \
--     --db-driver=mysql --mysql-host=... [options] \
--     run
--
-- Parameters:
--   --sql-dir: Path to directory containing .sql transaction files.
--
-- Logic:
--   1. thread_init(): Calls load_transactions() to read SQL files into memory.
--   2. event(): Randomly picks one loaded transaction and executes its statements.
-- ============================================================================

-- Define custom command line options for sysbench
sysbench.cmdline.options = {
    ["sql-dir"] = {"Directory containing transaction SQL files", ""}
}

-- Global state to store loaded transactions across thread lifecycles
local transactions = {}
local transaction_count = 0

--- Loads SQL files from the directory specified by --sql-dir.
-- This function scans the directory, reads .sql files (excluding setup/teardown),
-- and parses them into a structure ready for execution.
function load_transactions()
    local sql_dir = sysbench.opt.sql_dir
    
    -- Validate mandatory parameter
    if not sql_dir or sql_dir == "" then
        error("You must specify the SQL directory using --sql-dir")
    end

    -- Normalize directory path (ensure trailing slash)
    if string.sub(sql_dir, -1) ~= "/" then
        sql_dir = sql_dir .. "/"
    end

    -- Use shell 'find' to retrieve all .sql files in the immediate directory.
    -- This allows the script to remain agnostic of file naming conventions.
    local p = io.popen("find " .. sql_dir .. " -maxdepth 1 -name '*.sql'")
    if not p then
        error("Could not access directory: " .. sql_dir)
    end

    -- Iterate through each found file path
    for file_path in p:lines() do
        -- EXCLUSION LOGIC:
        -- setup.sql and teardown.sql are reserved for environment prep/cleanup
        -- and should not be part of the performance simulation transactions.
        if not string.match(file_path, "setup.sql$") and not string.match(file_path, "teardown.sql$") then
            local f = io.open(file_path, "r")
            if f then
                local content = f:read("*all")
                f:close()

                local statements = {}
                -- PARSING LOGIC:
                -- Split the file content by semicolons (;) to handle multi-statement transactions.
                for stmt in string.gmatch(content, "([^;]+);") do
                    -- CLEANING LOGIC:
                    -- Remove SQL comments (-- comment) and trim whitespace for cleaner DB execution.
                    local lines = {}
                    for line in string.gmatch(stmt, "([^\n]+)") do
                        -- Ignore lines starting with --
                        if not string.match(line, "^%s*%-%-") then
                            table.insert(lines, line)
                        end
                    end
                    
                    -- Rebuild the statement into a single line string
                    local clean_stmt = table.concat(lines, " ")
                    clean_stmt = string.gsub(clean_stmt, "^%s*(.-)%s*$", "%1")
                    
                    -- Only add non-empty statements to the transaction block
                    if clean_stmt ~= "" then
                        table.insert(statements, clean_stmt)
                    end
                end

                -- A file is considered a valid transaction if it contains at least one SQL statement
                if #statements > 0 then
                    table.insert(transactions, statements)
                end
            end
        end
    end
    p:close()

    -- Final validation: ensure at least one transaction was loaded
    transaction_count = #transactions
    if transaction_count == 0 then
        error("No .sql files found in " .. sql_dir)
    end
    
    -- Print summary to stdout (visible in sysbench logs)
    print(string.format("Loaded %d transactions from %s", transaction_count, sql_dir))
end

--- sysbench entry point: initialization for each worker thread.
function thread_init()
    -- Each thread loads the directory contents into its own local memory space
    load_transactions()
    
    -- Initialize random seed using time and Thread ID to ensure different
    -- threads pick different transactions even if started simultaneously.
    math.randomseed(os.time() + sysbench.tid)
end

--- sysbench entry point: logic executed for each 'request' (iteration).
function event()
    -- 1. Randomly pick a transaction from the loaded list
    local idx = math.random(transaction_count)
    local statements = transactions[idx]

    -- 2. Execute all SQL statements in this transaction sequentially
    -- Note: Sysbench handles transaction wrap (BEGIN/COMMIT) automatically
    -- if configured, or they can be explicitly included in the .sql files.
    for _, stmt in ipairs(statements) do
        db_query(stmt)
    end
end
