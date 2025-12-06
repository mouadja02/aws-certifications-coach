#!/bin/bash

# Database restore script for AWS Certifications Coach
# Usage: ./scripts/restore_database.sh <backup_file>

set -e

# Configuration
CONTAINER_NAME="aws-coach-db"
DB_NAME="aws_certifications"
DB_USER="awscoach"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backup file is provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: No backup file specified${NC}"
    echo "Usage: $0 <backup_file.sql.gz>"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}Error: Backup file not found: ${BACKUP_FILE}${NC}"
    exit 1
fi

echo -e "${YELLOW}Starting database restore...${NC}"

# Check if container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo -e "${RED}Error: Database container is not running${NC}"
    exit 1
fi

# Extract if compressed
if [[ "$BACKUP_FILE" == *.gz ]]; then
    echo -e "${GREEN}Extracting compressed backup...${NC}"
    TEMP_FILE="${BACKUP_FILE%.gz}"
    gunzip -c "$BACKUP_FILE" > "$TEMP_FILE"
    SQL_FILE="$TEMP_FILE"
else
    SQL_FILE="$BACKUP_FILE"
fi

# Confirm restore
echo -e "${YELLOW}WARNING: This will overwrite the current database!${NC}"
read -p "Are you sure you want to continue? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo -e "${RED}Restore cancelled${NC}"
    [ -f "$TEMP_FILE" ] && rm "$TEMP_FILE"
    exit 1
fi

# Drop and recreate database
echo -e "${GREEN}Recreating database...${NC}"
docker exec -t "$CONTAINER_NAME" psql -U "$DB_USER" -c "DROP DATABASE IF EXISTS $DB_NAME;"
docker exec -t "$CONTAINER_NAME" psql -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;"

# Restore backup
echo -e "${GREEN}Restoring database from backup...${NC}"
docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" < "$SQL_FILE"

# Clean up temp file
[ -f "$TEMP_FILE" ] && rm "$TEMP_FILE"

echo -e "${GREEN}Database restored successfully!${NC}"

